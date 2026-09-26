"""Angka di sini dicocokkan dengan `bia_calc` di libchipsea_bias_vA019.so."""
import hashlib
import unittest

from rumus.cs_bias_vA019 import (
    cs_bias_vA019,
    metric_regression,
    parse_multi_frequency,
    _execute,
)

_Z = (5000, 4800, 300, 4500, 4600, 5100, 4900, 280, 4400, 4700)
_EDGE = (1000, 7500, 100, 1000, 7500, 7500, 1000, 650, 7500, 1000)
_BAD = (999, 4800, 300, 4500, 4600, 5100, 4900, 280, 4400, 4700)

_KEYS = (
    "bfp",
    "slm",
    "bmi",
    "standard_weight",
    "bmr",
    "vfl",
    "metabolic_age",
    "body_score",
    "la_slm",
    "tr_bfm",
    "sfm",
    "obesity_degree",
)


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


_GOLDEN = {
    (1, 30, 1700, 700, 0, _Z): (
        "51ab4151c9678d97e69aaf5b41fc5f18b678018ec564634256a8a2bc428ab952",
        (
            40.8,
            38.9,
            24.2,
            63.0,
            1265,
            13,
            36,
            60,
            2.0,
            14.0,
            23.1,
            11.1,
        ),
    ),
    (0, 30, 1700, 700, 0, _Z): (
        "02114f46b0f578cc35efbf15a9e824fd984545d01a35b1cd046dbe448e47d32e",
        (
            44.6,
            36.2,
            24.2,
            60.0,
            1207,
            14,
            35,
            61,
            2.0,
            15.2,
            25.6,
            16.7,
        ),
    ),
    (1, 6, 1200, 400, 0, _Z): (
        "d2223a0b6f359561c2348800d4d1cf784aa3f21bfa78cd496bdf83ac7727b76d",
        (
            52.2,
            18.1,
            27.8,
            30.6,
            783,
            15,
            6,
            70,
            0.8,
            9.8,
            16.9,
            30.7,
        ),
    ),
    (1, 99, 1500, 600, 0, _Z): (
        "8289f59325cb14b1dd7926050d875bc1d71d607da7349223b0a79bdcc12226ee",
        (
            48.3,
            29.1,
            26.7,
            49.0,
            1040,
            14,
            100,
            60,
            1.5,
            15.1,
            23.2,
            22.4,
        ),
    ),
    (1, 30, 1700, 200, 0, _Z): (
        "b7ce80157aea2a23f933c8425182b0bf3badd5fce5a4052f49133e229676255f",
        (
            3.0,
            17.5,
            6.9,
            63.0,
            789,
            1,
            36,
            60,
            1.0,
            0.2,
            0.6,
            0.4,
        ),
    ),
    (1, 40, 1750, 1501, 0, _Z): (
        "a190f25f9e03ee0323e53cd998e39829fff3399e7e64a30d9d4e6283f72b8fec",
        (
            55.0,
            63.9,
            49.0,
            66.5,
            1829,
            38,
            46,
            60,
            3.5,
            43.8,
            66.0,
            125.7,
        ),
    ),
    (0, 40, 2200, 900, 0, _Z): (
        "2f803dd48062db052af6d38bfa5c54757ade36710bc1668f3f25d813ab46869b",
        (
            24.1,
            64.3,
            18.6,
            102.9,
            1845,
            9,
            40,
            73,
            3.3,
            10.2,
            18.7,
            0.4,
        ),
    ),
    (0, 25, 1650, 620, 0, _EDGE): (
        "f8158425c13a8141df1f42089d969aaaf214eaf99f13ef6a46d5f8b4bd555f1e",
        (
            34.1,
            38.1,
            22.8,
            57.0,
            1252,
            4,
            24,
            74,
            2.2,
            10.0,
            19.0,
            8.8,
        ),
    ),
    (1, 30, 1700, 700, 1, _Z): (
        "d1b0d94d68e4f6ac3a7316cb6e04cfa3e1c1f10ca6f777970503a5c7b7b7d8db",
        (
            0.0,
            0.0,
            24.2,
            63.0,
            0,
            0,
            18,
            60,
            0.0,
            0.0,
            0.0,
            11.1,
        ),
    ),
    (1, 30, 1700, 700, 1, (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)): (
        "d1b0d94d68e4f6ac3a7316cb6e04cfa3e1c1f10ca6f777970503a5c7b7b7d8db",
        (
            0.0,
            0.0,
            24.2,
            63.0,
            0,
            0,
            18,
            60,
            0.0,
            0.0,
            0.0,
            11.1,
        ),
    ),
    (1, 30, 1700, 700, 1, _BAD): (
        "d1b0d94d68e4f6ac3a7316cb6e04cfa3e1c1f10ca6f777970503a5c7b7b7d8db",
        (
            0.0,
            0.0,
            24.2,
            63.0,
            0,
            0,
            18,
            60,
            0.0,
            0.0,
            0.0,
            11.1,
        ),
    ),
}


