"""Tulis ulang `cs_bias_vA019` dari `libchipsea_bias_vA019.so`.

Pemanggil Java-nya [`CsAlgoBuilder.toParserMultiFrequencyData`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java).
Library asli tidak dipanggil. `fmadd` ARM dibulatkan sekali lewat `Decimal`,
sama seperti tulis ulang v235.

Jenis kelamin: 0 perempuan, 1 laki-laki. Tinggi dan berat masuk sebagai
persepuluhan (cm dan kg kali 10). Sepuluh impedansi juga ohm kali 10, urutan
tangan kanan, tangan kiri, batang, kaki kanan, kaki kiri, lalu frekuensi kedua
dengan urutan yang sama. `mode` pada pemanggil Java selalu 0.

Kode gagal positif: 1 masukan kosong, 2 berat, 3 tinggi, 4 umur, 5 jenis
kelamin, 6 impedansi. Berat yang lolos 20,0–250,0 kg, tinggi 90,0–220,0 cm,
umur 6–99. Pada mode 0, tungkai 100,0–750,0 ohm dan batang 10,0–65,0 ohm.
Mode lain melewati pemeriksaan impedansi.

Setiap metrik mode 0 adalah campuran regresi 26 koefisien dan polinomial 9
koefisien. Skala campurannya float32 `0x3e99999a`, bukan pecahan 0,3 yang pas.
Batas, tingkat, dan segmen mengikuti alur `bia_calc`.
"""

from __future__ import annotations

import base64
import math
import struct
import zlib
from dataclasses import dataclass
from decimal import Context, Decimal, localcontext

_FMA = Context(prec=80)
_IN = 0x60000
_OUT = 0x61000
_ENTRY = 0x6C9C
_OUT_SIZE = 0x3D0


def _fma(a: float, b: float, c: float) -> float:
    with localcontext(_FMA):
        wide = Decimal(a) * Decimal(b) + Decimal(c)
    return float(wide)


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _java_round(value: float) -> int:
    """`Math.round(float)`: lantai dari nilai ditambah 0,5 pada float32."""
    return math.floor(_f32(value + _f32(0.5)))


# offset, jenis, nama. Jenis d double, h int16, b uint8.
# Sama dengan salinan JNI ke `CSBiasDataVA019`.
_LAYOUT = (
    ("bfp", 0x0, "d"),
    ("bfp_normal_low", 0x8, "d"),
    ("bfp_normal_up", 0x10, "d"),
    ("bfp_overweight_up", 0x18, "d"),
    ("bfp_level", 0x20, "h"),
    ("bfm", 0x28, "d"),
    ("bfm_normal_low", 0x30, "d"),
    ("bfm_normal_up", 0x38, "d"),
    ("bfm_overweight_up", 0x40, "d"),
    ("bfm_level", 0x48, "h"),
    ("bwm", 0x50, "d"),
    ("bwm_normal_low", 0x58, "d"),
    ("bwm_normal_up", 0x60, "d"),
    ("bwm_level", 0x68, "h"),
    ("bwp", 0x70, "d"),
    ("bmc", 0x78, "d"),
    ("bmcp", 0x80, "d"),
    ("bmc_normal_low", 0x88, "d"),
    ("bmc_normal_up", 0x90, "d"),
    ("bmc_level", 0x98, "h"),
    ("minerals", 0xa0, "d"),
    ("minerals_normal_low", 0xa8, "d"),
    ("minerals_normal_up", 0xb0, "d"),
    ("minerals_level", 0xb8, "h"),
    ("pm", 0xc0, "d"),
    ("pm_normal_low", 0xc8, "d"),
    ("pm_normal_up", 0xd0, "d"),
    ("pm_level", 0xd8, "h"),
    ("pp", 0xe0, "d"),
    ("slm", 0xe8, "d"),
    ("slm_normal_low", 0xf0, "d"),
    ("slm_normal_up", 0xf8, "d"),
    ("slm_level", 0x100, "h"),
    ("ffm", 0x108, "d"),
    ("smm", 0x110, "d"),
    ("smm_normal_low", 0x118, "d"),
    ("smm_normal_up", 0x120, "d"),
    ("smm_level", 0x128, "h"),
    ("smi", 0x130, "d"),
    ("bmr", 0x138, "h"),
    ("bmr_normal_low", 0x13a, "h"),
    ("bmr_normal_up", 0x13c, "h"),
    ("bmr_level", 0x13e, "h"),
    ("vfl", 0x140, "h"),
    ("vfl_normal_low", 0x142, "h"),
    ("vfl_normal_up", 0x144, "h"),
    ("vfl_warning_up", 0x146, "h"),
    ("vfl_level", 0x148, "h"),
    ("metabolic_age", 0x14a, "b"),
    ("body_score", 0x14b, "b"),
    ("bmi", 0x150, "d"),
    ("bmi_normal_low", 0x158, "d"),
    ("bmi_normal_up", 0x160, "d"),
    ("bmi_overweight_up", 0x168, "d"),
    ("bmi_level", 0x170, "h"),
    ("body_type", 0x172, "h"),
    ("standard_weight", 0x178, "d"),
    ("weight_control", 0x180, "d"),
    ("muscle_control", 0x188, "d"),
    ("fat_control", 0x190, "d"),
    ("waist_circumference", 0x198, "d"),
    ("hip_circumference", 0x1a0, "d"),
    ("waist_hip_ratio", 0x1a8, "d"),
    ("la_slm", 0x1b0, "d"),
    ("la_slm_normal_low", 0x1b8, "d"),
    ("la_slm_normal_up", 0x1c0, "d"),
    ("ra_slm", 0x1c8, "d"),
    ("ra_slm_normal_low", 0x1d0, "d"),
    ("ra_slm_normal_up", 0x1d8, "d"),
    ("ll_slm", 0x1e0, "d"),
    ("ll_slm_normal_low", 0x1e8, "d"),
    ("ll_slm_normal_up", 0x1f0, "d"),
    ("rl_slm", 0x1f8, "d"),
    ("rl_slm_normal_low", 0x200, "d"),
    ("rl_slm_normal_up", 0x208, "d"),
    ("tr_slm", 0x210, "d"),
    ("tr_slm_normal_low", 0x218, "d"),
    ("tr_slm_normal_up", 0x220, "d"),
    ("la_slml", 0x228, "h"),
    ("ra_slml", 0x22a, "h"),
    ("ll_slml", 0x22c, "h"),
    ("rl_slml", 0x22e, "h"),
    ("tr_slml", 0x230, "h"),
    ("la_bfm", 0x238, "d"),
    ("la_bfm_normal_low", 0x240, "d"),
    ("la_bfm_normal_up", 0x248, "d"),
    ("ra_bfm", 0x250, "d"),
    ("ra_bfm_normal_low", 0x258, "d"),
    ("ra_bfm_normal_up", 0x260, "d"),
    ("ll_bfm", 0x268, "d"),
    ("ll_bfm_normal_low", 0x270, "d"),
    ("ll_bfm_normal_up", 0x278, "d"),
    ("rl_bfm", 0x280, "d"),
    ("rl_bfm_normal_low", 0x288, "d"),
    ("rl_bfm_normal_up", 0x290, "d"),
    ("tr_bfm", 0x298, "d"),
    ("tr_bfm_normal_low", 0x2a0, "d"),
    ("tr_bfm_normal_up", 0x2a8, "d"),
    ("la_bfml", 0x2b0, "h"),
    ("ra_bfml", 0x2b2, "h"),
    ("ll_bfml", 0x2b4, "h"),
    ("rl_bfml", 0x2b6, "h"),
    ("tr_bfml", 0x2b8, "h"),
    ("arm_muscle_even_level", 0x2ba, "b"),
    ("leg_muscle_even_level", 0x2bb, "b"),
    ("body_muscle_even_level", 0x2bc, "b"),
    ("arm_fat_even_level", 0x2bd, "b"),
    ("leg_fat_even_level", 0x2be, "b"),
    ("body_fat_even_level", 0x2bf, "b"),
    ("la_mass", 0x2c0, "d"),
    ("ra_mass", 0x2c8, "d"),
    ("ll_mass", 0x2d0, "d"),
    ("rl_mass", 0x2d8, "d"),
    ("tr_mass", 0x2e0, "d"),
    ("la_bfp", 0x2e8, "d"),
    ("ra_bfp", 0x2f0, "d"),
    ("ll_bfp", 0x2f8, "d"),
    ("rl_bfp", 0x300, "d"),
    ("tr_bfp", 0x308, "d"),
    ("la_slp", 0x310, "d"),
    ("ra_slp", 0x318, "d"),
    ("ll_slp", 0x320, "d"),
    ("rl_slp", 0x328, "d"),
    ("tr_slp", 0x330, "d"),
    ("slp", 0x338, "d"),
    ("icw", 0x340, "d"),
    ("standard_icw", 0x348, "d"),
    ("icw_normal_low", 0x350, "d"),
    ("icw_normal_up", 0x358, "d"),
    ("icw_level", 0x360, "h"),
    ("ecw", 0x368, "d"),
    ("standard_ecw", 0x370, "d"),
    ("ecw_normal_low", 0x378, "d"),
    ("ecw_normal_up", 0x380, "d"),
    ("ecw_level", 0x388, "h"),
    ("body_cell_mass", 0x390, "d"),
    ("standard_bcm", 0x398, "d"),
    ("bcm_normal_low", 0x3a0, "d"),
    ("bcm_normal_up", 0x3a8, "d"),
    ("bcm_level", 0x3b0, "h"),
    ("recommended_calorie_intake", 0x3b2, "h"),
    ("eee", 0x3b4, "h"),
    ("sfm", 0x3b8, "d"),
    ("sfp", 0x3c0, "d"),
    ("obesity_degree", 0x3c8, "d"),
)


