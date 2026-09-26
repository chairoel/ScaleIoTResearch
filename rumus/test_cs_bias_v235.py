"""Angka di sini dicocokkan dengan `bia_calc` di libchipsea_bias_v235.so."""

import unittest

from rumus.cs_bias_v235 import cs_bias_v235, parse_default_z

_FIELDS = (
    "BFP",
    "SLM",
    "BWP",
    "BMC",
    "VFR",
    "PP",
    "SMM",
    "BMI",
    "SBW",
    "MC",
    "WC",
    "FC",
    "BMR",
    "MA",
    "SBC",
)


def _values(sex, age, height, weight_100, impedance_10):
    result = cs_bias_v235(sex, age, height, weight_100, impedance_10)
    data = result.data
    return result.result, None if data is None else tuple(getattr(data, name) for name in _FIELDS)


_GOLDEN = {
    (1, 30, 170, 7055, 5000): (
        21.05156626506024,
        53.045669999999994,
        55.30005669737775,
        2.6024500000000046,
        8.5,
        19.88870218716509,
        29.279374999999995,
        24.39446366782007,
        63.0,
        -3.408122409314993,
        -7.5500030517578125,
        -4.141880642442819,
        1587.320665,
        30,
        64,
    ),
    (0, 30, 170, 7055, 5000): (
        32.940177179305444,
        44.13277,
        47.86678242381289,
        3.127935000000008,
        5.5,
        14.688525232801961,
        26.852474999999995,
        24.39446366782007,
        60.000003814697266,
        -2.3107041854804393,
        -10.549999237060547,
        -8.239295051580108,
        1438.20497,
        39,
        64,
    ),
    (1, 18, 90, 2000, 2000): (
        35.901999999999994,
        14.620099999999999,
        73.107,
        1.0,
        3.0,
        -0.006500000000002615,
        20.0,
        24.691358024691358,
        17.212499618530273,
        1.4667746833801258,
        -2.7875003814697266,
        -4.254275064849852,
        478.8071,
        23,
        58,
    ),
    (0, 99, 220, 25000, 15000): (
        45.0,
        80.147,
        34.54348,
        7.0,
        51.5,
        -2.484680000000003,
        52.92059999999999,
        51.65289256198347,
        102.8499984741211,
        -60.36250114440918,
        -147.1500015258789,
        -86.78750038146973,
        3054.1901,
        80,
        45,
    ),
    (1, 45, 149, 15000, 8500): (
        45.0,
        73.0283,
        42.951899999999995,
        4.0,
        54.0,
        5.733633333333339,
        31.5486,
        67.56452412053511,
        47.1771240234375,
        -43.342987060546875,
        -102.8228759765625,
        -59.479888916015625,
        2287.6192,
        55,
        45,
    ),
    (0, 45, 150, 15001, 8500): (
        45.0,
        48.19933400000001,
        35.8115951431948,
        7.0,
        31.5,
        -3.680847411635878,
        29.380744999999987,
        66.66666666666667,
        48.0,
        -46.505496978759766,
        -102.00999450683594,
        -55.50449752807617,
        1918.0383740000002,
        55,
        45,
    ),
    (1, 60, 190, 5550, 3333): (
        5.0,
        53.753945,
        65.39603153153153,
        1.0,
        1.0,
        31.457923423423424,
        34.15004999999999,
        15.373961218836564,
        77.0,
        11.185,
        21.5,
        10.315,
        1467.43617,
        50,
        64,
    ),
    (0, 25, 191, 8233, 6421): (
        31.59579422530165,
        51.32890200000001,
        46.39019381305302,
        4.0,
        5.5,
        15.95512657336683,
        31.97618499999999,
        22.559688605027276,
        77.52212524414062,
        1.8244100662779026,
        -4.8078765869140625,
        -6.632286653191965,
        1687.0746420000003,
        35,
        79,
    ),
}


class CsBiasV235Test(unittest.TestCase):
    def test_nilai_sama_dengan_library(self):
        for case, expected in _GOLDEN.items():
            with self.subTest(case=case):
                code, values = _values(*case)
                self.assertEqual(code, 0)
                self.assertEqual(values, expected)

    def test_kode_galat_berurutan(self):
        self.assertEqual(cs_bias_v235(0, 30, 170, 1999, 5000).result, -2)
        self.assertEqual(cs_bias_v235(0, 30, 89, 1999, 5000).result, -2)
        self.assertEqual(cs_bias_v235(0, 30, 89, 7000, 5000).result, -3)
        self.assertEqual(cs_bias_v235(0, 17, 170, 7000, 5000).result, -4)
        self.assertEqual(cs_bias_v235(2, 30, 170, 7000, 5000).result, -5)
        self.assertEqual(cs_bias_v235(0, 30, 170, 7000, 1999).result, -6)
        self.assertIsNone(cs_bias_v235(0, 30, 170, 1999, 5000).data)

    def test_laporan_java_memotong_float(self):
        report = parse_default_z(1, 30, 170.9, 70.56, 500.4)
        self.assertEqual(report.result, 0)
        self.assertEqual(report.data.bfp, 21.062211990356445)
        self.assertEqual(report.data.slp, 75.17662048339844)
        self.assertEqual(report.data.bmr, 1587)
        self.assertEqual(report.data.vfl, 8.5)
        self.assertEqual(report.data.sbc, 64)


if __name__ == "__main__":
    unittest.main()
