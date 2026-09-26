"""GATT OKOK versi 16, perintah 0 dan 1, serta rakitan perintah 18 dan 19."""

import unittest
from datetime import datetime, timezone

from rumus.gatt_okok import FrameFormatError, GattBelumDidukung, GattMenunggu, GattParser, parse_gatt


def _prop(lock=1, digit="10", unit="kg"):
    unit_bits = {"kg": "00", "jin": "01", "lb": "10", "st": "11"}[unit]
    digit_bits = {"int": "01", "10": "00", "100": "10"}[digit]
    return int(f"000{unit_bits}{digit_bits}{lock}", 2)


def _u16(value: int) -> tuple[int, int]:
    return (value >> 8) & 0xFF, value & 0xFF


def _v16(prop: int, weight: tuple[int, int] = (0x02, 0xC1), **fields: int) -> bytes:
    raw = {
        "axunge": 225,
        "water": 550,
        "muscle": 400,
        "bmr": 1500,
        "visceral": 80,
        "bone": 25,
    }
    raw.update(fields)
    return bytes(
        (
            0xCA,
            16,
            0,
            0,
            prop,
            weight[0],
            weight[1],
            *_u16(raw["axunge"]),
            *_u16(raw["water"]),
            *_u16(raw["muscle"]),
            *_u16(raw["bmr"]),
            *_u16(raw["visceral"]),
            raw["bone"] & 0xFF,
        )
    )


def _v17(command: int, prop: int, weight: tuple[int, int] = (0x02, 0xC1)) -> bytes:
    return bytes((0xCA, 17, 0, command, 0, weight[0], weight[1], 0, 0, 0, 0, prop))


class GattV16Test(unittest.TestCase):
    def test_terkunci_menyimpan_angka_paket(self):
        parsed = parse_gatt(_v16(_prop()))
        self.assertEqual(parsed.version, 16)
        self.assertIsNone(parsed.command)
        self.assertEqual(parsed.lock_flag, 1)
        self.assertEqual(parsed.property, _prop())
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.scale_weight, "70.5")
        self.assertFalse(parsed.history)
        self.assertEqual(parsed.axunge, 22.5)
        self.assertEqual(parsed.water, 55.0)
        self.assertEqual(parsed.muscle, 40.0)
        self.assertEqual(parsed.bmr, 1500.0)
        self.assertEqual(parsed.visceral_fat, 8.0)
        self.assertEqual(parsed.ori_visceral_fat, 80.0)
        self.assertEqual(parsed.bone, 2.5)
        self.assertEqual(parsed.role_id, 0)
        self.assertIsNone(parsed.weighing_date)

    def test_otot_tidak_dihitung_ulang_dari_berat(self):
        parsed = parse_gatt(_v16(_prop(), muscle=400))
        self.assertEqual(parsed.muscle, 40.0)
        self.assertNotEqual(parsed.muscle, (40.0 / parsed.weight_kg) * 100.0)

    def test_belum_kunci_hanya_berat(self):
        parsed = parse_gatt(_v16(_prop(lock=0)))
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.lock_flag, 0)
        self.assertEqual(parsed.axunge, 0.0)
        self.assertEqual(parsed.water, 0.0)
        self.assertEqual(parsed.muscle, 0.0)
        self.assertEqual(parsed.bmr, 0.0)
        self.assertEqual(parsed.visceral_fat, 0.0)
        self.assertEqual(parsed.ori_visceral_fat, 0.0)
        self.assertEqual(parsed.bone, 0.0)

    def test_terkunci_tanpa_byte_komposisi(self):
        frame = bytes((0xCA, 16, 0, 0, _prop(), 0x02, 0xC1))
        parsed = parse_gatt(frame)
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.axunge, 0.0)
        self.assertEqual(parsed.ori_visceral_fat, 0.0)
        self.assertEqual(parsed.bone, 0.0)

    def test_batas_penyempitan(self):
        cases = (
            ("axunge", 49, "axunge", 0.0),
            ("axunge", 50, "axunge", 5.0),
            ("axunge", 450, "axunge", 45.0),
            ("axunge", 451, "axunge", 0.0),
            ("axunge", 65535, "axunge", 0.0),
            ("water", 199, "water", 0.0),
            ("water", 200, "water", 20.0),
            ("water", 850, "water", 85.0),
            ("water", 851, "water", 0.0),
            ("water", 1000, "water", 0.0),
            ("muscle", 999, "muscle", 99.9),
            ("muscle", 1000, "muscle", 0.0),
            ("bmr", 4999, "bmr", 4999.0),
            ("bmr", 5000, "bmr", 500.0),
            ("bmr", 65535, "bmr", 0.0),
            ("visceral", 590, "visceral_fat", 59.0),
            ("visceral", 591, "visceral_fat", 0.0),
            ("visceral", 25600, "visceral_fat", 0.0),
            ("bone", 9, "bone", 0.0),
            ("bone", 10, "bone", 1.0),
            ("bone", 40, "bone", 4.0),
            ("bone", 41, "bone", 4.0),
            ("bone", 255, "bone", 4.0),
        )
        for field, raw, attr, expected in cases:
            with self.subTest(field=field, raw=raw):
                parsed = parse_gatt(_v16(_prop(), **{field: raw}))
                self.assertEqual(getattr(parsed, attr), expected)

    def test_lemak_visceral_mentah_tetap(self):
        parsed = parse_gatt(_v16(_prop(), visceral=25600))
        self.assertEqual(parsed.visceral_fat, 0.0)
        self.assertEqual(parsed.ori_visceral_fat, 25600.0)