@dataclass(frozen=True)
class BiasVA019Data:
    bfp: float
    bfp_normal_low: float
    bfp_normal_up: float
    bfp_overweight_up: float
    bfp_level: int
    bfm: float
    bfm_normal_low: float
    bfm_normal_up: float
    bfm_overweight_up: float
    bfm_level: int
    bwm: float
    bwm_normal_low: float
    bwm_normal_up: float
    bwm_level: int
    bwp: float
    bmc: float
    bmcp: float
    bmc_normal_low: float
    bmc_normal_up: float
    bmc_level: int
    minerals: float
    minerals_normal_low: float
    minerals_normal_up: float
    minerals_level: int
    pm: float
    pm_normal_low: float
    pm_normal_up: float
    pm_level: int
    pp: float
    slm: float
    slm_normal_low: float
    slm_normal_up: float
    slm_level: int
    ffm: float
    smm: float
    smm_normal_low: float
    smm_normal_up: float
    smm_level: int
    smi: float
    bmr: int
    bmr_normal_low: int
    bmr_normal_up: int
    bmr_level: int
    vfl: int
    vfl_normal_low: int
    vfl_normal_up: int
    vfl_warning_up: int
    vfl_level: int
    metabolic_age: int
    body_score: int
    bmi: float
    bmi_normal_low: float
    bmi_normal_up: float
    bmi_overweight_up: float
    bmi_level: int
    body_type: int
    standard_weight: float
    weight_control: float
    muscle_control: float
    fat_control: float
    waist_circumference: float
    hip_circumference: float
    waist_hip_ratio: float
    la_slm: float
    la_slm_normal_low: float
    la_slm_normal_up: float
    ra_slm: float
    ra_slm_normal_low: float
    ra_slm_normal_up: float
    ll_slm: float
    ll_slm_normal_low: float
    ll_slm_normal_up: float
    rl_slm: float
    rl_slm_normal_low: float
    rl_slm_normal_up: float
    tr_slm: float
    tr_slm_normal_low: float
    tr_slm_normal_up: float
    la_slml: int
    ra_slml: int
    ll_slml: int
    rl_slml: int
    tr_slml: int
    la_bfm: float
    la_bfm_normal_low: float
    la_bfm_normal_up: float
    ra_bfm: float
    ra_bfm_normal_low: float
    ra_bfm_normal_up: float
    ll_bfm: float
    ll_bfm_normal_low: float
    ll_bfm_normal_up: float
    rl_bfm: float
    rl_bfm_normal_low: float
    rl_bfm_normal_up: float
    tr_bfm: float
    tr_bfm_normal_low: float
    tr_bfm_normal_up: float
    la_bfml: int
    ra_bfml: int
    ll_bfml: int
    rl_bfml: int
    tr_bfml: int
    arm_muscle_even_level: int
    leg_muscle_even_level: int
    body_muscle_even_level: int
    arm_fat_even_level: int
    leg_fat_even_level: int
    body_fat_even_level: int
    la_mass: float
    ra_mass: float
    ll_mass: float
    rl_mass: float
    tr_mass: float
    la_bfp: float
    ra_bfp: float
    ll_bfp: float
    rl_bfp: float
    tr_bfp: float
    la_slp: float
    ra_slp: float
    ll_slp: float
    rl_slp: float
    tr_slp: float
    slp: float
    icw: float
    standard_icw: float
    icw_normal_low: float
    icw_normal_up: float
    icw_level: int
    ecw: float
    standard_ecw: float
    ecw_normal_low: float
    ecw_normal_up: float
    ecw_level: int
    body_cell_mass: float
    standard_bcm: float
    bcm_normal_low: float
    bcm_normal_up: float
    bcm_level: int
    recommended_calorie_intake: int
    eee: int
    sfm: float
    sfp: float
    obesity_degree: float


@dataclass(frozen=True)
class BiasVA019Result:
    result: int
    data: BiasVA019Data | None


@dataclass(frozen=True)
class MultiFrequencyReport:
    """Nilai yang disimpan `toParserMultiFrequencyData`."""

    bfp: float
    slm: float
    bwp: float
    bmc: float
    vfl: float
    pp: float
    smm: float
    swt: float
    mc: float
    wc: float
    fc: float
    whr: float
    wl: float
    hl: float
    bmr: int
    bt: int
    ma: int
    sbc: int
    slp: float
    bmcp: float
    bfm: float
    ffm: float
    bwm: float
    pm: float
    smi: float
    la_bfm: float
    la_slm: float
    ra_bfm: float
    ra_slm: float
    rl_bfm: float
    rl_slm: float
    ll_bfm: float
    ll_slm: float
    tr_bfm: float
    tr_slm: float
    sfm: float
    sfp: float
    icw: float
    ecw: float
    body_cell_mass: float
    obesity_degree: float


@dataclass(frozen=True)
class MultiFrequencyReportResult:
    result: int
    data: MultiFrequencyReport | None


def _decode(buf: bytes) -> BiasVA019Data:
    values = []
    for _name, off, kind in _LAYOUT:
        if kind == "d":
            values.append(struct.unpack_from("<d", buf, off)[0])
        elif kind == "h":
            values.append(struct.unpack_from("<h", buf, off)[0])
        else:
            values.append(buf[off])
    return BiasVA019Data(*values)


def _newton_sqrt(value: float) -> float:
    """Akar Newton di pembantu regresi. Tebakan awal separuh nilai, batas 1e-10."""
    eps = struct.unpack_from("<d", _program_image(), 0x1600)[0]
    guess = value * 0.5
    resid = _fma(guess, guess, -value)
    opposite = -_fma(guess, guess, -value)
    err = opposite if resid < 0.0 else resid
    if not (err > eps):
        return guess
    step = 0
    while True:
        guess = guess - (resid / (guess + guess))
        resid = _fma(guess, guess, -value)
        opposite = -_fma(guess, guess, -value)
        err = opposite if resid < 0.0 else resid
        if step > 99:
            break
        step += 1
        if not (err > eps):
            break
    return guess


