"""Satu sesi ukur.

Berat yang disimpan adalah `GattOkok` dengan `lock_flag == 1` dan
`history == False`, lewat [`GattParser`](../rumus/gatt_okok.py).
Impedansi yang masuk rumus adalah `impedance_ohm` pada siaran terkunci,
lewat [`parse_broadcast`](../rumus/siaran_okok.py). Satu nilai ohm memakai
[`parse_default_z`](../rumus/cs_bias_v235.py). Sepuluh nilai memakai
[`parse_multi_frequency`](../rumus/cs_bias_vA019.py). Laporan memakai
hasil rumus itu.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

from rumus.cs_bias_v235 import OkokReport, parse_default_z

if TYPE_CHECKING:
    from rumus.cs_bias_vA019 import MultiFrequencyReport
from rumus.gatt_okok import GattKonfirmasi, GattOkok, GattParser
from rumus.siaran_okok import SiaranOkok, parse_broadcast


@dataclass(frozen=True)
class DataTubuh:
    """Tinggi, umur, dan jenis kelamin yang rumus butuhkan.

    Jenis kelamin 0 perempuan, 1 laki-laki.
    """

    tinggi_cm: float
    umur: int
    jenis_kelamin: int

    def __post_init__(self) -> None:
        if self.jenis_kelamin not in (0, 1):
            raise ValueError("jenis kelamin 0 atau 1")


@dataclass(frozen=True)
class HasilUkur:
    mac: str
    product_id: int
    berat_kg: float
    tampilan_berat: str
    impedansi_ohm: tuple[float, ...]
    rumus: str
    kode: int
    laporan: OkokReport | MultiFrequencyReport


class PenyimpanHasil(Protocol):
    def simpan_hasil(self, hasil: HasilUkur) -> int: ...


def hitung_laporan(
    tubuh: DataTubuh,
    berat_kg: float,
    impedansi_ohm: float | tuple[float, ...] | list[float],
):
    """Laporan dari data tubuh, berat kilogram, dan impedansi ohm."""
    if isinstance(impedansi_ohm, (int, float)):
        nilai = (float(impedansi_ohm),)
    else:
        nilai = tuple(float(item) for item in impedansi_ohm)
    if len(nilai) == 1:
        hasil = parse_default_z(
            tubuh.jenis_kelamin,
            tubuh.umur,
            tubuh.tinggi_cm,
            berat_kg,
            nilai[0],
        )
        return "v235", hasil.result, hasil.data
    if len(nilai) == 10:
        from rumus.cs_bias_vA019 import parse_multi_frequency

        hasil = parse_multi_frequency(
            tubuh.jenis_kelamin,
            tubuh.umur,
            tubuh.tinggi_cm,
            berat_kg,
            nilai,
        )
        return "vA019", hasil.result, hasil.data
    raise ValueError("impedansi laporan harus 1 atau 10 nilai")


class SesiUkur:
    """Satu pengukuran. Hasil pertama yang rumusnya berhasil yang disimpan."""

    def __init__(self, tubuh: DataTubuh, penyimpan: PenyimpanHasil | None = None) -> None:
        self.tubuh = tubuh
        self._penyimpan = penyimpan
        self._parser = GattParser()
        self.siaran: SiaranOkok | None = None
        self._impedansi: float | None = None
        self._mac = ""
        self._product_id = 0
        self._berat: GattOkok | None = None
        self.kode: int | None = None
        self.rumus: str | None = None
        self.hasil: HasilUkur | None = None

    @property
    def impedansi_ohm(self) -> float | None:
        return self._impedansi

    @property
    def berat_kg(self) -> float | None:
        if self._berat is None:
            return None
        return self._berat.weight_kg

    def keadaan(self) -> str:
        if self.hasil is not None:
            return "selesai"
        if self._impedansi is None:
            return "menunggu impedansi"
        if self._berat is None:
            return "menunggu berat"
        return f"rumus {self.kode}"

    def terima_siaran(self, frame: bytes, mac: str = "") -> SiaranOkok:
        parsed = parse_broadcast(frame, mac)
        self.siaran = parsed
        if self.hasil is None and parsed.locked and parsed.impedance_ohm is not None:
            self._impedansi = parsed.impedance_ohm
            self._mac = parsed.mac
            self._product_id = parsed.product_id
            self._tutup()
        return parsed

    def terima_gatt(self, frame: bytes) -> GattOkok | GattKonfirmasi | None:
        parsed = self._parser.parse(frame)
        if (
            self.hasil is None
            and isinstance(parsed, GattOkok)
            and parsed.lock_flag == 1
            and not parsed.history
        ):
            self._berat = parsed
            self._tutup()
        return parsed

    def _tutup(self) -> None:
        if self.hasil is not None or self._berat is None or self._impedansi is None:
            return
        rumus, kode, data = hitung_laporan(
            self.tubuh,
            self._berat.weight_kg,
            self._impedansi,
        )
        self.rumus = rumus
        self.kode = kode
        if kode != 0 or data is None:
            return
        hasil = HasilUkur(
            mac=self._mac,
            product_id=self._product_id,
            berat_kg=self._berat.weight_kg,
            tampilan_berat=self._berat.scale_weight,
            impedansi_ohm=(self._impedansi,),
            rumus=rumus,
            kode=kode,
            laporan=data,
        )
        if self._penyimpan is not None:
            self._penyimpan.simpan_hasil(hasil)
        self.hasil = hasil
