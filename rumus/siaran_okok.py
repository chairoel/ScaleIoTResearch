"""Parser siaran OKOK yang tidak terenkripsi.

Mengikuti [`chipseaBroadcastFrame`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java)
dan [`WeightUnitUtil`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/WeightUnitUtil.java).
Angka multi-byte big-endian, lewat hex seperti [`BytesUtil.bytesToInt`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java).
`and-int/lit16` di bytecode memakai topeng `0xFF`.

Siaran `0xC0` dengan bit 7 byte offset 4 menyala ditolak. Kunci 4 byte tidak ada di rilis pertama.
"""

from __future__ import annotations

import math
import struct
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

_LB_PER_KG = struct.unpack("<f", struct.pack("<f", 0.4535924))[0]


class FrameFormatError(ValueError):
    """Header kosong atau tidak dikenal."""


class EncryptedBroadcastError(FrameFormatError):
    """Siaran 0xC0 terenkripsi, di luar rilis pertama."""


@dataclass(frozen=True)
class SiaranOkok:
    header: int
    version: int
    mac: str
    weight_kg: float
    scale_weight: str | None
    impedance_ohm: float | None
    product_id: int
    device_type: int
    cmd_id: int
    locked: bool
    seq: int
    property: int


def _u8(value: int) -> int:
    return value & 0xFF


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _bits(value: int) -> str:
    value = _u8(value)
    return "".join(str((value >> shift) & 1) for shift in range(7, -1, -1))


def _bytes_to_int(raw: bytes) -> int:
    if not raw:
        return 0
    return int(raw.hex(), 16)


def _round_half_up(value: float, places: int, *, as_float32: bool) -> float:
    quantum = Decimal("1") if places == 0 else Decimal("1").scaleb(-places)
    rounded = Decimal(value).quantize(quantum, rounding=ROUND_HALF_UP)
    number = float(rounded)
    return _f32(number) if as_float32 else number


def _unit(prop: int) -> str:
    pair = _bits(prop)[3:5]
    if pair == "01":
        return "jin"
    if pair == "10":
        return "lb"
    if pair == "11":
        return "st"
    return "kg"


def _digit_places(prop: int, *, cloud: bool, cloud_v4: bool) -> int:
    if cloud_v4:
        pair = _bits(prop)[1:3]
        if pair == "01":
            return 0
        if pair == "10":
            return 1
        return 2
    pair = _bits(prop)[5:7]
    if cloud:
        if pair == "01":
            return 0
        if pair == "10":
            return 1
        return 2
    if pair == "01":
        return 0
    if pair == "10":
        return 2
    return 1


def _lock_bit(prop: int) -> bool:
    return _bits(prop)[7] == "1"


def _device_type_v2(prop: int) -> int:
    return 0 if _bits(prop)[2] == "0" else 2


def _div10(raw: int) -> float:
    return _f32(_f32(raw) / _f32(10.0))


def _java_float_text(value: float) -> str:
    """Teks `Float.toString` untuk float32 yang sudah bulat ke bilangan desimal pendek."""
    number = _f32(value)
    if math.isnan(number):
        return "NaN"
    if math.isinf(number):
        return "Infinity" if number > 0 else "-Infinity"
    if number == 0.0:
        return "-0.0" if math.copysign(1.0, number) < 0 else "0.0"
    sign = "-" if number < 0 else ""
    mag = -number if number < 0 else number
    scientific = mag < 1e-3 or mag >= 1e7
    for digits in range(1, 10):
        if scientific:
            mantissa, exponent = format(mag, f".{digits}e").split("e")
            if "." not in mantissa:
                mantissa += ".0"
            parsed = _f32(float(f"{mantissa}e{int(exponent)}"))
            if parsed == mag:
                return f"{sign}{mantissa}E{int(exponent)}"
            continue
        text = format(mag, f".{digits}g")
        if "e" in text or "E" in text:
            continue
        if _f32(float(text)) == mag:
            if "." not in text:
                text += ".0"
            return sign + text
    return sign + format(mag, ".8g")


