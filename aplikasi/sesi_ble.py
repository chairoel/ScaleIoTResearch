"""Satu sesi dari iklan BLE dan notify GATT.

Layanan dan karakteristik OKOK ada di
[`BtGattAttr`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/BtGattAttr.java).
Notify dipasang pada RX. Sesi ini tidak menulis ke TX.
"""

from __future__ import annotations

import asyncio
import contextlib
import sys
from typing import Protocol

from rumus.gatt_okok import GattKonfirmasi, GattOkok
from rumus.iklan_okok import muatan_dari_pabrik
from rumus.siaran_okok import EncryptedBroadcastError, FrameFormatError

LAYANAN = "0000fff0-0000-1000-8000-00805f9b34fb"
NOTIFY = "0000fff1-0000-1000-8000-00805f9b34fb"


class _Sesi(Protocol):
    hasil: object | None

    def terima_siaran(self, frame: bytes, mac: str = ""): ...

    def terima_gatt(self, frame: bytes): ...

    def keadaan(self) -> str: ...


class PendengarSesi:
    """Meneruskan iklan dan notify ke satu [`SesiUkur`](sesi_ukur.py)."""

    def __init__(self, sesi: _Sesi, mac: str = "") -> None:
        self.sesi = sesi
        self.mac = mac
        self.alamat = mac
        self.siap = False
        self.hex_siaran = ""
        self.hex_gatt = ""
        self._terenkripsi: set[str] = set()
        self._siaran: tuple | None = None
        self._gatt: tuple | None = None
        self._gatt_salah = ""

    def iklan(self, alamat: str, muatan: bytes) -> str | None:
        if self.alamat and alamat.lower() != self.alamat.lower():
            return None
        try:
            parsed = self.sesi.terima_siaran(muatan, alamat)
        except EncryptedBroadcastError:
            self._pasang(alamat)
            if alamat.lower() in self._terenkripsi:
                return None
            self._terenkripsi.add(alamat.lower())
            return f"{alamat} siaran terenkripsi"
        except FrameFormatError:
            return None
        self._pasang(alamat)
        if self.sesi.hasil is None and parsed.locked and parsed.impedance_ohm is not None:
            self.hex_siaran = muatan.hex()
        tanda = (parsed.locked, parsed.impedance_ohm, parsed.weight_kg)
        if tanda == self._siaran:
            return None
        self._siaran = tanda
        kunci = "kunci" if parsed.locked else "terbuka"
        if parsed.impedance_ohm is None:
            ohm = "tanpa impedansi"
        else:
            ohm = f"{parsed.impedance_ohm} ohm"
        return f"{alamat} siaran {kunci} {parsed.weight_kg} kg {ohm}"

    def gatt(self, frame: bytes) -> str | None:
        sudah = self.sesi.hasil is not None
        try:
            parsed = self.sesi.terima_gatt(frame)
        except FrameFormatError as exc:
            teks = str(exc)
            if teks == self._gatt_salah:
                return None
            self._gatt_salah = teks
            return f"GATT diabaikan: {teks}"
        if parsed is None:
            return None
        if isinstance(parsed, GattKonfirmasi):
            return "GATT konfirmasi peran"
        if not isinstance(parsed, GattOkok):
            return None
        if not sudah and parsed.lock_flag == 1 and not parsed.history:
            self.hex_gatt = frame.hex()
        tanda = (parsed.lock_flag, parsed.history, parsed.weight_kg)
        if tanda == self._gatt:
            return None
        self._gatt = tanda
        riwayat = " riwayat" if parsed.history else ""
        return f"GATT kunci {parsed.lock_flag}{riwayat} {parsed.scale_weight} kg"

    def _pasang(self, alamat: str) -> None:
        if not self.alamat:
            self.alamat = alamat
        self.siap = True


def boleh_sambung(pendengar: PendengarSesi, alamat: str) -> bool:
    """Sambungan GATT baru setelah impedansi terkunci dari perangkat ini."""
    return bool(
        pendengar.hex_siaran
        and pendengar.alamat
        and alamat.lower() == pendengar.alamat.lower()
    )