def metric_regression(
    index: int,
    seed: float,
    sex: int,
    height_10: int,
    weight_10: int,
    impedance: list[int] | tuple[int, ...],
) -> float:
    """Satu metrik mode 0. `seed` pada `bia_calc` adalah BMI.

    Bagian akurat memakai tinggi, berat, jenis kelamin, sepuluh impedansi,
    dan akarnya. Polinomial pengulang hanya lima impedansi pertama.
    """
    if not 0 <= index < 20:
        raise ValueError("indeks metrik di luar 0–19")
    if len(impedance) != 10:
        raise ValueError("impedansi harus 10 nilai")
    image = _program_image()
    height = float(height_10) / 10.0
    weight = float(weight_10) / 10.0
    accurate = [
        struct.unpack_from("<d", image, 0x1730 + index * 0xD0 + 8 * i)[0] for i in range(26)
    ]
    repeat = [
        struct.unpack_from("<d", image, 0x2770 + index * 0x48 + 8 * i)[0] for i in range(9)
    ]
    sex_d = float(sex & 0xFF)
    zs = [float(z & 0xFFFF) / 10.0 for z in impedance]
    linear = _fma(accurate[0], height, weight * accurate[1])
    linear = _fma(sex_d, accurate[2], linear)
    for i in range(10):
        linear = _fma(accurate[3 + i], zs[i], linear)
    acc = _fma(accurate[13], _newton_sqrt(height), accurate[14] * _newton_sqrt(weight))
    acc = linear + acc
    for i in range(10):
        acc = _fma(accurate[15 + i], _newton_sqrt(zs[i]), acc)
    acc = acc + accurate[25]
    poly = _fma(repeat[0], height, repeat[1] * sex_d)
    poly = _fma(seed, repeat[2], poly)
    for i in range(5):
        poly = _fma(repeat[3 + i], zs[i], poly)
    poly = poly + repeat[8]
    scale = struct.unpack_from("<f", image, 0x135C0)[0]
    return _fma(scale, acc, (1.0 - scale) * poly)


def cs_bias_vA019(
    sex: int,
    age: int,
    height_10: int,
    weight_10: int,
    mode: int,
    impedance: list[int] | tuple[int, ...] | None,
) -> BiasVA019Result:
    """Hasil penuh `CSBiasDataVA019`. `impedance is None` mengembalikan kode 1."""
    if impedance is None:
        return BiasVA019Result(1, None)
    if len(impedance) != 10:
        raise ValueError("impedansi harus 10 nilai")
    code, raw = _execute(sex, age, height_10, weight_10, mode, impedance)
    if code != 0:
        return BiasVA019Result(code, None)
    return BiasVA019Result(0, _decode(raw))


def parse_multi_frequency(
    sex: int,
    age: int,
    height_cm: float,
    weight_kg: float,
    impedance_ohm: list[float] | tuple[float, ...],
) -> MultiFrequencyReportResult:
    """Jalan yang sama dengan `toParserMultiFrequencyData` sampai field laporan terisi.

    Tinggi dan berat dibulatkan seperti `Math.round` setelah dikali 10 pada
    float32. Impedansi dipotong ke int setelah dikali 10. Field yang di-cast
    `(float)` di Java disimpan sebagai float32. `sfm`, `sfp`, `icw`, `ecw`,
    massa sel, dan derajat obesitas tetap double.
    """
    if len(impedance_ohm) != 10:
        raise ValueError("impedansi harus 10 nilai")
    height_10 = _java_round(_f32(_f32(height_cm) * _f32(10.0)))
    weight_10 = _java_round(_f32(_f32(weight_kg) * _f32(10.0)))
    impedance = [
        math.trunc(_f32(_f32(ohm) * _f32(10.0))) for ohm in impedance_ohm
    ]
    native = cs_bias_vA019(sex, age, height_10, weight_10, 0, impedance)
    if native.result != 0 or native.data is None:
        return MultiFrequencyReportResult(native.result, None)
    data = native.data
    report = MultiFrequencyReport(
        bfp=_f32(data.bfp),
        slm=_f32(data.slm),
        bwp=_f32(data.bwp),
        bmc=_f32(data.bmc),
        vfl=_f32(float(data.vfl)),
        pp=_f32(data.pp),
        smm=_f32(data.smm),
        swt=_f32(data.standard_weight),
        mc=_f32(data.muscle_control),
        wc=_f32(data.weight_control),
        fc=_f32(data.fat_control),
        whr=_f32(data.waist_hip_ratio),
        wl=_f32(data.waist_circumference),
        hl=_f32(data.hip_circumference),
        bmr=data.bmr,
        bt=data.body_type,
        ma=data.metabolic_age,
        sbc=data.body_score,
        slp=_f32(data.slp),
        bmcp=_f32(data.bmcp),
        bfm=_f32(data.bfm),
        ffm=_f32(data.ffm),
        bwm=_f32(data.bwm),
        pm=_f32(data.pm),
        smi=_f32(data.smi),
        la_bfm=_f32(data.la_bfm),
        la_slm=_f32(data.la_slm),
        ra_bfm=_f32(data.ra_bfm),
        ra_slm=_f32(data.ra_slm),
        rl_bfm=_f32(data.rl_bfm),
        rl_slm=_f32(data.rl_slm),
        ll_bfm=_f32(data.ll_bfm),
        ll_slm=_f32(data.ll_slm),
        tr_bfm=_f32(data.tr_bfm),
        tr_slm=_f32(data.tr_slm),
        sfm=data.sfm,
        sfp=data.sfp,
        icw=data.icw,
        ecw=data.ecw,
        body_cell_mass=data.body_cell_mass,
        obesity_degree=data.obesity_degree,
    )
    return MultiFrequencyReportResult(0, report)


def _program_image() -> bytes:
    return _engine().base


def _execute(sex, age, height_10, weight_10, mode, impedance):
    raw = bytearray(32)
    raw[0] = mode & 0xFF
    struct.pack_into("<H", raw, 2, height_10 & 0xFFFF)
    struct.pack_into("<H", raw, 4, weight_10 & 0xFFFF)
    raw[6] = sex & 0xFF
    raw[7] = age & 0xFF
    for i, z in enumerate(impedance):
        struct.pack_into("<H", raw, 8 + 2 * i, z & 0xFFFF)
    eng = _engine()
    eng.reset_mem()
    eng.store(_IN, bytes(raw))
    eng.store(_OUT, b"\x00" * _OUT_SIZE)
    eng.sx("x0", _OUT)
    eng.sx("x1", _IN)
    eng.sx("x30", RET)
    eng.z = 1
    pc = _ENTRY
    steps = 0
    while pc != RET:
        pc = eng.step(pc)
        steps += 1
        if steps > 2_000_000:
            raise RuntimeError(f"batas langkah di {pc:#x}")
    code = eng.gx("x0") & 0xFFFFFFFF
    return code, bytes(eng.load(_OUT, _OUT_SIZE))


_ENGINE = None


def _engine():
    global _ENGINE
    if _ENGINE is None:
        _ENGINE = _Engine(*_load_program())
    return _ENGINE


def _load_program():
    raw = zlib.decompress(base64.b64decode(_PROGRAM))
    image_len = struct.unpack_from("<I", raw, 0)[0]
    image = raw[4 : 4 + image_len]
    pos = 4 + image_len
    count = struct.unpack_from("<I", raw, pos)[0]
    pos += 4
    insns = {}
    for _ in range(count):
        addr, nxt, mlen = struct.unpack_from("<IIB", raw, pos)
        pos += 9
        mnem = raw[pos : pos + mlen].decode()
        pos += mlen
        olen = struct.unpack_from("<H", raw, pos)[0]
        pos += 2
        ops = raw[pos : pos + olen].decode()
        pos += olen
        insns[addr] = (mnem, ops, nxt)
    return image, insns


_MASK64 = (1 << 64) - 1
_MASK32 = (1 << 32) - 1
RET = 0xFFFF_FFFF_FFFF_FFFF
TPIDR = 0x50000
STACK = 0x70000
MEM_SIZE = 0x80000

PLT = {
    0xB2F0: 0x5EC8,
    0xB300: 0x61F8,
    0xB310: 0x67CC,
    0xB320: 0x6A38,
}


_INVERT = {
    "eq": "ne",
    "ne": "eq",
    "hs": "lo",
    "cs": "cc",
    "lo": "hs",
    "cc": "cs",
    "mi": "pl",
    "pl": "mi",
    "vs": "vc",
    "vc": "vs",
    "hi": "ls",
    "ls": "hi",
    "ge": "lt",
    "lt": "ge",
    "gt": "le",
    "le": "gt",
}