def _scale_text(high: int, low: int, scaled: float, places: int, unit: str) -> str:
    if unit == "st":
        return f"{_u8(high)}:{_java_float_text(_f32(_u8(low) / 10.0))}"
    if places == 0:
        return str(int(_f32(scaled)))
    shown = _round_half_up(scaled, places, as_float32=True)
    return _java_float_text(shown)


def parse_weight(high: int, low: int, prop: int, *, cloud: bool = False, cloud_v4: bool = False) -> tuple[float, str]:
    """Berat kilogram dan teks di timbangan, sama dengan `WeightUnitUtil.getParserReturn`."""
    places = _digit_places(prop, cloud=cloud, cloud_v4=cloud_v4)
    raw = _bytes_to_int(bytes((_u8(high), _u8(low))))
    if places == 0:
        scaled = _f32(raw)
    elif places == 1:
        scaled = _f32(_f32(raw) / _f32(10.0))
    else:
        scaled = _f32(_f32(raw) / _f32(100.0))
    scaled = _round_half_up(scaled, places, as_float32=True)
    unit = _unit(prop)
    text = _scale_text(high, low, scaled, places, unit)
    if unit == "jin":
        kg = _f32(scaled * _f32(0.5))
    elif unit == "lb":
        kg = _f32(scaled * _LB_PER_KG)
    elif unit == "st":
        stones, _, pounds = text.partition(":")
        try:
            pounds_value = float(pounds)
            total_lb = (int(stones) * 14) + pounds_value
        except ValueError:
            total_lb = 0.0
        kg = _round_half_up(_f32(_f32(total_lb) * _LB_PER_KG), 3, as_float32=True)
    else:
        kg = scaled
    kg = _round_half_up(kg, places, as_float32=False)
    return kg, text


def _cloud_property(prop: int) -> int:
    unit = _unit(prop)
    places = _digit_places(prop, cloud=True, cloud_v4=False)
    prefix = {"jin": "00001", "lb": "00010", "st": "00011"}.get(unit, "00000")
    suffix = {1: "001", 2: "101"}.get(places, "011")
    return int(prefix + suffix, 2)


def _need(frame: bytes, size: int) -> None:
    if len(frame) < size:
        raise FrameFormatError("panjang siaran tidak cukup")


def _from_weight(
    frame: bytes,
    mac: str,
    *,
    version: int,
    device_type: int,
    cmd_id: int,
    prop: int,
    weight_kg: float,
    scale_weight: str | None,
    impedance_ohm: float | None,
    product_id: int,
    seq: int,
    locked: bool,
) -> SiaranOkok:
    return SiaranOkok(
        header=frame[0],
        version=version,
        mac=mac,
        weight_kg=weight_kg,
        scale_weight=scale_weight,
        impedance_ohm=impedance_ohm,
        product_id=product_id,
        device_type=device_type,
        cmd_id=cmd_id,
        locked=locked,
        seq=seq,
        property=_u8(prop),
    )


def _parse_ca(frame: bytes, mac: str) -> SiaranOkok:
    _need(frame, 2)
    if frame[1] == 32:
        return _parse_ca_v20(frame, mac)
    return _parse_ca_legacy(frame, mac)


def _parse_ca_legacy(frame: bytes, mac: str) -> SiaranOkok:
    _need(frame, 5)
    version = frame[1]
    device_type = 0
    prop = 0
    cmd_id = 0
    if version == 16:
        device_type = frame[3]
        prop = frame[4]
        cmd_id = _u8(prop)
    elif version == 17:
        prop = frame[3]
        device_type = frame[4]
    if device_type != 0:
        _need(frame, 11)
        weight_kg, scale_weight = parse_weight(frame[5], frame[6], prop, cloud=False)
        return _from_weight(
            frame,
            mac,
            version=version,
            device_type=_u8(device_type),
            cmd_id=1 if _lock_bit(prop) else 0,
            prop=prop,
            weight_kg=weight_kg,
            scale_weight=scale_weight,
            impedance_ohm=None,
            product_id=_bytes_to_int(frame[7:11]),
            seq=0,
            locked=_lock_bit(prop),
        )
    if version == 16:
        _need(frame, 10)
        weight_kg = _div10(_bytes_to_int(frame[8:10]))
        return _from_weight(
            frame,
            mac,
            version=version,
            device_type=0,
            cmd_id=cmd_id,
            prop=prop,
            weight_kg=weight_kg,
            scale_weight=None,
            impedance_ohm=None,
            product_id=0,
            seq=0,
            locked=_lock_bit(prop),
        )
    if version != 17:
        return _from_weight(
            frame,
            mac,
            version=version,
            device_type=0,
            cmd_id=0,
            prop=0,
            weight_kg=0.0,
            scale_weight=None,
            impedance_ohm=None,
            product_id=0,
            seq=0,
            locked=False,
        )
    _need(frame, 11)
    weight_kg, scale_weight = parse_weight(frame[5], frame[6], prop, cloud=False)
    return _from_weight(
        frame,
        mac,
        version=17,
        device_type=0,
        cmd_id=1 if _lock_bit(prop) else 0,
        prop=prop,
        weight_kg=weight_kg,
        scale_weight=scale_weight,
        impedance_ohm=None,
        product_id=_bytes_to_int(frame[7:11]),
        seq=0,
        locked=_lock_bit(prop),
    )