class GattV17Test(unittest.TestCase):
    def test_perintah_1_berat_tanpa_komposisi(self):
        parsed = parse_gatt(_v17(1, _prop(lock=0)))
        self.assertEqual(parsed.version, 17)
        self.assertEqual(parsed.command, 1)
        self.assertEqual(parsed.lock_flag, 1)
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.scale_weight, "70.5")
        self.assertFalse(parsed.history)
        self.assertEqual(parsed.axunge, 0.0)
        self.assertEqual(parsed.ori_visceral_fat, 0.0)

    def test_perintah_0_tetap_membaca_berat(self):
        parsed = parse_gatt(_v17(0, _prop(lock=1, unit="jin"), (0x00, 0x8C)))
        self.assertEqual(parsed.command, 0)
        self.assertEqual(parsed.lock_flag, 0)
        self.assertEqual(parsed.weight_kg, 7.0)
        self.assertEqual(parsed.scale_weight, "14.0")
        self.assertEqual(parsed.property, _prop(lock=1, unit="jin"))

    def test_properti_di_offset_11(self):
        parsed = parse_gatt(_v17(1, _prop(unit="jin"), (0x00, 0x8C)))
        self.assertEqual(parsed.weight_kg, 7.0)
        self.assertEqual(parsed.scale_weight, "14.0")


class GattDitolakTest(unittest.TestCase):
    def test_format(self):
        with self.assertRaises(FrameFormatError):
            parse_gatt(b"")
        with self.assertRaises(FrameFormatError):
            parse_gatt(bytes((0xC0, 16, 0, 0, 1, 2, 3)))
        with self.assertRaises(FrameFormatError):
            parse_gatt(bytes((0xCA, 16, 0, 0, 1, 2)))
        with self.assertRaises(FrameFormatError):
            parse_gatt(bytes((0xCA, 17, 0, 1, 0, 2, 0xC1, 0, 0, 0, 0)))

    def test_di_luar_cakupan(self):
        with self.assertRaises(GattBelumDidukung):
            parse_gatt(bytes((0xCA, 32, 0)))
        with self.assertRaises(GattBelumDidukung):
            parse_gatt(_v17(20, _prop()))

    def test_muatan_perintah_18_tidak_valid(self):
        with self.assertRaises(FrameFormatError):
            parse_gatt(_v17(18, _prop()))
        with self.assertRaises(FrameFormatError):
            parse_gatt(_v17(19, _prop()))


def _body(
    prop: int,
    weight: tuple[int, int] = (0x03, 0x20),
    role: int = 0x01020304,
    when: int = 1_700_000_000,
    muscle: int = 100,
    axunge: int = 225,
    water: int = 550,
    bmr: int = 1500,
    visceral: int = 80,
    bone: int = 25,
) -> bytes:
    return (
        when.to_bytes(4, "big")
        + bytes((prop, 0))
        + role.to_bytes(4, "big")
        + bytes(weight)
        + axunge.to_bytes(2, "big")
        + water.to_bytes(2, "big")
        + muscle.to_bytes(2, "big")
        + bmr.to_bytes(2, "big")
        + visceral.to_bytes(2, "big")
        + bytes((bone & 0xFF,))
    )


def _packets(command: int, body: bytes, sizes: tuple[int, ...]) -> list[bytes]:
    frames = []
    offset = 0
    total = len(sizes)
    for number, size in enumerate(sizes, start=1):
        chunk = body[offset : offset + size]
        offset += size
        index = ((number & 0x0F) << 4) | (total & 0x0F)
        frames.append(bytes((0xCA, 17, size + 2, command, index)) + chunk)
    return frames