def _cond(name: str, n: int, z: int, c: int, v: int) -> bool:
    if name == "eq":
        return z == 1
    if name == "ne":
        return z == 0
    if name in ("hs", "cs"):
        return c == 1
    if name in ("lo", "cc"):
        return c == 0
    if name == "mi":
        return n == 1
    if name == "pl":
        return n == 0
    if name == "vs":
        return v == 1
    if name == "vc":
        return v == 0
    if name == "hi":
        return c == 1 and z == 0
    if name == "ls":
        return c == 0 or z == 1
    if name == "ge":
        return n == v
    if name == "lt":
        return n != v
    if name == "gt":
        return z == 0 and n == v
    if name == "le":
        return z == 1 or n != v
    raise KeyError(name)


def _add_flags(a: int, b: int, bits: int) -> tuple[int, int, int, int, int]:
    mask = (1 << bits) - 1
    sign = 1 << (bits - 1)
    ua = a & mask
    ub = b & mask
    total = ua + ub
    carry = 1 if total > mask else 0
    result = total & mask
    negative = 1 if result & sign else 0
    zero = 1 if result == 0 else 0
    overflow = 1 if (~(ua ^ ub) & (ua ^ result) & sign) else 0
    return result, negative, zero, carry, overflow


def _sub_flags(a: int, b: int, bits: int) -> tuple[int, int, int, int, int]:
    mask = (1 << bits) - 1
    sign = 1 << (bits - 1)
    ua = a & mask
    ub = b & mask
    result = (ua - ub) & mask
    carry = 1 if ua >= ub else 0
    negative = 1 if result & sign else 0
    zero = 1 if result == 0 else 0
    overflow = 1 if ((ua ^ ub) & (ua ^ result) & sign) else 0
    return result, negative, zero, carry, overflow


