"""Parser GATT OKOK untuk sesi yang tersambung.

Mengikuti [`chipseaStraightFrame.process`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java)
untuk versi 16 dan perintah 0 serta 1 pada versi 17. Berat memakai
[`WeightUnitUtil.Parser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/WeightUnitUtil.java)
lewat [`parse_weight`](siaran_okok.py). Angka multi-byte big-endian, lewat hex seperti
[`BytesUtil.bytesToInt`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java).

Angka lemak, air, otot, BMR, lemak visceral, dan tulang pada versi 16 adalah isi paket
timbangan setelah penyempitan [`CsFatScale`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java).
Itu bukan laporan komposisi. Laporan tetap `cs_bias_v235` atau `cs_bias_vA019`.

Perintah 18, 19, dan 20 tidak diurai di sini.
"""

from __future__ import annotations

from dataclasses import dataclass

from rumus.siaran_okok import FrameFormatError, parse_weight


class GattBelumDidukung(FrameFormatError):
    """Versi atau perintah di luar cakupan parser ini."""


@dataclass(frozen=True)
class GattOkok:
    version: int
    command: int | None
    lock_flag: int
    property: int
    weight_kg: float
    scale_weight: str
    history: bool
    axunge: float
    water: float
    muscle: float
    bmr: float
    visceral_fat: float
    ori_visceral_fat: float
    bone: float


def _need(frame: bytes, size: int) -> None:
    if len(frame) < size:
        raise FrameFormatError("panjang GATT tidak cukup")


def _slice_int(frame: bytes, start: int, size: int) -> int:
    """`bytesToInt(subBytes(...))`. Potongan yang tidak muat menjadi 0."""
    if size <= 0 or len(frame) < start + size:
        return 0
    return int(frame[start : start + size].hex(), 16)


def _stored_weight(kg: float) -> float:
    """`setWeight` mengalikan 10 lalu membagi 10, jadi kilogram tetap kilogram."""
    return (kg * 10.0) / 10.0


def _set_axunge(raw: int) -> float:
    if raw >= 65535.0:
        return 0.0
    value = raw / 10.0
    if 5.0 <= value <= 45.0:
        return value
    return 0.0


def _set_water(raw: int) -> float:
    value = raw / 10.0
    if value >= 100.0 or value < 20.0 or value > 85.0:
        return 0.0
    return value


def _set_muscle(raw: int) -> float:
    value = raw / 10.0
    if value >= 100.0:
        return 0.0
    return value


def _set_bmr(raw: int) -> float:
    if raw >= 65535.0:
        return 0.0
    if raw >= 5000.0:
        return raw / 10.0
    return float(raw)


def _set_visceral(raw: int) -> tuple[float, float]:
    shown = raw / 10.0
    if shown >= 100.0 or shown > 59.0:
        shown = 0.0
    return shown, float(raw)


def _set_bone(raw: int) -> float:
    if raw >= 65535.0:
        return 0.0
    value = raw / 10.0
    if value >= 1.0:
        if value <= 4.0:
            return value
        return 4.0
    return 0.0


def _composition(frame: bytes) -> tuple[float, float, float, float, float, float, float]:
    axunge = _set_axunge(_slice_int(frame, 7, 2))
    water = _set_water(_slice_int(frame, 9, 2))
    muscle = _set_muscle(_slice_int(frame, 11, 2))
    bmr = _set_bmr(_slice_int(frame, 13, 2))
    visceral, ori = _set_visceral(_slice_int(frame, 15, 2))
    bone = _set_bone(_slice_int(frame, 17, 1))
    return axunge, water, muscle, bmr, visceral, ori, bone


def _result(
    *,
    version: int,
    command: int | None,
    lock_flag: int,
    prop: int,
    weight_kg: float,
    scale_weight: str,
    composition: tuple[float, float, float, float, float, float, float] | None,
) -> GattOkok:
    if composition is None:
        axunge = water = muscle = bmr = visceral = ori = bone = 0.0
    else:
        axunge, water, muscle, bmr, visceral, ori, bone = composition
    return GattOkok(
        version=version,
        command=command,
        lock_flag=lock_flag,
        property=prop & 0xFF,
        weight_kg=weight_kg,
        scale_weight=scale_weight,
        history=False,
        axunge=axunge,
        water=water,
        muscle=muscle,
        bmr=bmr,
        visceral_fat=visceral,
        ori_visceral_fat=ori,
        bone=bone,
    )


def _parse_v16(frame: bytes) -> GattOkok:
    _need(frame, 7)
    prop = frame[4]
    lock_flag = prop & 1
    weight_kg, scale_weight = parse_weight(frame[5], frame[6], prop, cloud=False)
    composition = _composition(frame) if lock_flag > 0 else None
    return _result(
        version=16,
        command=None,
        lock_flag=lock_flag,
        prop=prop,
        weight_kg=_stored_weight(weight_kg),
        scale_weight=scale_weight,
        composition=composition,
    )


def _parse_v17_weight(frame: bytes, command: int) -> GattOkok:
    _need(frame, 12)
    prop = frame[11]
    weight_kg, scale_weight = parse_weight(frame[5], frame[6], prop, cloud=False)
    return _result(
        version=17,
        command=command,
        lock_flag=command,
        prop=prop,
        weight_kg=_stored_weight(weight_kg),
        scale_weight=scale_weight,
        composition=None,
    )


def parse_gatt(frame: bytes) -> GattOkok:
    """Satu notifikasi GATT header `0xCA`, versi 16 atau versi 17 perintah 0 dan 1."""
    if not frame:
        raise FrameFormatError("GATT kosong")
    if frame[0] != 0xCA:
        raise FrameFormatError("header GATT bukan 0xCA")
    _need(frame, 3)
    version = frame[1]
    if version == 16:
        return _parse_v16(frame)
    if version == 17:
        _need(frame, 4)
        command = frame[3]
        if command in (0, 1):
            return _parse_v17_weight(frame, command)
        raise GattBelumDidukung("perintah GATT versi 17 di luar parser ini")
    raise GattBelumDidukung("versi GATT di luar parser ini")
