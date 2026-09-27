"""Pendengar BLE mengisi sesi dari muatan iklan dan notify."""

import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from aplikasi.__main__ import main
from aplikasi.sesi_ble import PendengarSesi, boleh_sambung, menerima_sambungan, putuskan_berat
from aplikasi.sesi_ukur import DataTubuh, SesiUkur
from rumus.cs_bias_v235 import parse_default_z
from rumus.iklan_okok import muatan_okok


def _prop(lock=1):
    return int(f"0000000{lock}", 2)


def _siaran() -> bytes:
    return bytes((0xC0, 7, 0x02, 0xC1, 0x13, 0x88, 0x00, 0x01, _prop()))


def _gatt() -> bytes:
    return bytes((0xCA, 17, 0, 1, 0, 0x02, 0x8F, 0, 0, 0, 0, _prop()))


class PendengarSesiTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tubuh = DataTubuh(170, 30, 1)

    def test_iklan_lalu_gatt_menutup_sesi(self):
        sesi = SesiUkur(self.tubuh)
        dengar = PendengarSesi(sesi)
        rekaman = bytes((0x02, 0x01, 0x06, len(_siaran()) + 1, 0xFF)) + _siaran()
        baris = dengar.iklan("AA:BB:CC:DD:EE:FF", muatan_okok(rekaman))
        self.assertIn("500", baris)
        self.assertTrue(dengar.siap)
        self.assertEqual(dengar.gatt(_gatt()), "GATT kunci 1 65.5 kg")
        self.assertEqual(sesi.hasil.berat_kg, 65.5)
        self.assertEqual(sesi.hasil.impedansi_ohm, (500.0,))
        self.assertEqual(sesi.hasil.laporan, parse_default_z(1, 30, 170, 65.5, 500.0).data)
        self.assertEqual(dengar.hex_siaran, _siaran().hex())
        self.assertEqual(dengar.hex_gatt, _gatt().hex())

    def test_perangkat_lain_diabaikan(self):
        sesi = SesiUkur(self.tubuh)
        dengar = PendengarSesi(sesi, "AA")
        self.assertIsNone(dengar.iklan("BB", _siaran()))
        self.assertFalse(dengar.siap)
        self.assertIsNotNone(dengar.iklan("aa", _siaran()))
        self.assertEqual(dengar.alamat, "AA")

    def test_sambungan_begitu_siaran_terbaca(self):
        sesi = SesiUkur(self.tubuh)
        dengar = PendengarSesi(sesi)
        terbuka = bytes((0xC0, 7, 0x02, 0xC1, 0x13, 0x88, 0x00, 0x01, 0))
        dengar.iklan("AA", terbuka)
        self.assertTrue(boleh_sambung(dengar, "AA"))
        self.assertFalse(boleh_sambung(dengar, "BB"))
        self.assertEqual(dengar.hex_siaran, "")

    def test_siaran_tak_tersambung_menutup_berat(self):
        sesi = SesiUkur(self.tubuh)
        dengar = PendengarSesi(sesi)
        dengar.iklan("AA", _siaran())
        self.assertIsNone(putuskan_berat(dengar, True, False))
        self.assertIsNone(sesi.hasil)
        self.assertEqual(putuskan_berat(dengar, False, False), "berat dari siaran terkunci")
        self.assertEqual(sesi.hasil.berat_kg, sesi.siaran.weight_kg)
        self.assertIsNone(putuskan_berat(dengar, False, False))

    def test_tanda_sambungan_iklan(self):
        class _Iklan:
            def __init__(self, isi):
                self.platform_data = (None, isi, -40)

        self.assertTrue(menerima_sambungan(_Iklan({"kCBAdvDataIsConnectable": 1})))
        self.assertFalse(menerima_sambungan(_Iklan({"kCBAdvDataIsConnectable": 0})))
        self.assertIsNone(menerima_sambungan(_Iklan({})))

    def test_siaran_berulang_diam(self):
        sesi = SesiUkur(self.tubuh)
        dengar = PendengarSesi(sesi)
        self.assertIsNotNone(dengar.iklan("AA", _siaran()))
        self.assertIsNone(dengar.iklan("AA", _siaran()))

    def test_perintah_sesi_tanpa_profil(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        berkas = str(Path(folder.name) / "scaleiot.sqlite")
        keluar = io.StringIO()
        with contextlib.redirect_stderr(keluar):
            kode = main(["--berkas", berkas, "sesi"])
        self.assertEqual(kode, 2)
        self.assertIn("Data tubuh belum ada.", keluar.getvalue())


if __name__ == "__main__":
    unittest.main()
