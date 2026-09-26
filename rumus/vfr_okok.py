"""Tulis ulang [`CsAlgoBuilder.getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java).

Badan method di Java hanya sisa `throw`. Isinya dibaca dari `getVFR` di
[`classes4.dex`](../ScaleHealtSource/base/classes4.dex). Library asli tidak dipanggil.

`vfl` adalah angka native yang disimpan laporan. `getVFR` adalah rumus Java
yang masuk ke skor lewat `getScoreWithAge`. Pada frekuensi ganda dan multi,
method ini mengembalikan `vfl`.
"""

from __future__ import annotations

import math
import struct

_NORMAL = "NORMAL"
_DUAL = "DualFrequency"
_MULTI = "MultiFrequency"

# (tinggi, berat, umur, impedansi, konstanta). Konstanta 8 elektroda perempuan dikurangi.
_MALE_EIGHT = (0xBE7EC56D, 0x3EBE353F, 0x3E09D495, 0x3C06594B, 0x417E6C22)
_FEMALE_EIGHT = (0xBDC95183, 0x3E93B646, 0x3D954C98, 0x3C0CE704, 0x4096978D)
_MALE = (0xBE88F5C3, 0x3ED70A3D, 0x3E15B574, 0x3C4985F0, 0x415FCB29)
_FEMALE = (0xBE290FF9, 0x3E868DB9, 0x3D84EA4B, 0x3B1D4952, 0x41458312)

_ONE = 0x3F800000
_HALF = 0x3F000000
_LEVEL_MAX = 0x426C0000


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _bits(raw: int) -> float:
    return struct.unpack(">f", raw.to_bytes(4, "big"))[0]


def _mul(left: float, right: float) -> float:
    return _f32(_f32(left) * _f32(right))


def _add(left: float, right: float) -> float:
    return _f32(_f32(left) + _f32(right))


def _sub(left: float, right: float) -> float:
    return _f32(_f32(left) - _f32(right))


def _cmpg(left: float, right: float) -> int:
    if math.isnan(left) or math.isnan(right):
        return 1
    if left > right:
        return 1
    if left < right:
        return -1
    return 0


def _cmpl(left: float, right: float) -> int:
    if math.isnan(left) or math.isnan(right):
        return -1
    if left > right:
        return 1
    if left < right:
        return -1
    return 0


def _float_to_int(value: float) -> int:
    """`float-to-int`: potong ke nol, NaN menjadi 0, di luar int32 dijepit."""
    if math.isnan(value):
        return 0
    if value >= 2147483648.0:
        return 2147483647
    if value < -2147483648.0:
        return -2147483648
    return math.trunc(value)


def _half_step(value: float) -> float:
    """Pecahan di bawah 0,5 tetap .0. Selain itu ditambah 0,5, tanpa naik ke bilangan berikutnya."""
    whole = _f32(float(_float_to_int(value)))
    fraction = _sub(value, whole)
    if _cmpg(fraction, _bits(_HALF)) >= 0:
        return _add(whole, _bits(_HALF))
    return whole


def _clamp_level(value: float) -> float:
    one = _bits(_ONE)
    if _cmpg(value, one) >= 0:
        ceiling = _bits(_LEVEL_MAX)
        if _cmpl(value, ceiling) <= 0:
            return value
        return ceiling
    return one


def _local(age: int, sex: int, eight: bool, height: float, weight: float, impedance: float) -> float:
    if age <= 17:
        return _f32(0.0)
    if eight:
        coef = _MALE_EIGHT if sex == 1 else _FEMALE_EIGHT
    else:
        coef = _MALE if sex == 1 else _FEMALE
    height_c, weight_c, age_c, impedance_c, constant = (_bits(item) for item in coef)
    total = _mul(height, height_c)
    total = _add(total, _mul(weight, weight_c))
    age_f = _f32(float(age))
    if not eight:
        age_f = _mul(age_f, _bits(_ONE))
    total = _add(total, _mul(age_f, age_c))
    total = _add(total, _mul(impedance, impedance_c))
    if eight and sex != 1:
        total = _sub(total, constant)
    else:
        total = _add(total, constant)
    return _clamp_level(_half_step(total))


def get_vfr(
    scale_type: str,
    age: int,
    sex: int,
    eight_electrode: bool,
    height_cm: float,
    weight_kg: float,
    impedance_ohm: float,
    vfl: float,
    bias_success: bool,
) -> float:
    """Tingkat lemak viseral yang dipakai skor.

    `scale_type` memakai nama [`Type`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java):
    `NORMAL`, `DualFrequency`, atau `MultiFrequency`. Jenis kelamin 1 adalah laki-laki.
    """
    stored = _f32(vfl)
    if scale_type in (_DUAL, _MULTI):
        return stored
    if scale_type != _NORMAL:
        raise ValueError("jenis timbangan di luar getVFR")
    level = _local(
        age,
        sex,
        eight_electrode,
        _f32(height_cm),
        _f32(weight_kg),
        _f32(impedance_ohm),
    )
    if eight_electrode:
        return level
    if bias_success:
        return stored
    return level