def _parse_ca_v20(frame: bytes, mac: str) -> SiaranOkok:
    _need(frame, 14)
    prop = frame[8]
    locked = _lock_bit(prop)
    device_type = 0 if frame[7] == 0 else 2
    if locked:
        weight_kg, scale_weight = parse_weight(frame[10], frame[11], prop, cloud=False)
        impedance = _div10(_bytes_to_int(frame[12:14]))
        seq = _u8(frame[9])
    else:
        weight_kg = 0.0
        scale_weight = ""
        impedance = 0.0
        seq = 0
    return _from_weight(
        frame,
        mac,
        version=32,
        device_type=device_type,
        cmd_id=1 if locked else 0,
        prop=prop,
        weight_kg=weight_kg,
        scale_weight=scale_weight,
        impedance_ohm=impedance,
        product_id=_bytes_to_int(frame[3:7]),
        seq=seq,
        locked=locked,
    )


def _parse_c0(frame: bytes, mac: str) -> SiaranOkok:
    _need(frame, 9)
    if frame[4] & 0x80:
        raise EncryptedBroadcastError("siaran 0xC0 terenkripsi di luar rilis pertama")
    prop = frame[8]
    weight_kg, scale_weight = parse_weight(frame[2], frame[3], prop, cloud=False)
    impedance = _div10(_bytes_to_int(frame[4:6]))
    return _from_weight(
        frame,
        mac,
        version=1,
        device_type=_device_type_v2(prop),
        cmd_id=1 if _lock_bit(prop) else 0,
        prop=prop,
        weight_kg=weight_kg,
        scale_weight=scale_weight,
        impedance_ohm=impedance,
        product_id=_bytes_to_int(frame[6:8]),
        seq=_u8(frame[1]),
        locked=_lock_bit(prop),
    )


def _parse_ff(frame: bytes, mac: str) -> SiaranOkok:
    _need(frame, 10)
    version = frame[2]
    prop = frame[3]
    product = _bytes_to_int(frame[6:10])
    if frame[6:10] == bytes((0xFA, 0xFB, 0xFC, 0xFD)):
        product = 997264800
        prop = 4
    elif product == 1104000001:
        prop = 4
    cloud_v4 = version in (16, 17)
    weight_kg, scale_weight = parse_weight(frame[5], frame[4], prop, cloud=not cloud_v4, cloud_v4=cloud_v4)
    return _from_weight(
        frame,
        mac,
        version=version,
        device_type=1,
        cmd_id=0,
        prop=_cloud_property(prop),
        weight_kg=weight_kg,
        scale_weight=scale_weight,
        impedance_ohm=None,
        product_id=product,
        seq=0,
        locked=False,
    )


def parse_broadcast(frame: bytes, mac: str = "") -> SiaranOkok:
    """Satu iklan pabrikan OKOK. `mac` adalah alamat yang dilihat pemindai."""
    if not frame:
        raise FrameFormatError("siaran kosong")
    header = frame[0]
    if header == 0xCA:
        return _parse_ca(frame, mac)
    if header == 0xFF:
        return _parse_ff(frame, mac)
    if header == 0xC0:
        return _parse_c0(frame, mac)
    raise FrameFormatError("header siaran tidak dikenal")
