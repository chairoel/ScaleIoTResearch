"""Angka dicocokkan dengan getVFR di classes4.dex."""

import unittest

from rumus.vfr_okok import get_vfr


def _vfr(**overrides):
    values = dict(
        scale_type="NORMAL",
        age=30,
        sex=1,
        eight_electrode=False,
        height_cm=170,
        weight_kg=70.5,
        impedance_ohm=500,
        vfl=3.25,
        bias_success=False,
    )
    values.update(overrides)
    return get_vfr(**values)


class VfrRumusTest(unittest.TestCase):
    def test_laki_laki_bukan_delapan_elektroda(self):
        self.assertEqual(_vfr(), 8.5)

    def test_perempuan_bukan_delapan_elektroda(self):
        self.assertEqual(_vfr(sex=0), 5.5)
        self.assertEqual(_vfr(sex=2), 5.5)

    def test_delapan_elektroda(self):
        self.assertEqual(_vfr(eight_electrode=True), 7.5)
        self.assertEqual(_vfr(sex=0, eight_electrode=True), 5.0)

    def test_pecahan_setengah(self):
        self.assertEqual(_vfr(impedance_ohm=487), 8.0)
        self.assertEqual(_vfr(impedance_ohm=488), 8.5)

    def test_batas_1_dan_59(self):
        self.assertEqual(
            _vfr(age=18, height_cm=220, weight_kg=40, impedance_ohm=200),
            1.0,
        )
        self.assertEqual(
            _vfr(age=90, height_cm=100, weight_kg=180, impedance_ohm=1600),
            59.0,
        )

    def test_umur_17_dan_bias(self):
        self.assertEqual(_vfr(age=17, eight_electrode=True, bias_success=True), 0.0)
        self.assertEqual(_vfr(age=17), 0.0)
        self.assertEqual(_vfr(age=17, bias_success=True), 3.25)
        self.assertEqual(_vfr(bias_success=True), 3.25)
        self.assertEqual(_vfr(eight_electrode=True, bias_success=True), 7.5)

    def test_frekuensi_ganda_dan_multi_mengembalikan_vfl(self):
        self.assertEqual(_vfr(scale_type="DualFrequency", age=10), 3.25)
        self.assertEqual(_vfr(scale_type="MultiFrequency", bias_success=False), 3.25)

    def test_jenis_tidak_dikenal(self):
        with self.assertRaises(ValueError):
            _vfr(scale_type="lain")


if __name__ == "__main__":
    unittest.main()
