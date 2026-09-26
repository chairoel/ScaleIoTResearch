"""Satu sesi: impedansi dari siaran, berat dari GATT, laporan dari rumus."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from aplikasi.__main__ import main
from aplikasi.sesi_ukur import DataTubuh, SesiUkur, hitung_laporan
from aplikasi.simpan import Penyimpan
from rumus.cs_bias_v235 import parse_default_z
from rumus.gatt_okok import GattKonfirmasi


def _prop(lock=1):
    return int(f"0000000{lock}", 2)


def _v17(command: int, weight: tuple[int, int], prop: int) -> bytes:
    return bytes((0xCA, 17, 0, command, 0, weight[0], weight[1], 0, 0, 0, 0, prop))


def _v16(prop: int, weight: tuple[int, int], axunge: int) -> bytes:
    return bytes((0xCA, 16, 0, 0, prop, weight[0], weight[1], axunge >> 8, axunge & 0xFF))


def _siaran_c0(impedance: tuple[int, int] = (0x13, 0x88)) -> bytes:
    return bytes((0xC0, 7, 0x02, 0xC1, impedance[0], impedance[1], 0x00, 0x01, _prop()))


class SesiUkurTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tubuh = DataTubuh(170, 30, 1)

    def test_berat_gatt_dan_impedansi_siaran(self):
        sesi = SesiUkur(self.tubuh)
        sesi.terima_siaran(_siaran_c0(), "AA:BB:CC:DD:EE:FF")
        parsed = sesi.terima_gatt(_v17(1, (0x02, 0x8F), _prop()))
        laporan = parse_default_z(1, 30, 170, 65.5, 500.0)
        self.assertEqual(parsed.weight_kg, 65.5)
        self.assertEqual(sesi.keadaan(), "selesai")
        self.assertIsNotNone(sesi.hasil)
        assert sesi.hasil is not None
        self.assertEqual(sesi.hasil.berat_kg, 65.5)
        self.assertEqual(sesi.hasil.tampilan_berat, "65.5")
        self.assertEqual(sesi.hasil.impedansi_ohm, (500.0,))
        self.assertEqual(sesi.hasil.mac, "AA:BB:CC:DD:EE:FF")
        self.assertEqual(sesi.hasil.product_id, 1)
        self.assertEqual(sesi.hasil.rumus, "v235")
        self.assertEqual(sesi.hasil.laporan, laporan.data)
        self.assertEqual(sesi.siaran.weight_kg, 70.5)

    def test_urutan_gatt_dahulu(self):
        sesi = SesiUkur(self.tubuh)
        menunggu = sesi.terima_gatt(_v17(0, (0x02, 0x8F), _prop()))
        self.assertEqual(menunggu.lock_flag, 0)
        self.assertIsNone(sesi.berat_kg)
        self.assertEqual(sesi.keadaan(), "menunggu impedansi")
        sesi.terima_gatt(_v17(1, (0x02, 0x8F), _prop()))
        self.assertEqual(sesi.keadaan(), "menunggu impedansi")
        sesi.terima_siaran(_siaran_c0(), "AA")
        self.assertEqual(sesi.hasil.berat_kg, 65.5)
        self.assertEqual(sesi.hasil.laporan, parse_default_z(1, 30, 170, 65.5, 500.0).data)

    def test_angka_paket_tidak_mengubah_lemak(self):
        pertama = SesiUkur(self.tubuh)
        kedua = SesiUkur(self.tubuh)
        for sesi, axunge in ((pertama, 225), (kedua, 400)):
            sesi.terima_siaran(_siaran_c0())
            sesi.terima_gatt(_v16(_prop(), (0x02, 0x8F), axunge))
        self.assertEqual(pertama.hasil.laporan, kedua.hasil.laporan)
        self.assertEqual(pertama.hasil.laporan.bfp, parse_default_z(1, 30, 170, 65.5, 500.0).data.bfp)

    def test_siaran_tanpa_impedansi_menunggu(self):
        sesi = SesiUkur(self.tubuh)
        frame = bytes((0xCA, 17, 0, 0x21, 2, 0x02, 0xC1, 0, 0, 1, 0))
        sesi.terima_siaran(frame)
        sesi.terima_gatt(_v17(1, (0x02, 0x8F), _prop()))
        self.assertIsNone(sesi.hasil)
        self.assertEqual(sesi.keadaan(), "menunggu impedansi")

    def test_siaran_belum_kunci_tidak_menimpa_impedansi(self):
        sesi = SesiUkur(self.tubuh)
        sesi.terima_siaran(_siaran_c0())
        terbuka = bytes((0xCA, 0x20, 0, 0, 0, 0, 42, 0, 0x20, 9, 0x02, 0xC1, 0x13, 0x88))
        sesi.terima_siaran(terbuka)
        self.assertEqual(sesi.impedansi_ohm, 500.0)
        sesi.terima_gatt(_v17(1, (0x02, 0x8F), _prop()))
        self.assertEqual(sesi.hasil.impedansi_ohm, (500.0,))

    def test_perintah_20_dan_riwayat_bukan_berat_sesi(self):
        sesi = SesiUkur(self.tubuh)
        sesi.terima_siaran(_siaran_c0())
        prop = _prop()
        peran = bytes((0xCA, 17, 13, 20, 0x11, 0x02, 0xC1, prop, 0, 0, 0, 1, 0, 0, 0, 2))
        parsed = sesi.terima_gatt(peran)
        self.assertIsInstance(parsed, GattKonfirmasi)
        self.assertEqual(sesi.keadaan(), "menunggu berat")
        when = (1_700_000_000).to_bytes(4, "big")
        body = when + bytes((prop, 0, 0, 0, 0, 1, 0x03, 0x20, 0, 225, 2, 0x26, 0, 100, 5, 220, 0, 80, 25))
        riwayat = bytes((0xCA, 17, len(body) + 2, 19, 0x11)) + body
        self.assertTrue(sesi.terima_gatt(riwayat).history)
        self.assertIsNone(sesi.hasil)
        sesi.terima_gatt(_v17(1, (0x02, 0x8F), prop))
        self.assertEqual(sesi.hasil.berat_kg, 65.5)

    def test_rumus_gagal_lalu_impedansi_berikutnya(self):
        sesi = SesiUkur(self.tubuh)
        sesi.terima_siaran(_siaran_c0((0x03, 0xE8)))
        sesi.terima_gatt(_v17(1, (0x02, 0x8F), _prop()))
        self.assertIsNone(sesi.hasil)
        self.assertEqual(sesi.kode, -6)
        self.assertEqual(sesi.keadaan(), "rumus -6")
        sesi.terima_siaran(_siaran_c0())
        self.assertEqual(sesi.hasil.impedansi_ohm, (500.0,))
        self.assertEqual(sesi.kode, 0)

    def test_hasil_pertama_tetap(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        simpan = Penyimpan(Path(folder.name) / "scaleiot.sqlite")
        self.addCleanup(simpan.tutup)
        sesi = SesiUkur(self.tubuh, simpan)
        sesi.terima_siaran(_siaran_c0())
        sesi.terima_gatt(_v17(1, (0x02, 0x8F), _prop()))
        sesi.terima_gatt(_v17(1, (0x03, 0x20), _prop()))
        self.assertEqual(sesi.hasil.berat_kg, 65.5)
        self.assertEqual(len(simpan.daftar()), 1)
        self.assertEqual(simpan.daftar()[0]["laporan"]["bfp"], sesi.hasil.laporan.bfp)

    def test_sepuluh_impedansi(self):
        ohm = [value / 10 for value in (5000, 4800, 300, 4500, 4600, 5100, 4900, 280, 4400, 4700)]
        rumus, kode, data = hitung_laporan(self.tubuh, 70.0, ohm)
        from rumus.cs_bias_vA019 import parse_multi_frequency

        langsung = parse_multi_frequency(1, 30, 170, 70.0, ohm)
        self.assertEqual(rumus, "vA019")
        self.assertEqual(kode, 0)
        self.assertEqual(data, langsung.data)


class SimpanDanPerintahTest(unittest.TestCase):
    def test_perintah_menyimpan_profil_dan_hasil(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        berkas = str(Path(folder.name) / "scaleiot.sqlite")
        keluar = io.StringIO()
        with contextlib.redirect_stdout(keluar):
            self.assertEqual(
                main(["--berkas", berkas, "tubuh", "--tinggi", "170", "--umur", "30", "--kelamin", "1"]),
                0,
            )
            self.assertEqual(main(["--berkas", berkas, "profil"]), 0)
            siaran = "C00702C11388000121"
            gatt = "CA11000100028F0000000021"
            self.assertEqual(
                main(["--berkas", berkas, "ukur", "--mac", "AA:BB", "--siaran", siaran, "--gatt", gatt]),
                0,
            )
            self.assertEqual(main(["--berkas", berkas, "daftar"]), 0)
        self.assertIn("Lemak 17.882137298583984", keluar.getvalue())
        simpan = Penyimpan(berkas)
        self.addCleanup(simpan.tutup)
        baris = simpan.daftar()
        self.assertEqual(len(baris), 1)
        self.assertEqual(baris[0]["berat_kg"], 65.5)
        self.assertEqual(baris[0]["mac"], "AA:BB")
        self.assertEqual(baris[0]["rumus"], "v235")
        self.assertEqual(baris[0]["laporan"]["bfp"], parse_default_z(1, 30, 170, 65.5, 500.0).data.bfp)


if __name__ == "__main__":
    unittest.main()
