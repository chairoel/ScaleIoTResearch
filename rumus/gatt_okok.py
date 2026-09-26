"""Parser GATT OKOK untuk sesi yang tersambung.

Mengikuti [`chipseaStraightFrame.process`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java)
untuk versi 16, perintah 0 dan 1 pada versi 17, rakitan perintah 18 dan 19, serta perintah 20.
Berat memakai [`WeightUnitUtil.Parser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/WeightUnitUtil.java)
lewat [`parse_weight`](siaran_okok.py). Angka multi-byte big-endian, lewat hex seperti
[`BytesUtil.bytesToInt`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java).

Angka lemak, air, otot, BMR, lemak visceral, dan tulang adalah isi paket timbangan setelah
penyempitan [`CsFatScale`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java).
Itu bukan laporan komposisi. Laporan tetap `cs_bias_v235` atau `cs_bias_vA019`.

Perintah 20 menghasilkan [`CsFatConfirm`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatConfirm.java),
bukan pengukuran. Beberapa paket butuh satu [`GattParser`](gatt_okok.py).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

from rumus.siaran_okok import FrameFormatError, parse_weight


class GattBelumDidukung(FrameFormatError):
    """Versi atau perintah di luar cakupan parser ini."""


class GattMenunggu(Exception):
    """Rakitan perintah 18, 19, atau 20 belum lengkap."""


@dataclass(frozen=True)
class GattKonfirmasi:
    """Daftar peran yang cocok. Bukan laporan komposisi."""

    version: int
    command: int
    property: int
    weight_kg: float
    scale_weight: str
    matched_roles: tuple[int, ...]


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
    role_id: int = 0
    weighing_date: datetime | None = None


def _need(frame: bytes, size: int) -> None:
    if len(frame) < size:
        raise FrameFormatError("panjang GATT tidak cukup")


def _java_byte(value: int) -> int:
    value &= 0xFF
    return value - 256 if value >= 128 else value


def _bytes_to_int(raw: bytes) -> int:
    """`Integer.parseInt(hex, 16)`. Nilai di atas int bertanda 32 bit menjadi 0."""
    if not raw:
        return 0
    value = int(raw.hex(), 16)
    if value > 0x7FFFFFFF:
        return 0
    return value


def _slice_int(frame: bytes, start: int, size: int) -> int:
    """`bytesToInt(subBytes(...))`. Potongan yang tidak muat menjadi 0."""
    if size <= 0 or len(frame) < start + size:
        return 0
    return _bytes_to_int(frame[start : start + size])


def _split_pack(raw: int) -> tuple[int, int]:
    """Nibble rendah = jumlah paket, nibble tinggi = nomor paket. Geser byte bertanda."""
    signed = _java_byte(raw)
    low = _java_byte((signed << 4) & 0xFF)
    total = _java_byte(low >> 4)
    number = _java_byte(signed >> 4)
    return total, number


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


def _recalculate_muscle(muscle: float, weight_kg: float) -> float:
    """Persen otot dari otot dibagi berat. Di atas atau sama dengan 50, nilai otot dipakai dan dibatasi 50."""
    if weight_kg == 0.0 and muscle == 0.0:
        ratio = float("nan")
    elif weight_kg == 0.0:
        ratio = float("inf") if muscle > 0.0 else float("-inf")
    else:
        ratio = (muscle / weight_kg) * 100.0
    if ratio >= 50.0:
        value = 50.0 if muscle >= 50.0 else muscle
    else:
        value = ratio
    raw = 0 if math.isnan(value) else int(value * 10.0)
    return _set_muscle(raw)


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
    history: bool = False,
    role_id: int = 0,
    weighing_date: datetime | None = None,
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
        history=history,
        axunge=axunge,
        water=water,
        muscle=muscle,
        bmr=bmr,
        visceral_fat=visceral,
        ori_visceral_fat=ori,
        bone=bone,
        role_id=role_id,
        weighing_date=weighing_date,
    )


def _concat_packets(store: dict[int, bytes]) -> bytes:
    parts: list[bytes] = []
    for index in range(1, len(store) + 1):
        key = index if index < 128 else index - 256
        piece = store.get(key)
        if piece is None:
            raise FrameFormatError("paket GATT hilang")
        parts.append(piece)
    return b"".join(parts)


def _parse_assembled(body: bytes, command: int) -> GattOkok:
    if len(body) < 12:
        raise FrameFormatError("rakitan GATT tidak cukup")
    prop = body[4]
    weight_kg, scale_weight = parse_weight(body[10], body[11], prop, cloud=False)
    weight_kg = _stored_weight(weight_kg)
    muscle = _recalculate_muscle(_set_muscle(_slice_int(body, 16, 2)), weight_kg)
    visceral, ori = _set_visceral(_slice_int(body, 20, 2))
    weighing_date = None
    if command == 19:
        weighing_date = datetime.fromtimestamp(_slice_int(body, 0, 4), timezone.utc)
    return _result(
        version=17,
        command=command,
        lock_flag=1,
        prop=prop,
        weight_kg=weight_kg,
        scale_weight=scale_weight,
        composition=(
            _set_axunge(_slice_int(body, 12, 2)),
            _set_water(_slice_int(body, 14, 2)),
            muscle,
            _set_bmr(_slice_int(body, 18, 2)),
            visceral,
            ori,
            _set_bone(_slice_int(body, 22, 1)),
        ),
        history=command == 19,
        role_id=_slice_int(body, 6, 4),
        weighing_date=weighing_date,
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


def _parse_roles(body: bytes) -> GattKonfirmasi:
    if len(body) < 3:
        raise FrameFormatError("rakitan peran GATT tidak cukup")
    prop = body[2]
    weight_kg, scale_weight = parse_weight(body[0], body[1], prop, cloud=False)
    roles: list[int] = []
    index = 3
    while index < len(body):
        roles.append(_slice_int(body, index, 4))
        index += 4
    return GattKonfirmasi(
        version=17,
        command=20,
        property=prop & 0xFF,
        weight_kg=_stored_weight(weight_kg),
        scale_weight=scale_weight,
        matched_roles=tuple(roles),
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


class GattParser:
    """Satu sambungan. Perintah 18, 19, dan 20 punya buffer masing-masing."""

    def __init__(self) -> None:
        self._live: dict[int, bytes] | None = {}
        self._history: dict[int, bytes] | None = {}
        self._roles: bytearray | None = bytearray()

    def parse(self, frame: bytes) -> GattOkok | GattKonfirmasi | None:
        """`None` berarti rakitan belum lengkap, sama dengan `Wait_Scale_Data`."""
        if not frame:
            raise FrameFormatError("GATT kosong")
        if frame[0] != 0xCA:
            raise FrameFormatError("header GATT bukan 0xCA")
        _need(frame, 3)
        version = frame[1]
        if version == 16:
            return _parse_v16(frame)
        if version != 17:
            raise GattBelumDidukung("versi GATT di luar parser ini")
        _need(frame, 4)
        command = frame[3]
        if command in (0, 1):
            return _parse_v17_weight(frame, command)
        if command in (18, 19):
            return self._absorb(frame, command)
        if command == 20:
            return self._absorb_roles(frame)
        raise GattBelumDidukung("perintah GATT versi 17 di luar parser ini")

    def _absorb(self, frame: bytes, command: int) -> GattOkok | None:
        _need(frame, 5)
        payload_len = _java_byte(frame[2]) - 2
        if payload_len < 0:
            raise FrameFormatError("panjang muatan GATT tidak valid")
        _need(frame, 5 + payload_len)
        payload = bytes(frame[5 : 5 + payload_len])
        total, number = _split_pack(frame[4])
        store = self._live if command == 18 else self._history
        if number == 1:
            store = {} if store is None else store
            store.clear()
        elif store is None:
            raise FrameFormatError("buffer GATT kosong")
        store.pop(number, None)
        store[number] = payload
        if command == 18:
            self._live = store
        else:
            self._history = store
        if total != number:
            return None
        if len(store) != total:
            store.clear()
            return None
        parsed = _parse_assembled(_concat_packets(store), command)
        if command == 18:
            self._live = None
        else:
            self._history = None
        return parsed

    def _absorb_roles(self, frame: bytes) -> GattKonfirmasi | None:
        _need(frame, 5)
        payload_len = _java_byte(frame[2]) - 2
        if payload_len > 0:
            _need(frame, 5 + payload_len)
            payload = bytes(frame[5 : 5 + payload_len])
        else:
            payload = b""
        total, number = _split_pack(frame[4])
        if self._roles is None:
            self._roles = bytearray()
        self._roles.extend(payload)
        if total != number:
            return None
        body = bytes(self._roles)
        if len(body) < 3:
            raise FrameFormatError("rakitan peran GATT tidak cukup")
        parsed = _parse_roles(body)
        self._roles = None
        return parsed


def parse_gatt(frame: bytes) -> GattOkok | GattKonfirmasi:
    """Satu notifikasi yang sudah lengkap. Rakitan yang belum selesai melempar [`GattMenunggu`]."""
    parsed = GattParser().parse(frame)
    if parsed is None:
        raise GattMenunggu("paket GATT belum lengkap")
    return parsed
