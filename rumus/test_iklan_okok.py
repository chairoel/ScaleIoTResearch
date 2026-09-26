"""Muatan iklan yang diteruskan ke parser siaran."""

import unittest

from rumus.iklan_okok import muatan_dari_pabrik, muatan_okok

_FRAME = bytes.fromhex("C00702C11388000121")


def _rekaman(frame: bytes, awalan: bytes = b"") -> bytes:
    return awalan + bytes((len(frame) + 1, 0xFF)) + frame


class IklanOkokTest(unittest.TestCase):
    def test_muatan_setelah_bendera(self):
        rekaman = _rekaman(_FRAME, bytes((0x02, 0x01, 0x06)))
        self.assertEqual(muatan_okok(rekaman), _FRAME)

    def test_uuid_sebelum_pabrik_tetap_diambil(self):
        rekaman = _rekaman(_FRAME, bytes((0x03, 0x02, 0xF0, 0xFF)))
        self.assertEqual(muatan_okok(rekaman), _FRAME)

    def test_pabrik_lain_dilewati(self):
        lain = bytes((0x04, 0xFF, 0x01, 0x02, 0x03))
        rekaman = lain + _rekaman(_FRAME)
        self.assertEqual(muatan_okok(rekaman), _FRAME)

    def test_bukan_okok(self):
        self.assertIsNone(muatan_okok(bytes((0x04, 0xFF, 0x01, 0x02, 0x03))))

    def test_rekaman_terpotong(self):
        self.assertIsNone(muatan_okok(bytes((0x05, 0xFF, 0xC0))))

    def test_id_pabrik_little_endian(self):
        company = int.from_bytes(_FRAME[:2], "little")
        self.assertEqual(muatan_dari_pabrik(company, _FRAME[2:]), _FRAME)
        self.assertIsNone(muatan_dari_pabrik(0x0001, b"\x02\x03"))


if __name__ == "__main__":
    unittest.main()