def _signed(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    sign = 1 << (bits - 1)
    if value & sign:
        return value - (1 << bits)
    return value


def _asr(value: int, shift: int, bits: int) -> int:
    return _signed(value, bits) >> shift


def _fdiv(a: float, b: float) -> float:
    try:
        return a / b
    except ZeroDivisionError:
        if a == 0.0 or math.isnan(a):
            return math.nan
        return math.copysign(math.inf, a) * math.copysign(1.0, b)


def _fp_op(mnem: str, a: float, b: float) -> float:
    if mnem == "fadd":
        return a + b
    if mnem == "fsub":
        return a - b
    if mnem == "fmul":
        return a * b
    return _fdiv(a, b)


class _Engine:
    def __init__(self, image: bytes, insns: dict[int, tuple[str, str, int]]):
        self.base = image
        self.insns = insns
        self.mem = bytearray(MEM_SIZE)
        self.x = [0] * 32
        self.v = [bytearray(16) for _ in range(32)]
        self.sp = STACK
        self.n = self.z = self.c = self.vf = 0
        self.reset_mem()

    def load(self, addr: int, n: int) -> bytes:
        if addr < 0 or addr + n > MEM_SIZE:
            raise IndexError(hex(addr))
        return bytes(self.mem[addr : addr + n])

    def store(self, addr: int, data: bytes) -> None:
        end = addr + len(data)
        if addr < 0 or end > MEM_SIZE:
            raise IndexError(hex(addr))
        self.mem[addr:end] = data

    def reset_mem(self) -> None:
        self.mem[:] = b"\x00" * MEM_SIZE
        self.mem[: len(self.base)] = self.base
        self.mem[TPIDR + 0x28 : TPIDR + 0x30] = b"CANARY!!"
        self.x = [0] * 32
        self.v = [bytearray(16) for _ in range(32)]
        self.sp = STACK
        self.n = self.z = self.c = self.vf = 0

    def gx(self, name: str) -> int:
        if name in ("xzr", "wzr"):
            return 0
        if name == "sp":
            return self.sp & _MASK64
        n = int(name[1:])
        if name[0] == "w":
            return self.x[n] & _MASK32
        return self.x[n] & _MASK64

    def sx(self, name: str, value: int) -> None:
        if name in ("xzr", "wzr"):
            return
        if name == "sp":
            self.sp = value & _MASK64
            return
        n = int(name[1:])
        if name[0] == "w":
            self.x[n] = value & _MASK32
        else:
            self.x[n] = value & _MASK64

    def gd(self, i: int) -> float:
        return struct.unpack_from("<d", self.v[i])[0]

    def sd(self, i: int, value: float) -> None:
        self.v[i][:] = struct.pack("<d", float(value)) + b"\x00" * 8

    def sd_bits(self, i: int, bits: int) -> None:
        self.v[i][:] = struct.pack("<Q", bits & _MASK64) + b"\x00" * 8

    def gs(self, i: int) -> float:
        return struct.unpack_from("<f", self.v[i])[0]

    def ss(self, i: int, value: float) -> None:
        self.v[i][:] = struct.pack("<f", float(value)) + b"\x00" * 12

    def ss_bits(self, i: int, bits: int) -> None:
        self.v[i][:] = struct.pack("<I", bits & _MASK32) + b"\x00" * 12

    def gq(self, i: int) -> bytes:
        return bytes(self.v[i])

    def sq(self, i: int, data: bytes) -> None:
        self.v[i][:] = data

    def _vidx(self, name: str) -> int:
        return int(name[1:])

    def _ok(self, cond: str) -> bool:
        return _cond(cond, self.n, self.z, self.c, self.vf)

    def _flags_from(self, result, negative, zero, carry, overflow) -> int:
        self.n, self.z, self.c, self.vf = negative, zero, carry, overflow
        return result

    def _fcmp(self, a: float, b: float) -> None:
        if math.isnan(a) or math.isnan(b):
            self.n, self.z, self.c, self.vf = 0, 0, 1, 1
        elif a == b:
            self.n, self.z, self.c, self.vf = 0, 1, 1, 0
        elif a < b:
            self.n, self.z, self.c, self.vf = 1, 0, 0, 0
        else:
            self.n, self.z, self.c, self.vf = 0, 0, 1, 0

    def _addr(self, operand: str) -> tuple[int, str | None, int]:
        """Return address, optional writeback register, and writeback delta.

        Writeback is applied by the caller after the access for post-index,
        and the returned address is already the access address for pre-index.
        The third value is the post-index delta (0 if none). Pre-index updates
        the base before return and reports delta 0.
        """
        body = operand[operand.index("[") + 1 : operand.index("]")]
        post = operand.endswith("]") is False and "]," in operand.replace(" ", "")
        # re-evaluate post/pre from the raw text
        pre = operand.endswith("!")
        post = "]," in operand
        parts = [p.strip() for p in body.split(",")]
        base_name = parts[0]
        base = self.gx(base_name)
        offset = 0
        if len(parts) == 2 and parts[1].startswith("#"):
            offset = int(parts[1][1:], 0)
        elif len(parts) >= 2:
            index_tok = parts[1]
            shift = 0
            if len(parts) == 3:
                shift_tok = parts[2]
                if shift_tok.startswith("lsl"):
                    shift = int(shift_tok.split("#")[1], 0)
                elif "uxtw" in shift_tok:
                    shift = int(shift_tok.split("#")[1], 0)
                    index_tok = "w" + index_tok[1:] if index_tok[0] == "x" else index_tok
                else:
                    raise NotImplementedError(operand)
            if "uxtw" in operand and len(parts) == 3:
                index = self.gx("w" + parts[1][1:]) if parts[1][0] in "xw" else self.gx(parts[1])
                offset = (index & _MASK32) << shift
            else:
                offset = (self.gx(parts[1]) << shift) & _MASK64
        if pre:
            base = (base + offset) & _MASK64
            self.sx(base_name, base)
            return base, None, 0
        if post:
            delta = int(operand.split("#")[-1].rstrip("]").strip(), 0)
            # operand like [x14], #0x2
            delta = int(operand[operand.rindex("#") + 1 :], 0)
            return base, base_name, delta
        return (base + offset) & _MASK64, None, 0

    def _access(self, operand: str) -> tuple[int, str | None, int]:
        addr, reg, delta = self._addr(operand)
        return addr, reg, delta

    def _finish_wb(self, reg: str | None, delta: int) -> None:
        if reg is not None:
            self.sx(reg, (self.gx(reg) + delta) & _MASK64)

    def _load_reg(self, name: str, addr: int) -> None:
        kind = name[0]
        idx = self._vidx(name) if kind in "dshqb" else None
        if kind == "x":
            self.sx(name, struct.unpack("<Q", self.load(addr, 8))[0])
        elif kind == "w":
            self.sx(name, struct.unpack("<I", self.load(addr, 4))[0])
        elif name.startswith("d"):
            self.v[idx][:] = self.load(addr, 8) + b"\x00" * 8
        elif name.startswith("s"):
            self.v[idx][:] = self.load(addr, 4) + b"\x00" * 12
        elif name.startswith("h"):
            self.v[idx][:] = self.load(addr, 2) + b"\x00" * 14
        elif name.startswith("b"):
            self.v[idx][:] = self.load(addr, 1) + b"\x00" * 15
        elif name.startswith("q"):
            self.v[idx][:] = self.load(addr, 16)
        else:
            raise NotImplementedError(name)

    def _store_reg(self, name: str, addr: int) -> None:
        kind = name[0]
        if kind == "x" or name == "sp":
            self.store(addr, struct.pack("<Q", self.gx(name)))
        elif kind == "w":
            self.store(addr, struct.pack("<I", self.gx(name)))
        elif name.startswith("d"):
            self.store(addr, bytes(self.v[self._vidx(name)][:8]))
        elif name.startswith("s"):
            self.store(addr, bytes(self.v[self._vidx(name)][:4]))
        elif name.startswith("h"):
            self.store(addr, bytes(self.v[self._vidx(name)][:2]))
        elif name.startswith("b"):
            self.store(addr, bytes(self.v[self._vidx(name)][:1]))
        elif name.startswith("q"):
            self.store(addr, self.gq(self._vidx(name)))
        else:
            raise NotImplementedError(name)

    def _pair_size(self, name: str) -> int:
        if name[0] in "xw" or name == "sp":
            return 8 if name[0] != "w" else 4
        if name[0] == "d":
            return 8
        if name[0] == "s":
            return 4
        if name[0] == "q":
            return 16
        raise NotImplementedError(name)

    def step(self, pc: int) -> int:
        mnem, ops, nxt = self.insns[pc]
        if mnem == "nop":
            return nxt
        if mnem == "ret":
            return self.gx("x30")
        if mnem == "b":
            return int(ops, 16)
        if mnem.startswith("b."):
            return int(ops, 16) if self._ok(mnem[2:]) else nxt
        if mnem == "bl":
            target = int(ops, 16)
            self.sx("x30", nxt)
            if target == 0xB2B0:
                dest = self.gx("x0")
                val = self.gx("w1") & 0xFF
                size = self.gx("x2")
                self.store(dest, bytes([val]) * size)
                return nxt
            if target == 0xB2E0:
                raise RuntimeError("stack check")
            return PLT.get(target, target)
        if mnem == "cbz":
            reg, target = [p.strip() for p in ops.split(",")]
            return int(target, 16) if self.gx(reg) == 0 else nxt
        if mnem == "cbnz":
            reg, target = [p.strip() for p in ops.split(",")]
            return int(target, 16) if self.gx(reg) != 0 else nxt
        if mnem == "mrs":
            self.sx(ops.split(",")[0].strip(), TPIDR)
            return nxt
        if mnem in ("adrp", "adr"):
            reg, imm = [p.strip() for p in ops.split(",")]
            self.sx(reg, int(imm, 16))
            return nxt
        if mnem == "mov":
            dst, src = [p.strip() for p in ops.split(",")]
            if src.startswith("#"):
                self.sx(dst, int(src[1:], 0))
            else:
                self.sx(dst, self.gx(src))
            return nxt
        if mnem == "movk":
            dst, imm, *rest = [p.strip() for p in ops.split(",")]
            shift = int(rest[0].split("#")[1], 0) if rest else 0
            mask = 0xFFFF << shift
            cur = self.gx(dst)
            bits = 64 if dst[0] == "x" else 32
            cur = (cur & ~mask) | ((int(imm[1:], 0) << shift) & mask)
            self.sx(dst, cur & ((1 << bits) - 1))
            return nxt
        if mnem == "movi":
            dst = ops.split(",")[0].strip()
            self.sd(self._vidx(dst), 0.0)
            return nxt
        if mnem == "fmov":
            dst, src = [p.strip() for p in ops.split(",")]
            if dst[0] == "d" and src.startswith("#"):
                self.sd(self._vidx(dst), float(src[1:]))
            elif dst[0] == "s" and src.startswith("#"):
                self.ss(self._vidx(dst), float(src[1:]))
            elif dst[0] == "d" and src[0] == "d":
                self.sd(self._vidx(dst), self.gd(self._vidx(src)))
            elif dst[0] == "d" and src[0] == "x":
                self.sd_bits(self._vidx(dst), self.gx(src))
            elif dst[0] == "s" and src[0] == "w":
                self.ss_bits(self._vidx(dst), self.gx(src))
            else:
                raise NotImplementedError(ops)
            return nxt
        if mnem in ("add", "sub", "subs", "cmp", "cmn"):
            return self._arith(mnem, ops, nxt)
        if mnem in ("lsl", "lsr", "asr"):
            dst, src, sh = [p.strip() for p in ops.split(",")]
            shift = int(sh[1:], 0)
            bits = 32 if dst[0] == "w" else 64
            value = self.gx(src)
            if mnem == "lsl":
                value = (value << shift) & ((1 << bits) - 1)
            elif mnem == "lsr":
                value = (value & ((1 << bits) - 1)) >> shift
            else:
                value = _asr(value, shift, bits) & ((1 << bits) - 1)
            self.sx(dst, value)
            return nxt
        if mnem == "and":
            dst, a, b = [p.strip() for p in ops.split(",")]
            self.sx(dst, self.gx(a) & int(b[1:], 0))
            return nxt
        if mnem == "smull":
            dst, a, b = [p.strip() for p in ops.split(",")]
            self.sx(dst, (_signed(self.gx(a), 32) * _signed(self.gx(b), 32)) & _MASK64)
            return nxt
        if mnem == "umaddl":
            dst, a, b, c = [p.strip() for p in ops.split(",")]
            prod = (self.gx(a) & _MASK32) * (self.gx(b) & _MASK32)
            self.sx(dst, (prod + self.gx(c)) & _MASK64)
            return nxt
        if mnem == "ubfiz":
            dst, src, lsb, width = [p.strip() for p in ops.split(",")]
            lsb_i = int(lsb[1:], 0)
            width_i = int(width[1:], 0)
            self.sx(dst, ((self.gx(src) & ((1 << width_i) - 1)) << lsb_i) & _MASK64)
            return nxt
        if mnem in ("csel", "csinc", "csinv", "cinc", "cset", "csetm", "cneg"):
            return self._condmov(mnem, ops, nxt)
        if mnem in ("fadd", "fsub", "fmul", "fdiv", "fneg"):
            return self._fp(mnem, ops, nxt)
        if mnem in ("fmadd", "fnmadd", "fnmsub"):
            dst, n, m, a = [p.strip() for p in ops.split(",")]
            nv, mv, av = self.gd(self._vidx(n)), self.gd(self._vidx(m)), self.gd(self._vidx(a))
            if mnem == "fmadd":
                result = _fma(nv, mv, av)
            elif mnem == "fnmsub":
                result = _fma(nv, mv, -av)
            else:
                result = -_fma(nv, mv, av)
            self.sd(self._vidx(dst), result)
            return nxt
        if mnem == "fcmp":
            a, b = [p.strip() for p in ops.split(",")]
            av = self.gs(self._vidx(a)) if a[0] == "s" else self.gd(self._vidx(a))
            if b.startswith("#"):
                bv = float(b[1:])
            else:
                bv = self.gs(self._vidx(b)) if b[0] == "s" else self.gd(self._vidx(b))
            self._fcmp(av, bv)
            return nxt
        if mnem == "fcsel":
            dst, a, b, cond = [p.strip() for p in ops.split(",")]
            pick = a if self._ok(cond) else b
            if dst[0] == "s":
                self.ss(self._vidx(dst), self.gs(self._vidx(pick)))
            else:
                self.sd(self._vidx(dst), self.gd(self._vidx(pick)))
            return nxt
        if mnem == "fcvt":
            dst, src = [p.strip() for p in ops.split(",")]
            if dst[0] == "d":
                self.sd(self._vidx(dst), self.gs(self._vidx(src)))
            else:
                self.ss(self._vidx(dst), self.gd(self._vidx(src)))
            return nxt
        if mnem == "scvtf":
            dst, src = [p.strip() for p in ops.split(",")]
            value = float(_signed(self.gx(src), 32 if src[0] == "w" else 64))
            if dst[0] == "s":
                self.ss(self._vidx(dst), value)
            else:
                self.sd(self._vidx(dst), value)
            return nxt
        if mnem == "ucvtf":
            dst, src = [p.strip() for p in ops.split(",")]
            if src[0] in "wd":
                if src[0] == "w":
                    self.sd(self._vidx(dst), float(self.gx(src) & _MASK32))
                else:
                    bits = struct.unpack_from("<Q", self.v[self._vidx(src)])[0]
                    self.sd(self._vidx(dst), float(bits))
            else:
                raise NotImplementedError(ops)
            return nxt
        if mnem == "fcvtzs":
            dst, src = [p.strip() for p in ops.split(",")]
            value = self.gd(self._vidx(src)) if src[0] == "d" else self.gs(self._vidx(src))
            bits = 32 if dst[0] == "w" else 64
            limit = (1 << (bits - 1)) - 1
            if math.isnan(value):
                converted = 0
            elif value >= limit:
                converted = limit
            elif value <= -limit - 1:
                converted = -limit - 1
            else:
                converted = math.trunc(value)
            self.sx(dst, converted & ((1 << bits) - 1))
            return nxt
        if mnem == "frintp":
            dst, src = [p.strip() for p in ops.split(",")]
            value = self.gd(self._vidx(src))
            if math.isnan(value) or math.isinf(value):
                rounded = value
            else:
                rounded = float(math.ceil(value))
            self.sd(self._vidx(dst), rounded)
            return nxt
        if mnem == "dup":
            dst, src = [p.strip() for p in ops.split(",")]
            raw = struct.pack("<Q", self.gx(src))
            self.sq(self._vidx(dst.split(".")[0].replace("v", "q")), raw + raw)
            return nxt
        if mnem in ("ldr", "ldrb", "ldrh", "ldrsh", "ldur"):
            dst, memop = ops.split(",", 1)
            dst = dst.strip()
            addr, reg, delta = self._access(memop.strip())
            if mnem == "ldrsh":
                self.sx(dst, _signed(struct.unpack("<H", self.load(addr, 2))[0], 16))
            elif mnem == "ldrh":
                self.sx(dst, struct.unpack("<H", self.load(addr, 2))[0])
            elif mnem == "ldrb":
                self.sx(dst, self.load(addr, 1)[0])
            else:
                self._load_reg(dst, addr)
            self._finish_wb(reg, delta)
            return nxt
        if mnem in ("str", "strh", "strb", "stur"):
            src, memop = ops.split(",", 1)
            src = src.strip()
            addr, reg, delta = self._access(memop.strip())
            if mnem == "strh":
                self.store(addr, struct.pack("<H", self.gx(src) & 0xFFFF))
            elif mnem == "strb":
                self.store(addr, bytes([self.gx(src) & 0xFF]))
            else:
                self._store_reg(src, addr)
            self._finish_wb(reg, delta)
            return nxt
        if mnem in ("ldp", "stp"):
            a, b, memop = [p.strip() for p in ops.split(",", 2)]
            size = self._pair_size(a)
            addr, reg, delta = self._access(memop)
            if mnem == "ldp":
                self._load_reg(a, addr)
                self._load_reg(b, addr + size)
            else:
                self._store_reg(a, addr)
                self._store_reg(b, addr + size)
            self._finish_wb(reg, delta)
            return nxt
        raise NotImplementedError(hex(pc) + " " + mnem + " " + ops)

    def _arith(self, mnem: str, ops: str, nxt: int) -> int:
        parts = [p.strip() for p in ops.split(",")]
        if mnem in ("cmp", "cmn"):
            a, b = parts[0], ",".join(parts[1:])
            dst = None
        else:
            dst, a, b = parts[0], parts[1], ",".join(parts[2:])
        bits = 32 if a[0] == "w" else 64
        av = self.gx(a)
        shift = 0
        if "lsl #" in b:
            reg, sh = [p.strip() for p in b.split(",")]
            shift = int(sh.split("#")[1], 0)
            bv = (self.gx(reg) & ((1 << bits) - 1)) << shift
        elif b.startswith("#"):
            bv = int(b[1:], 0)
        else:
            bv = self.gx(b)
        if mnem in ("add",):
            result = (av + bv) & ((1 << bits) - 1)
            self.sx(dst, result)
            return nxt
        if mnem == "sub":
            self.sx(dst, (av - bv) & ((1 << bits) - 1))
            return nxt
        if mnem in ("subs", "cmp"):
            result, n, z, c, v = _sub_flags(av, bv, bits)
            self._flags_from(result, n, z, c, v)
            if dst is not None:
                self.sx(dst, result)
            return nxt
        result, n, z, c, v = _add_flags(av, bv, bits)
        self._flags_from(result, n, z, c, v)
        return nxt

    def _condmov(self, mnem: str, ops: str, nxt: int) -> int:
        parts = [p.strip() for p in ops.split(",")]
        if mnem == "cset":
            dst, cond = parts
            value = 1 if self._ok(cond) else 0
            self.sx(dst, value)
            return nxt
        if mnem == "csetm":
            dst, cond = parts
            bits = 32 if dst[0] == "w" else 64
            value = ((1 << bits) - 1) if self._ok(cond) else 0
            self.sx(dst, value)
            return nxt
        if mnem == "cneg":
            dst, src, cond = parts
            bits = 32 if dst[0] == "w" else 64
            value = self.gx(src)
            if self._ok(cond):
                value = (-_signed(value, bits)) & ((1 << bits) - 1)
            self.sx(dst, value)
            return nxt
        if mnem == "cinc":
            dst, src, cond = parts
            parts = [dst, src, src, _INVERT[cond]]
            mnem = "csinc"
        dst, a, b, cond = parts
        bits = 32 if dst[0] == "w" else 64
        mask = (1 << bits) - 1
        if self._ok(cond):
            value = self.gx(a)
        elif mnem == "csel":
            value = self.gx(b)
        elif mnem == "csinc":
            value = (self.gx(b) + 1) & mask
        else:
            value = (~self.gx(b)) & mask
        self.sx(dst, value & mask)
        return nxt

    def _fp(self, mnem: str, ops: str, nxt: int) -> int:
        parts = [p.strip() for p in ops.split(",")]
        if mnem == "fneg":
            dst, src = parts
            self.sd(self._vidx(dst), -self.gd(self._vidx(src)))
            return nxt
        dst, a, b = parts
        if dst[0] == "s":
            av = self.gs(self._vidx(a))
            bv = self.gs(self._vidx(b))
            self.ss(self._vidx(dst), _fp_op(mnem, av, bv))
            return nxt
        av = self.gd(self._vidx(a))
        bv = self.gd(self._vidx(b))
        self.sd(self._vidx(dst), _fp_op(mnem, av, bv))
        return nxt


_PROGRAM = """
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
yuG+5dmZ2XbtlPazEreMLr5OW9KHGfPWz3N3WsYrHvc183heiOF2SkruvuWnaXW3WwPntTtHn30Wta916D3a513tFnLPe/QSp0Xu
SypX0p/3HNjxlZ3rmP+t/ePjvIB5dFGobGmzduto96KP70xRFTKbl6zY22JACcN++stlw6v7GI/sB4YfIlYwm6qqvqlIXs8Yx12o
zYv7dK2D4Z/Oj37HYYX2o3LGEt75Zps+n5vRQhn9IxV899Iqusf3bdLWTypq1A49DvRL/emsupav88S0pu6vaWvx1SeznNff7suE
LF3o6LppMfPqyaSJE18bwvQ9eCrL6VYKQ/wfl8zrA3sunPSYWaT7u3Vv6kNa9b1dwjc7FzWqz+R7r7w/XT+2Vq6ZLh7fHRmrrsXP
WtKN+qTAi3kWWvXZqsL5TJvqkW39v3yDGXNxpcSuZ+L/uT4122deedTpETNm490NRQUnaV/F/TkuTifpmTNfV51Ju0f37P5KSPqN
mbQ66sfvR+9ZQX/eZZxhj20+88mgH5YbJr5P9zzz86/uBSX0t7Il8+8PXMr0Hfn1pqDeG5j3Aqa2LuvyDbNje+v5Ya3WMhu+ev2z
q9M21eqzN2N6iZ+MMLxsfS4tnOC96gcbQ+EXPw6R5x1nio6NC6M+P0P3OvvZitTU35kO5368vHtCIXPJ8dDpzV021Mojj9idM/7k
KiY8qWnrh9NKmV6Hnnww1ucD+tLurbuPxZTQgX+OYg/QX9ORj/b5fMmW0N5BoYc7PN1WO4/bFv6vj9r9Pv1P5fzFdat/jxGfW8T/
yzf9uMMFuVKS0mPf37fOMAlHv0oaVnWX9nv74C+xG+8y9L0do3K3FDNHXCMX7R+4nVnkd231xNbr6LTF49wdx7zFvFs21ubBlM2M
/NVemcpf5tHbcp9kp3feSJ94PGH3lQmH6E0Mudnn/k46UilZb79oT608d9Vbb1Y3L/nH+typmLy85D3GIv7uroN/jescpTy9hInf
epthUpXV03I/OEuHz0k6dvGTn5gRzWtkmzvPpP1++iVHcrSAdk2NIjppJtJfKqj88XGFtDZ7wg8O2xfTdp3+mvLzjneYi9+V7am6
llo7br9t8vkxi9Yx73/5w5nosx/Vzu9PuXtDm3RuqnzZ/qZ792HwtMHRyg33bo1YO2ADs/lo+N3vJ2+mfye32fSc+iVzYMWjKs3j
IuaLec/Ky5bm1MoTS40q/+1ZGrMvf6p/+roJzNAag8cjx0l0ry9jl5HDJ9Kvl8QdSGu6kN5Qs3j0360m0k1buP3R7vdMumtkwl+t
M2bTRQuHVNmdOUNnZHjJN9tfsWj39+fHMusNS+jFXzmt8H6rsFH8+c5eHbb90cqwbt7Aux9Xr2fmT5/RZnbZFrrj6UOX7QftZnLp
soB3PytiRuvP+V/PyGQWeg9f3ybtk9eo0bkeh++PZ+KbNVt82WsS89G9YzW/a7LpUXOazvCZMYkediFjZTW1iO56yZVe1G0yPeXO
h+3PfZJdK0fx5IDovTan6b53v/DRb660qM/fj36emzQqhR7o1Hf7/+6UNorf6fuC7FZZLQ3Mwr+cLjb5lflllGP38AfHaL9b9j/u
3VLBJNtdHn730FfMlfe9WiV/P5v5Mnbe4sud9zHDJEf6uNpvZC5lHD2im7mWmdhkjdtry9bSw7r9L2TtmuV0yBPV1WXSL5j9c2bl
ZI6dzdzxGPZ27xPv09GdfpUtWdRCmaTatbycdlGufm1/63lT5cruP179vtezY0zy36qsOa2e0J+O6pzQ9ItrtXI/mxywTmqzn5FG
DX8945U+9K5p3ZSDD/xN3yp8vFK/5gk98sb5j0oyL9H7F8gG/JU90rD2UPvPjl7cxUwMTk/at3MSHd00sVn3j/YwqiaP3w6A9f3W
+ZK4WbIkpkY+fc3pSzPoi7+26/115QRGcn7Dzz+E6pm1Xf/q6Ls3g/Y+uiS6251J9E+L7ZPj3l9B9yn0depycDKdmD7nYcxvOfQJ
w9vX/yo7Rx92Odnm2si/6QnvpIe263bH4vzcVm+q2rR2G33/QlXNsTWbGsV/0vn7/s4DuhpCf1o5tezm58z2YfZf3Bg0lv41/lzG
oDu7mfLJJwd/vWcFM/OW89CdQUnMtYiqIbaJM+m07EWGnGkTmN1ucW85HdIzM7sSv7QuyaD3Oh6ht7w/ifZ7Y92T0xNW0B1faXrk
rkZPN3svtatPcA7dduj0c3HSU/TMkrgj7f2q6V8+nPyk2XHL+iwO2tY/r9sO+sMezdov3b65UfwzX24IOOfd1XCu96A1E9lCWmHz
i7fa6fl4a/nq0BuXDqtq4RFJKxymdYmk9dGGX5qfV9NtJE+zVydOYgrvf+f6TDKW+cGd+nLWd+r/8/1A/TKn5br2K9Z+T+t/7Lek
ebci+uiMZ82GSwot2uvK++Edou8PoA+uufaWe7t4unTwxcDwpCHME1lvdtHAScy8wwW/evbQ/r+uz+Te4T9+vf1TutfxXeHEoAM0
PbjJay7X99Je338S5/zxz/TD4QsNeZvH02rvTYXFkmX0F3c/euYyMouZ1/m1zLemvkePmN7v2eYvltKLKg/OnNFrGRNHO1z84Ow6
ZtXKxMoJYzcwy3YvL13YJI9ZFNBx+6QW7/6f6/co5NiFk8VNDIfWfDZuostX9I97FKf6fDufdh9oeHY+dy+tLpv40bo3UujRHcvb
TH9vxnPzdvDcaqr3mDz6k2Nfz7xaMZG53Ouj2Q/nFdTK/dgzftgbW/SM9MIbrcp+mP1/rs/aoncuR21pbZj/zXxVFugzaXA3Q0nS
PHo3+YA602M3vTp3ybi3ssbRyn4HHvfbkFerz5klC7JsK1NoaeHEFVd+nEgvynzdca/jZGZNL7vTg07l18pt02H72Fw2k9lraBb0
e7MF/+f6OJe1y+5zsbXh/Yq+xXlkBT30lQvVH/9vZ63c+k9d/6BKCugbl/Yvv/94MX1v8cSctqElzM7YPrvPDt5IvzXxyrO1K0vo
ptdTHl1ospyJS1eerclazQz7Kv/m1HcZpmzf67953Cxheu3N9WldWPp/rs+Tdx9rNa93M8SVfNjh0aQvmaLqziXN+7saFH+e6XrM
RqLM+/Q68feRJXT447duypsvox8vuTDwhz776T/SJ6nKm+fT7R/4/PDuwny6aMYPhSpSaUiK6FLRxaOY/nJu6+53fJ8wN2rcrxU/
raFlTX6x+yhiLq2aKVvcq988uvmpiZKW0Z/SPudnnW6imETviCnp+NBxMl1+Yaf856ZRBt+7k/eNLzxPL5/SZvKIMFvlhYM7Ox78
4yfaeYF9QZpfHjNu4R3fx7/OYPI3F3Z+1GUbI9/YZUk8k8I0/3Ng+clZaUz/wzUjqtnehle+MVx+en5D7fzkSDP1J3w30t3fdfm+
Z5dwJviP2JWTukQy27pIBlyKn8y0M7x6I08WwtxUfv1syqMg5uTKqGcrHRwMSTd+Dp5XXFzL587piac6DId9+Y1Jqy4uC2Fyfrjf
tPmuMMbtwz5uH/6dw7RIdr16/I1uTMrj1avstnZl7oRv61dy094wd3LTisiw0/TR1cF/b9oqUbb8IPYdTcJ5Wtkn/UJJ9TvMuCtZ
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
37CXw++6PcH6Qg4cgnwFXr4vyIvjISXY68Cvq3udbPaKf2b/phqSbYhvtDAHyKOJ+7/PEf2AfivQfyuKgVuiXNNES7L/lNfrAi+t
oBPG1TERL+SNvBxSgee/4Ce291G3upiS64CPBR59yef3coyIhyzLMg9cfwY0sC+ZhnwEPTwmkuw/yeUzZA3kCcEuyGuMsL9sp/9n
/PYrzPN7q95+te20hv2olp+FNWA08BPL1WYGyTbGa50F2ZDf2/X41eflPgu/YRdsJ/9n69Mot4bf01Bz63ip5P98rRvUwF6zdp1f
p2JbLyT/0z5uAK7NRn4lKtax6L/xGynmV8qvd4r3SVbsv/XnwRy/EWJ+O3h+bitenN9wMb8veH6t1r04v2Fifl/x/FqWvDi/WDG/
fTy/FqUvzm+omN9+np/rjhfnFyPmd4zn1/yLF+c3RMzvBM+v2Vcvzi9azO8Uzw+/HX5Rfv1E/Jz3m/L5x2sT8Fg/e7KOlBM68qyK
Xb94ks7+GB9nUjmpW794og5lks6VwP0EnXSuVFebx5Zm6zZIY6ulLra6DflDq3F8MpBg++LedH6WziiLVG6vWzc/U4cy2Z3g1zgb
uUy3XhpdTfYn2Mpfldxac3XxaJ3EFs6pP6tMcjwnyyiCy6eXnUbpxPKjbDZNHHVXTitZSSrBXm4+Uid1aaqTrKnLaZVOI3S2p0hW
auukq3QarosU9uLSWc66Kw7DauWUrABZHGJ1RttJ57royFKEDdWhfJJZLXRkJS/bZacYHcrn1cC7b+kXBIuySfaBPE5DdFK5m84b
5LwyW8lW5itZm7MoS2vdlelKbg+Oa+jlKUpWKnfXXXYarONkk7fRXc5Qsj64P09TsrUy2rbVVToMqpVRYtsO2gN5+WwpXeUIsMO1
OvuRT0H+oUo2XJCTZKH9ptJkbSJJkq0cCDj4fAfkJm2h3U/JknKoI6BuAjUN8v1MwlmYZP+Y/bqObEfWyR6kZJ28SFbSgWQvv6pk
+2N+Brkl/tDuDPK8ArWvku0MOvijDiDFZR8l60+C/N3h3gPu5XIHSRjct4F71KUP3LdSgh7ygZ0FP+gC8kpUAG+uZFM/neuOskv6
QttJyc7dP9dd0h/uHZTctzeX7aEeArUU5K/E3z6SrDfIqwS58DdPMu7vJLzF/b090paIrZEqih6+2b/08Yio0idx/Ur/Sn69tDqj
byk7JbL0hk+E7lbncN2dIJXuj17H0/HvNAyWEN3jyCZppISIvU0S3Wm4X4ff2kpdt669rwjr9WdNq08APp1smqYB+Bsk4jdNI404
zxRhMuE7Le47IKDp+if/WwOuDf34rcxYgDUhG/8bOeK/JbEffxeA/66u9O9ok7//QwD9QSnQNy1l86UcPX7bjjxK8z2e+NsY9J0I
ZRj3ewEZfmcSz/3eK8EN94hEMH6z5Yb/xqh7XkxngtiZVsL/zQR5l9JVA8m8GG+Xvjs6BBr6+LYO33EtKK/P5ea2O7xdInZcbyPZ
cbm5dEcHeeSOaw42AFNCm9jRvoVqh78nUXS1FbkD5lh3FeZMi7+PclP26euq8jhwQfNuX9dIDxwbv8FygrGn2xJZ+PuG21KiSDdr
rfsCDVH0u1S+9Q9pk63lHZS5f9gS92bPUlbbSRKow26J1DXX1z1UNTWx9s7pVIBSQ22vqbn7O9B2lCVTpwqSPA4pkzz8vNXUkkFZ
VAEZwW5vQrgovROpEzA/f8CYFX5JVKB7NnU4NIs6pXzdo0LAjxmcRdUsJLPm4Lf7gA/jumx/VhObDHyzYJxPXAiX8lEZ1fcXJHtc
iUz2iAKahEHZlNozkTo4Kr0a+eO3ag/8kqkY9xzqemg2dT+yn8cDATdncDa1VuCvBv4LBP72imT8nUXhjhaES0Lb1z02+CVQCpII
vgE6KWr+qPDU66rxu3T8/Z/aT00NBZvh3wzC3/Og7X6XemwdB3a7Bfj4W5LvySbzT9oSRZn6jOpfScUtadN+HkopEeurHz/1Otj/
npuW8lUkUQHhGureoWSP+8rkWv1R7yYgE9rpPuiBdroOdrqn7GeCh3Y6Wl1jYqfLNTWt2jsrp6FscjnnT4UdXZXTfN2U0wpg3IC2
ymlppXX+dRhgW0mFA8qNcjn/qHk3e9S46gKQL/AN5Y57bxI7HvZT6rwV8VSgp3JaIPTPUKg8DkP/dbic3bWUN1zX+ql0hE1fD09J
pIeXC/ifl/JpZXNyR2WrcN0NH+KpHPzYk3jdo7J5hK6Y6OfhSUR7zCDCPdR+2dRNGDt/f9994frUahkXM3V/pxO/q8K/WeTlF0/N
DMW/p6mh1DZKD3bK4FKIOS7+2kH83Z3ClAaAri5fhj91Xt+iyFPicQ51NF5c39fQd4Dv49r/g/ZlUfsAtCUt69qHoe0tah+Hdrio
fRLa8aJ2BbRnitrnUBZR+0ccX9T+Bcfn24S1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1
WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1WIu1/H9eAh7w9bIQvp4q1KTQv0di2t5Wr32gXvu40G4q
tE8LbUpoy4T675qaDDGdvVBHOZjipQgIcqHtJtRPBXqp0G4l1Dsd+VoYlrgr1Ea8kY/42rXeuHZC/UQgdKg3nq1QjxEEUwjt2wL+
o2e8PLkCIxuhf5AwgLvQDhXs3VZoOxvlFPRxFuifCe1YoV1Tz171S96rgv5d+bpKaDu/wteXhNpNgOcK7SgBf2eAMN+Bgl8IBs30
/W/+tTrdtH30bcHOGr4uSxbsMs4ai9ZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZi
LdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLdZiLf9/KStXrHjNagVrsRZrsRZrsRZrsRZr+aflpiv/N6bK4JLm
TIxvQuRkdvHEyycgt1sAgsu5rgmZLYjcbmFdPHODArp4viVgBAaMxe4ziKJJTGzKo9R2IvwC9umyc5oQuaFdPGOj+0fGxPUdFIDg
i3DZJOkyJjkRiQFI0rV7AF+w5xISpidmOxG5wPMtpEaZQsdix1VeqOymfKcwYuhYhFdxI2ZMasX1AbhHvYIIt2u5JwYjd278XG3o
WOy4i4IBhzRXI4ugJG2PLp7pOemePsGh2P2Ql31iuoJI7NbFE5kkBiDwiVEpO06p3DAEVCNQk5idqeAYom0CAhBIxPFiOBOJQSiG
IDDYFXts4hogQ6Asrm707sLoQQh0FHUEAhBFC0Cgc1ytvjh/uYHCDI/FDleOKkGXycucGIgANwTGd9Wl2hEBud2TggIQ0DaOt60b
AbLwlqlXEMMzTrBfizq0pKSgWgNif/s4wU72nKSAhxC/BuQPRGCX+iIiIIAXMV0riBiKgOA4kwlIDERAaBzvL04cW5H62NHbaGYH
XlzezghV1k1Pt7rp6a4JHYs9kUKvi5Epr2r3+ICx2BUl0iUEBMGJCkTgoLq5EAkTGDoWO6JF4oPFEkMQECvSHs0SgoCRphPUIxQB
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
"""