class GattRakitanTest(unittest.TestCase):
    def test_perintah_18_satu_paket(self):
        body = _body(_prop(lock=0), muscle=100)
        parsed = parse_gatt(_packets(18, body, (len(body),))[0])
        self.assertEqual(parsed.command, 18)
        self.assertEqual(parsed.lock_flag, 1)
        self.assertFalse(parsed.history)
        self.assertIsNone(parsed.weighing_date)
        self.assertEqual(parsed.role_id, 0x01020304)
        self.assertEqual(parsed.weight_kg, 80.0)
        self.assertEqual(parsed.scale_weight, "80.0")
        self.assertEqual(parsed.axunge, 22.5)
        self.assertEqual(parsed.water, 55.0)
        self.assertEqual(parsed.muscle, 12.5)
        self.assertEqual(parsed.bmr, 1500.0)
        self.assertEqual(parsed.visceral_fat, 8.0)
        self.assertEqual(parsed.ori_visceral_fat, 80.0)
        self.assertEqual(parsed.bone, 2.5)

    def test_otot_tetap_bila_persen_tidak_di_bawah_50(self):
        parsed = parse_gatt(_packets(18, _body(_prop(lock=0), muscle=400), (23,))[0])
        self.assertEqual(parsed.muscle, 40.0)

    def test_otot_dibatasi_50(self):
        parsed = parse_gatt(_packets(18, _body(_prop(lock=0), muscle=600), (23,))[0])
        self.assertEqual(parsed.muscle, 50.0)

    def test_otot_terpotong_ke_persepuluhan(self):
        parsed = parse_gatt(_packets(18, _body(_prop(lock=0), (0x02, 0xC1), muscle=200), (23,))[0])
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.muscle, 28.3)

    def test_perintah_19_dua_paket(self):
        body = _body(_prop(lock=0), muscle=100, visceral=25600)
        frames = _packets(19, body, (14, 9))
        parser = GattParser()
        self.assertIsNone(parser.parse(frames[0]))
        parsed = parser.parse(frames[1])
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.command, 19)
        self.assertTrue(parsed.history)
        self.assertEqual(parsed.lock_flag, 1)
        self.assertEqual(parsed.weighing_date, datetime.fromtimestamp(1_700_000_000, timezone.utc))
        self.assertEqual(parsed.role_id, 0x01020304)
        self.assertEqual(parsed.muscle, 12.5)
        self.assertEqual(parsed.visceral_fat, 0.0)
        self.assertEqual(parsed.ori_visceral_fat, 25600.0)

    def test_paket_terakhir_datang_lebih_dulu_mengosongkan_buffer(self):
        frames = _packets(18, _body(_prop(lock=0)), (14, 9))
        parser = GattParser()
        self.assertIsNone(parser.parse(frames[1]))
        self.assertIsNone(parser.parse(frames[0]))
        parsed = parser.parse(frames[1])
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.role_id, 0x01020304)

    def test_paket_1_mengulang_rakitan(self):
        first = _packets(18, _body(_prop(lock=0), role=1), (14, 9))
        second = _packets(18, _body(_prop(lock=0), role=2), (14, 9))
        parser = GattParser()
        self.assertIsNone(parser.parse(first[0]))
        self.assertIsNone(parser.parse(second[0]))
        parsed = parser.parse(second[1])
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.role_id, 2)

    def test_buffer_pengukuran_dan_riwayat_terpisah(self):
        live = _packets(18, _body(_prop(lock=0), role=7), (23,))[0]
        history = _packets(19, _body(_prop(lock=0), role=9), (14, 9))
        parser = GattParser()
        self.assertIsNone(parser.parse(history[0]))
        parsed_live = parser.parse(live)
        self.assertIsNotNone(parsed_live)
        assert parsed_live is not None
        self.assertEqual(parsed_live.role_id, 7)
        self.assertFalse(parsed_live.history)
        parsed_history = parser.parse(history[1])
        self.assertIsNotNone(parsed_history)
        assert parsed_history is not None
        self.assertEqual(parsed_history.role_id, 9)
        self.assertTrue(parsed_history.history)

    def test_setelah_selesai_paket_bukan_1_ditolak(self):
        parser = GattParser()
        parser.parse(_packets(18, _body(_prop(lock=0)), (23,))[0])
        stray = _packets(18, _body(_prop(lock=0)), (14, 9))[1]
        with self.assertRaises(FrameFormatError):
            parser.parse(stray)

    def test_nibble_8_tidak_selesai(self):
        body = _body(_prop(lock=0))
        frame = bytes((0xCA, 17, len(body) + 2, 18, 0x18)) + body
        self.assertIsNone(GattParser().parse(frame))
        with self.assertRaises(GattMenunggu):
            parse_gatt(frame)

    def test_id_peran_dan_waktu_di_atas_int(self):
        body = _body(_prop(lock=0), role=0x80000000, when=0x80000000)
        parsed = parse_gatt(_packets(19, body, (23,))[0])
        self.assertEqual(parsed.role_id, 0)
        self.assertEqual(parsed.weighing_date, datetime.fromtimestamp(0, timezone.utc))

    def test_rakitan_pendek(self):
        frame = bytes((0xCA, 17, 6, 18, 0x11, 1, 2, 3, 4))
        with self.assertRaises(FrameFormatError):
            parse_gatt(frame)


if __name__ == "__main__":
    unittest.main()