_SEED = 24.221453287197235
_REGRESSION = (
    (0, 40.827466294992256),
    (2, 31.961128943334767),
    (9, 1.9140253167195729),
    (19, 17.409626510834112),
)


class CsBiasVA019Test(unittest.TestCase):
    def test_nilai_sama_dengan_library(self):
        for case, (digest, fields) in _GOLDEN.items():
            sex, age, height, weight, mode, impedance = case
            with self.subTest(case=case):
                code, raw = _execute(sex, age, height, weight, mode, impedance)
                self.assertEqual(code, 0)
                self.assertEqual(_digest(raw), digest)
                result = cs_bias_vA019(sex, age, height, weight, mode, impedance)
                self.assertEqual(result.result, 0)
                got = tuple(getattr(result.data, name) for name in _KEYS)
                self.assertEqual(got, fields)

    def test_kode_galat_berurutan(self):
        self.assertEqual(cs_bias_vA019(1, 30, 1700, 700, 0, None).result, 1)
        self.assertIsNone(cs_bias_vA019(1, 30, 1700, 700, 0, None).data)
        self.assertEqual(cs_bias_vA019(1, 30, 1700, 199, 0, _Z).result, 2)
        self.assertEqual(cs_bias_vA019(1, 30, 899, 199, 0, _Z).result, 2)
        self.assertEqual(cs_bias_vA019(1, 30, 899, 700, 0, _Z).result, 3)
        self.assertEqual(cs_bias_vA019(1, 30, 2201, 700, 0, _Z).result, 3)
        self.assertEqual(cs_bias_vA019(1, 5, 1700, 700, 0, _Z).result, 4)
        self.assertEqual(cs_bias_vA019(1, 100, 1700, 700, 0, _Z).result, 4)
        self.assertEqual(cs_bias_vA019(2, 30, 1700, 700, 0, _Z).result, 5)
        self.assertEqual(cs_bias_vA019(1, 30, 1700, 700, 0, _BAD).result, 6)
        self.assertIsNone(cs_bias_vA019(1, 30, 1700, 199, 0, _Z).data)

    def test_regresi_mode_nol(self):
        for index, expected in _REGRESSION:
            with self.subTest(index=index):
                got = metric_regression(index, _SEED, 1, 1700, 700, _Z)
                self.assertEqual(got, expected)

    def test_laporan_java_memotong_float(self):
        report = parse_multi_frequency(
            1,
            30,
            170.06,
            70.04,
            [value / 10 for value in _Z],
        )
        self.assertEqual(report.result, 0)
        self.assertEqual(report.data.bfp, 40.79999923706055)
        self.assertEqual(report.data.bmr, 1266)
        self.assertEqual(report.data.vfl, 13.0)
        self.assertEqual(report.data.sfm, 23.1)
        self.assertEqual(report.data.sbc, 60)
        self.assertEqual(report.data.swt, 63.099998474121094)


if __name__ == "__main__":
    unittest.main()
