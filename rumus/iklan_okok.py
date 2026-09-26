"""Muatan pabrik dari iklan BLE yang masuk parser siaran OKOK.

Parser Java menerima byte setelah tipe AD `0xFF`. Byte pertama muatan
`0xCA` atau `0xC0` menandai keluarga OKOK.
"""

from __future__ import annotations

_HEADER = (0xCA, 0xC0)


def muatan_okok(rekaman: bytes) -> bytes | None:
    """Muatan pabrik pertama yang berawalan `0xCA` atau `0xC0`.

    Rekaman adalah scan record mentah: panjang, tipe, lalu data.
    Pencarian berjalan sampai habis, termasuk bila daftar UUID 16-bit
    muncul sebelum data pabrik.
    """
    indeks = 0
    while indeks < len(rekaman):
        panjang = rekaman[indeks]
        indeks += 1
        if panjang == 0 or indeks + panjang > len(rekaman):
            return None
        blok = rekaman[indeks : indeks + panjang]
        indeks += panjang
        if not blok or blok[0] != 0xFF or len(blok) < 2:
            continue
        muatan = blok[1:]
        if muatan[0] in _HEADER:
            return muatan
    return None


def muatan_dari_pabrik(company_id: int, sisa: bytes) -> bytes | None:
    """Susun ulang id pabrik 16-bit little-endian plus sisa muatan."""
    muatan = int(company_id).to_bytes(2, "little") + bytes(sisa)
    if muatan[0] in _HEADER:
        return muatan
    return None