def _karakteristik_notify(services):
    layanan = services.get_service(LAYANAN)
    if layanan is not None:
        char = layanan.get_characteristic(NOTIFY)
        if char is not None:
            return char
    return services.get_characteristic(NOTIFY)


def _teks_layanan(services) -> str:
    baris = ["karakteristik notify OKOK tidak ada"]
    for service in services:
        baris.append(service.uuid)
        for char in service.characteristics:
            baris.append(f"  {char.uuid} {','.join(char.properties)}")
    return "\n".join(baris)


async def dengar(pendengar: PendengarSesi, detik: float) -> None:
    """Pindai iklan OKOK, sambung GATT, dan isi pendengar sampai sesi selesai.

    Pemindaian dihentikan sebelum sambungan. Pada macOS, sambungan yang
    berjalan bersama pemindaian habis waktu dan `TimeoutError` tidak berisi pesan.
    """
    from bleak import BleakClient, BleakScanner

    selesai = asyncio.Event()
    loop = asyncio.get_running_loop()
    tugas: asyncio.Task | None = None
    berhenti = False
    putaran = 0

    def _cek() -> None:
        if pendengar.sesi.hasil is not None:
            selesai.set()

    def _gatt(frame: bytes) -> None:
        baris = pendengar.gatt(frame)
        if baris:
            print(baris, flush=True)
        _cek()

    scanner: BleakScanner | None = None

    async def _sambung(device) -> None:
        nonlocal tugas, putaran
        assert scanner is not None
        await scanner.stop()
        print("pemindaian berhenti, menyambung GATT", flush=True)
        try:
            for nomer in range(1, 4):
                if berhenti or pendengar.sesi.hasil is not None:
                    return
                print(f"menyambung {device.address} percobaan {nomer}", flush=True)
                try:
                    async with BleakClient(device, timeout=15.0) as client:
                        char = _karakteristik_notify(client.services)
                        if char is None:
                            print(_teks_layanan(client.services), file=sys.stderr, flush=True)
                            putaran += 1
                            return

                        def _notify(_char, data: bytearray) -> None:
                            raw = bytes(data)
                            try:
                                loop.call_soon_threadsafe(_gatt, raw)
                            except RuntimeError:
                                return

                        await client.start_notify(char, _notify)
                        print(f"notify {char.uuid}", flush=True)
                        await selesai.wait()
                        return
                except TimeoutError:
                    print(
                        "waktu sambungan habis. Tutup aplikasi OKOK di ponsel bila timbangan sedang tersambung di sana.",
                        flush=True,
                    )
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    print(f"sambungan gagal: {type(exc).__name__}: {exc!r}", file=sys.stderr, flush=True)
            putaran += 1
        finally:
            if pendengar.sesi.hasil is None and not berhenti and putaran < 2:
                tugas = None
                await scanner.start()

    def _di_loop(device, muatan: bytes) -> None:
        nonlocal tugas
        if berhenti:
            return
        baris = pendengar.iklan(device.address, muatan)
        if baris:
            print(baris, flush=True)
        _cek()
        if tugas is None and boleh_sambung(pendengar, device.address) and putaran < 2:
            tugas = asyncio.create_task(_sambung(device))

    def _on_detect(device, adv) -> None:
        muatan = None
        for company, sisa in adv.manufacturer_data.items():
            muatan = muatan_dari_pabrik(company, sisa)
            if muatan is not None:
                break
        if muatan is None:
            return
        loop.call_soon_threadsafe(_di_loop, device, muatan)

    scanner = BleakScanner(_on_detect)
    await scanner.start()
    try:
        await asyncio.wait_for(selesai.wait(), detik)
    except TimeoutError:
        pass
    finally:
        berhenti = True
        selesai.set()
        if tugas is not None:
            tugas.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await tugas
        with contextlib.suppress(Exception):
            await scanner.stop()
