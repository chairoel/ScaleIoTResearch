"""Siaran OKOK yang tidak terenkripsi, dicocokkan dengan parser Java."""

import unittest

from rumus.siaran_okok import (
    EncryptedBroadcastError,
    FrameFormatError,
    parse_broadcast,
    parse_weight,
)


def _prop(lock=1, digit="10", unit="kg", fat=False):
    unit_bits = {"kg": "00", "jin": "01", "lb": "10", "st": "11"}[unit]
    digit_bits = {"int": "01", "10": "00", "100": "10"}[digit]
    bits = f"00{1 if fat else 0}{unit_bits}{digit_bits}{lock}"
    return int(bits, 2)


class ParseWeightTest(unittest.TestCase):
    def test_kilogram_satu_desimal(self):
        kg, text = parse_weight(0x02, 0xC1, _prop())
        self.assertEqual(kg, 70.5)
        self.assertEqual(text, "70.5")

    def test_jin_dibagi_dua(self):
        kg, text = parse_weight(0x00, 0x8C, _prop(unit="jin"))
        self.assertEqual(kg, 7.0)
        self.assertEqual(text, "14.0")

    def test_pon_bilangan_bulat(self):
        kg, text = parse_weight(0x00, 0x64, _prop(digit="int", unit="lb"))
        self.assertEqual(kg, 45.0)
        self.assertEqual(text, "100")

    def test_stone_lewat_float32(self):
        kg, text = parse_weight(1, 0, _prop(unit="st"))
        self.assertEqual(text, "1:0.0")
        self.assertEqual(kg, 6.3)


class BroadcastTest(unittest.TestCase):
    def test_c0_lemak_terkunci(self):
        frame = bytes((0xC0, 7, 0x02, 0xC1, 0x13, 0x88, 0x00, 0x01, 0x21))
        parsed = parse_broadcast(frame, "AA:BB:CC:DD:EE:FF")
        self.assertEqual(parsed.header, 0xC0)
        self.assertEqual(parsed.version, 1)
        self.assertEqual(parsed.mac, "AA:BB:CC:DD:EE:FF")
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.scale_weight, "70.5")
        self.assertEqual(parsed.impedance_ohm, 500.0)
        self.assertEqual(parsed.product_id, 1)
        self.assertEqual(parsed.device_type, 2)
        self.assertEqual(parsed.seq, 7)
        self.assertTrue(parsed.locked)
        self.assertEqual(parsed.cmd_id, 1)

    def test_c0_terenkripsi_ditolak(self):
        short = bytes((0xC0, 1, 0, 0, 0x80, 0, 0, 0, 0x21))
        long = short + bytes(6)
        with self.assertRaises(EncryptedBroadcastError):
            parse_broadcast(short)
        with self.assertRaises(EncryptedBroadcastError):
            parse_broadcast(long)

    def test_ca_versi_32_terkunci(self):
        frame = bytes(
            (0xCA, 0x20, 0, 0, 0, 0, 42, 1, 0x21, 3, 0x02, 0xC1, 0x13, 0x88)
        )
        parsed = parse_broadcast(frame)
        self.assertEqual(parsed.version, 32)
        self.assertEqual(parsed.product_id, 42)
        self.assertEqual(parsed.device_type, 2)
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.impedance_ohm, 500.0)
        self.assertEqual(parsed.seq, 3)
        self.assertTrue(parsed.locked)

    def test_ca_versi_32_belum_kunci(self):
        frame = bytes((0xCA, 0x20, 0, 0, 0, 0, 42, 0, 0x20, 9, 0x02, 0xC1, 0x13, 0x88))
        parsed = parse_broadcast(frame)
        self.assertEqual(parsed.weight_kg, 0.0)
        self.assertEqual(parsed.scale_weight, "")
        self.assertEqual(parsed.impedance_ohm, 0.0)
        self.assertEqual(parsed.seq, 0)
        self.assertFalse(parsed.locked)
        self.assertEqual(parsed.device_type, 0)

    def test_ca_versi_17(self):
        frame = bytes((0xCA, 17, 0, 0x21, 2, 0x02, 0xC1, 0, 0, 1, 0))
        parsed = parse_broadcast(frame)
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.product_id, 256)
        self.assertEqual(parsed.device_type, 2)
        self.assertIsNone(parsed.impedance_ohm)
        self.assertTrue(parsed.locked)

    def test_ca_versi_16_timbangan_berat(self):
        frame = bytes((0xCA, 16, 0, 0, 0x21, 0, 0, 0, 0x02, 0x8F))
        parsed = parse_broadcast(frame)
        self.assertEqual(parsed.weight_kg, 65.5)
        self.assertIsNone(parsed.scale_weight)
        self.assertEqual(parsed.product_id, 0)
        self.assertEqual(parsed.cmd_id, 0x21)
        self.assertEqual(parsed.device_type, 0)
        self.assertTrue(parsed.locked)

    def test_ca_versi_lain_kosong(self):
        parsed = parse_broadcast(bytes((0xCA, 1, 0, 0, 0)))
        self.assertEqual(parsed.weight_kg, 0.0)
        self.assertEqual(parsed.version, 1)

    def test_cloud(self):
        frame = bytes((0xFF, 0, 1, 0x04, 0xC1, 0x02, 0, 0, 0, 2))
        parsed = parse_broadcast(frame)
        self.assertEqual(parsed.device_type, 1)
        self.assertEqual(parsed.weight_kg, 70.5)
        self.assertEqual(parsed.product_id, 2)
        self.assertEqual(parsed.property, 1)
        self.assertEqual(parsed.cmd_id, 0)
        self.assertIsNone(parsed.impedance_ohm)

    def test_cloud_product_khusus(self):
        frame = bytes((0xFF, 0, 1, 0, 0xE8, 0x03, 0xFA, 0xFB, 0xFC, 0xFD))
        parsed = parse_broadcast(frame)
        self.assertEqual(parsed.product_id, 997264800)
        self.assertEqual(parsed.weight_kg, 100.0)
        self.assertEqual(parsed.scale_weight, "100.0")
        self.assertEqual(parsed.property, 1)

    def test_ditolak(self):
        with self.assertRaises(FrameFormatError):
            parse_broadcast(b"")
        with self.assertRaises(FrameFormatError):
            parse_broadcast(bytes((0xAB,)))
        with self.assertRaises(FrameFormatError):
            parse_broadcast(bytes(8))


if __name__ == "__main__":
    unittest.main()
