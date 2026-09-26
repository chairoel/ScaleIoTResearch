"""Tulis ulang `cs_bias_v235` dari `libchipsea_bias_v235.so`.

Pemanggil Java-nya [`CsAlgoBuilder.parseDefaultZ`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java).
Library asli tidak dipanggil. Pembulatan `fmadd` di ARM dipertahankan lewat
satu pembulatan pada `a * b + c`, karena dua operasi Python terpisah
bergeser satu ulp.

Jenis kelamin: 0 perempuan, 1 laki-laki. Itu sama dengan baris koefisien
yang cocok dengan `Sex == 1` di `getBFR_Raw`.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from decimal import Context, Decimal, localcontext

_FMA = Context(prec=80)

# Kelompok baris koefisien. Indeks baris = sex + 2 * kelompok.
_FAT, _SLM, _WATER, _BMR, _VISCERAL, _AGE = range(6)

# Lima int32 per baris, dari simbol `coefficient` di .rodata 0xa78.
# Urutan: tinggi, berat, umur, impedansi, konstanta. Skala 10000.
_COEFFICIENT = (
    (-3332, 7509, 196, 72, 227193),
    (-3315, 6216, 183, 85, 225540),
    (31860, 19340, -2060, -1320, -1645560),
    (28670, 38940, -4080, -1235, -1576650),
    (87700, 297300, 12800, -6030, 517500),
    (93900, 375800, -3200, -6925, 97000),
    (75432, 99474, -34382, -3090, -2882821),
    (75037, 131523, -43376, -3486, -3117751),
    (-1651, 2628, 649, 24, 123445),
    (-2675, 4200, 1462, 123, 139871),
    (-11165, 15784, 4615, 415, 832548),
    (-7471, 9161, 4184, 517, 542267),
)


def _d(bits: int) -> float:
    return struct.unpack("<d", struct.pack("<Q", bits))[0]


def _f(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits))[0]


# Double di .rodata. Beberapa nilai adalah float32 yang dilebarkan.
_K_VFR_4 = _d(0xBFD2147AE0000000)
_K_POLY_SCALE = _d(0x3FD99999A0000000)
_K_SMM_CONST = _d(0xC034376C8B439581)
_K_SCORE_F_LIN = _d(0xC0240A3D80000000)
_K_BODY_SCALE = _d(0x3FB99999A0000000)
_K_BMI_QUAD = _d(0xC016BE76C0000000)
_K_SCORE_M_LIN = _d(0x4025B33340000000)
_K_SMM_WT = _d(0x3FC65604189374BC)
_K_VFR_CONST = _d(0x4056566660000000)
_K_SCORE_F_4 = _d(0x3F302E4B60000000)
_K_SMM_AGE = _d(0xBF907C84B5DCC63F)
_K_VFR_3 = _d(0x400F4BC6A0000000)
_K_SCORE_M_2 = _d(0xBFD2E48E80000000)
_K_SCORE_F_2 = _d(0x3FEEB5DCC0000000)
_K_SCORE_M_CONST = _d(0x3FDB2FEC60000000)
_K_VFR_5 = _d(0x3F7D8A5480000000)
_K_BMI_LIN = _d(0x406E366660000000)
_K_SCORE_F_3 = _d(0xBF9C8C9320000000)
_K_SMM_SEX = _d(0x40036A4A8C154C98)
_K_VFR_1 = _d(0x403E6147A0000000)
_K_SMM_Z = _d(0xBF916872B020C49C)
_K_VFR_2 = _d(0xC036451EC0000000)
_K_VFR_WEIGHT = _d(0x3FB47AE140000000)
_K_SCORE_F_CONST = _d(0x40541AE140000000)
_K_SMM_H = _d(0x3FD0779A6B50B0F2)
_K_SCORE_M_3 = _d(0xBF6A0F0A60000000)
_K_SCORE_M_4 = _d(0x3F1C714FC0000000)
_K_FC_SEX = _d(0xBFB47AE147AE147B)
_K_BMI_COEF = _d(0x3FD99999A0000000)
_K_BMI_COEF_ZERO_VFR = _d(0x3FDEB851E0000000)
_K_AGE_ON_BFP = _f(0x3CF5C28F)
_K_WT_MALE = _f(0x3F451EB8)
_K_WT_FEMALE = _f(0x3F3C28F6)

_BMI_ADD = -2470.0
_VFR_FLOOR = -50.0


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _fma(a: float, b: float, c: float) -> float:
    with localcontext(_FMA):
        wide = Decimal(a) * Decimal(b) + Decimal(c)
    return float(wide)


def _i16(value: int) -> int:
    value &= 0xFFFF
    if value >= 0x8000:
        return value - 0x10000
    return value


def _linear(height: int, weight_100: int, impedance_10: int, age: int, sex: int, group: int) -> float:
    """(c0*H + c1*berat + c2*umur + c3*Z + c4) / 10000."""
    c0, c1, c2, c3, c4 = _COEFFICIENT[sex + (group << 1)]
    height_s = _i16(height)
    weight_s = _i16(weight_100)
    impedance_s = _i16(impedance_10)
    from_weight = float(c1) * float(weight_s) / 100.0
    from_z = float(c3) * float(impedance_s) / 10.0
    total = _fma(float(c0), float(height_s), from_weight)
    total = _fma(float(c2), float(age & 0xFF), total)
    return (total + from_z + float(c4)) / 10000.0


def _half_step(value: float) -> float:
    """Bagian pecahan di bawah 0,5 menjadi .0, selain itu .5. Tidak naik ke bilangan berikutnya."""
    whole = math.trunc(value)
    if value - float(whole) < 0.5:
        return float(whole)
    return float(_f32(_f32(whole) + _f32(0.5)))


def _standard_weight(height: int, sex: int) -> float:
    height_u = height & 0xFFFF
    if (height_u - 150) & 0xFFFFFFFF > 40:
        height_f = _f32(_i16(height_u))
        scaled = _f32(_f32(height_f * _f32(21.25)) / _f32(100.0))
        return float(_f32(_f32(scaled * height_f) / _f32(100.0)))
    if sex != 1:
        delta = _i16(height_u - 70)
        return float(_f32(_f32(delta) * _f32(0.6)))
    delta = _i16(height_u - 80)
    return float(_f32(_f32(delta) * _f32(0.7)))


def _body_age(raw: float, age: int) -> int:
    age &= 0xFF
    estimate = math.trunc(raw)
    if estimate - age >= 11:
        estimate = age + 10
    elif age - estimate > 10:
        estimate = age - 10
    if estimate <= 18:
        estimate = 18
    if estimate >= 80:
        estimate = 80
    return estimate


def _score(bfp: float, slm: float, vfr: float, bmi: float, weight_100: int, age: int, sex: int) -> int:
    bmi_poly = _fma(bmi * _K_BMI_QUAD, bmi, bmi * _K_BMI_LIN) + _BMI_ADD
    if bmi_poly < 55.0:
        bmi_base = 55.0
    elif bmi_poly > 96.0:
        bmi_base = 96.0
    else:
        bmi_base = bmi_poly

    x = bfp + float(_f32(float(age & 0xFF) * _K_AGE_ON_BFP))
    if sex != 0:
        square = x * x
        cube = x * square
        fourth = x * cube
        male = cube * _K_SCORE_M_3
        male = _fma(fourth, _K_SCORE_M_4, male)
        male = _fma(square, _K_SCORE_M_2, male)
        fat_term = _fma(x, _K_SCORE_M_LIN, male) + _K_SCORE_M_CONST
        weight_coef = _K_WT_MALE
    else:
        fourth = x * _K_SCORE_F_4
        cube = x * _K_SCORE_F_3
        fourth = x * fourth
        cube = x * cube
        fourth = x * fourth
        cube = x * cube
        female = _fma(fourth, x, cube)
        female = _fma(x * _K_SCORE_F_2, x, female)
        fat_term = _fma(x, _K_SCORE_F_LIN, female) + _K_SCORE_F_CONST
        weight_coef = _K_WT_FEMALE

    if vfr < 15.0:
        fifth = vfr * _K_VFR_5
        fourth = vfr * _K_VFR_4
        cubic_base = vfr * _K_VFR_3
        fifth = vfr * fifth
        fourth = vfr * fourth
        fifth = vfr * fifth
        fourth = vfr * fourth
        fifth = vfr * fifth
        fourth = vfr * fourth
        visceral = _fma(fifth, vfr, fourth)
        visceral = _fma(vfr * cubic_base, vfr, visceral)
        visceral = _fma(vfr * _K_VFR_2, vfr, visceral)
        visceral = _fma(vfr, _K_VFR_1, visceral) + _K_VFR_CONST
    else:
        visceral = _VFR_FLOOR
    if visceral < _VFR_FLOOR:
        visceral = _VFR_FLOOR

    weight_s = _f32(_i16(weight_100))
    weight_term = _f32(_f32(weight_s / _f32(-100.0)) * weight_coef)
    body = slm + 90.0 + float(weight_term)
    if body > 100.0:
        body = 100.0
    if fat_term < 55.0:
        fat_term = 55.0

    bmi_coef = _K_BMI_COEF_ZERO_VFR if vfr == 0.0 else _K_BMI_COEF
    visceral_scale = 0.0 if vfr == 0.0 else _K_VFR_WEIGHT
    total = _fma(bmi_coef, bmi_base, fat_term * _K_POLY_SCALE)
    total = _fma(body, _K_BODY_SCALE, total)
    total = _fma(visceral_scale, visceral, total)
    raw = math.trunc(total)
    if raw >= 100:
        raw = 100
    if raw <= 45:
        raw = 45
    return raw


@dataclass(frozen=True)
class BiasV235Data:
    """Isi `CSBiasDataV235`. Satuan mengikuti library, belum disempitkan ke float Java."""

    BFP: float
    SLM: float
    BWP: float
    BMC: float
    VFR: float
    PP: float
    SMM: float
    BMI: float
    SBW: float
    MC: float
    WC: float
    FC: float
    BMR: float
    MA: int
    SBC: int


@dataclass(frozen=True)
class BiasV235Result:
    result: int
    data: BiasV235Data | None


def cs_bias_v235(sex: int, age: int, height_cm: int, weight_100: int, impedance_10: int) -> BiasV235Result:
    """Sama dengan JNI `cs_bias_v235`.

    `weight_100` adalah berat kilogram kali 100. `impedance_10` adalah ohm kali 10.
    Tinggi, berat, dan impedansi dipotong ke 16 bit. Umur dan jenis kelamin dipotong ke 8 bit.

    Rentang yang diterima library: berat 20–250 kg, tinggi 90–220 cm, umur 18–99,
    jenis kelamin 0 atau 1, impedansi 200–1500 ohm. Di luar itu `data` kosong dan
    `result` negatif: -2 berat, -3 tinggi, -4 umur, -5 jenis kelamin, -6 impedansi.
    """
    sex &= 0xFF
    age &= 0xFF
    height_cm &= 0xFFFF
    weight_100 &= 0xFFFF
    impedance_10 &= 0xFFFF

    weight_s = _i16(weight_100)
    weight_times_100 = _f32(weight_s)
    weight_kg_f = _f32(weight_times_100 / _f32(100.0))
    if not (weight_kg_f >= _f32(20.0) and weight_kg_f <= _f32(250.0)):
        return BiasV235Result(-2, None)
    if 65405 > ((height_cm - 221) & 0xFFFF):
        return BiasV235Result(-3, None)
    if ((age - 100) & 0xFF) < 174:
        return BiasV235Result(-4, None)
    if sex > 1:
        return BiasV235Result(-5, None)
    if 52535 > ((impedance_10 - 15001) & 0xFFFF):
        return BiasV235Result(-6, None)

    weight10 = float(_f32(weight_times_100 / _f32(10.0)))
    weight_kg = float(weight_kg_f)
    heavy = weight_kg_f > _f32(150.0)

    bfp = _linear(height_cm, weight_100, impedance_10, age, sex, _FAT) / weight10 * 1000.0
    if bfp > 45.0 or bfp < 5.0:
        bfp = 45.0 if bfp > 45.0 else 5.0

    slm = _linear(height_cm, weight_100, impedance_10, age, sex, _SLM) / 10.0
    slm_hi = 236.5 if heavy else 141.5
    if slm < 7.0:
        slm = 7.0
    elif slm > slm_hi:
        slm = slm_hi

    bone = float(math.trunc(weight10)) / 10.0 + (bfp * weight10 / -1000.0) - slm
    bone_hi = 7.0 if heavy else 4.0
    if bone >= bone_hi:
        bone = bone_hi
    elif bone <= 1.0:
        bone = 1.0

    water = _linear(height_cm, weight_100, impedance_10, age, sex, _WATER) / weight10 * 10.0
    if water < 20.0:
        water = 20.0
    elif water > 85.0:
        water = 85.0

    height_s = _i16(height_cm)
    impedance_s = _i16(impedance_10)
    protein = (slm + (water * weight10 / -1000.0)) / weight_kg * 100.0
    muscle = _fma(float(weight_s), _K_SMM_WT, 0.0) / 100.0
    muscle_z = float(impedance_s) * _K_SMM_Z / 10.0
    muscle = _fma(float(height_s), _K_SMM_H, muscle)
    muscle = _fma(float(age), _K_SMM_AGE, muscle)
    muscle = muscle + muscle_z + _K_SMM_CONST
    muscle = _fma(float(sex), _K_SMM_SEX, muscle)
    muscle_hi = 117.0 if heavy else 70.0
    if muscle > muscle_hi:
        muscle = muscle_hi
    elif muscle < 20.0:
        muscle = 20.0

    bmr = _linear(height_cm, weight_100, impedance_10, age, sex, _BMR)
    visceral = _half_step(_linear(height_cm, weight_100, impedance_10, age, sex, _VISCERAL))
    if visceral > 59.0:
        visceral = 59.0
    elif visceral < 1.0:
        visceral = 1.0

    height_sq = height_s * height_s
    bmi = float(math.trunc(weight10)) * 1000.0 / float(height_sq)
    standard = _standard_weight(height_cm, sex)
    fat_control = bfp * weight_kg / -100.0
    slope = _fma(float(sex), _K_FC_SEX, 0.25)
    weight_control = standard - weight_kg
    fat_control = _fma(standard, slope, fat_control)
    muscle_control = weight_control - fat_control
    metabolic_age = _body_age(
        _linear(height_cm, weight_100, impedance_10, age, sex, _AGE),
        age,
    )
    body_score = _score(bfp, slm, visceral, bmi, weight_100, age, sex)
    data = BiasV235Data(
        BFP=bfp,
        SLM=slm,
        BWP=water,
        BMC=bone,
        VFR=visceral,
        PP=protein,
        SMM=muscle,
        BMI=bmi,
        SBW=standard,
        MC=muscle_control,
        WC=weight_control,
        FC=fat_control,
        BMR=bmr,
        MA=metabolic_age,
        SBC=body_score,
    )
    return BiasV235Result(0, data)


@dataclass(frozen=True)
class OkokReport:
    """Nilai yang disimpan `parseDefaultZ` setelah penyempitan Java."""

    bfp: float
    slm: float
    slp: float
    bwp: float
    bmc: float
    vfl: float
    pp: float
    smm: float
    swt: float
    mc: float
    wc: float
    fc: float
    bmr: int
    ma: int
    sbc: int


@dataclass(frozen=True)
class OkokReportResult:
    result: int
    data: OkokReport | None


def parse_default_z(
    sex: int,
    age: int,
    height_cm: float,
    weight_kg: float,
    impedance_ohm: float,
) -> OkokReportResult:
    """Jalan yang sama dengan `parseDefaultZ` sampai field laporan terisi.

    Lemak viseral yang disimpan adalah `vfl`, dari field native `VFR`. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) adalah rumus Java untuk skor, di [`rumus/vfr_okok.py`](vfr_okok.py), dan tidak dipakai di sini.
    """
    height_f = _f32(height_cm)
    weight_f = _f32(weight_kg)
    impedance_f = _f32(impedance_ohm)
    native = cs_bias_v235(
        sex,
        age,
        math.trunc(height_f),
        math.trunc(_f32(_f32(100.0) * weight_f)),
        math.trunc(_f32(impedance_f * _f32(10.0))),
    )
    if native.result != 0 or native.data is None:
        return OkokReportResult(native.result, None)
    data = native.data
    if weight_f > 0.0:
        slp = _f32((data.SLM / float(weight_f)) * 100.0)
    else:
        slp = 0.0
    report = OkokReport(
        bfp=_f32(data.BFP),
        slm=_f32(data.SLM),
        slp=slp,
        bwp=_f32(data.BWP),
        bmc=_f32(data.BMC),
        vfl=_f32(data.VFR),
        pp=_f32(data.PP),
        smm=_f32(data.SMM),
        swt=_f32(data.SBW),
        mc=_f32(data.MC),
        wc=_f32(data.WC),
        fc=_f32(data.FC),
        bmr=math.trunc(data.BMR),
        ma=data.MA,
        sbc=data.SBC,
    )
    return OkokReportResult(0, report)
