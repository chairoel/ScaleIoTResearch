"""Perintah satu sesi ukur.

    python -m aplikasi tubuh --tinggi 170 --umur 30 --kelamin 1
    python -m aplikasi ukur --mac AA:BB --siaran C0... --gatt CA...
    python -m aplikasi sesi
    python -m aplikasi daftar
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from aplikasi.sesi_ble import PendengarSesi, dengar
from aplikasi.sesi_ukur import DataTubuh, SesiUkur
from aplikasi.simpan import Penyimpan
from rumus.siaran_okok import FrameFormatError

_BERKAS = Path("data/scaleiot.sqlite")


def _hex(text: str) -> bytes:
    raw = text.replace(" ", "").replace(":", "")
    if raw.lower().startswith("0x"):
        raw = raw[2:]
    return bytes.fromhex(raw)


def _tubuh_dari(args: argparse.Namespace, simpan: Penyimpan) -> DataTubuh | None:
    if args.tinggi is not None or args.umur is not None or args.kelamin is not None:
        if args.tinggi is None or args.umur is None or args.kelamin is None:
            print("Tinggi, umur, dan jenis kelamin diisi bersama.", file=sys.stderr)
            return None
        return DataTubuh(args.tinggi, args.umur, args.kelamin)
    return simpan.muat_tubuh()


def _cetak_hasil(sesi: SesiUkur) -> None:
    hasil = sesi.hasil
    if hasil is None:
        print(sesi.keadaan())
        return
    laporan = hasil.laporan
    print(f"Berat {hasil.tampilan_berat} kg")
    print(f"Impedansi {hasil.impedansi_ohm[0]} ohm")
    print(f"Lemak {laporan.bfp}")
    print(f"Otot {laporan.smm}")
    print(f"Air {laporan.bwp}")
    print(f"Viseral {laporan.vfl}")
    print(f"Skor {laporan.sbc}")
    print(f"Rumus {hasil.rumus}")


def _sesi_ble(args: argparse.Namespace, tubuh: DataTubuh, simpan: Penyimpan) -> int:
    sesi = SesiUkur(tubuh, simpan)
    pendengar = PendengarSesi(sesi, args.mac)
    sys.stdout.reconfigure(line_buffering=True)
    sys.stderr.reconfigure(line_buffering=True)
    print(f"Mendengarkan timbangan selama {args.detik:g} detik. Naik ke timbangan.")
    print("Jika macOS menanyakan izin Bluetooth, izinkan untuk proses ini.")
    try:
        asyncio.run(dengar(pendengar, args.detik))
    except Exception as exc:
        print(exc, file=sys.stderr)
        return 1
    _cetak_hasil(sesi)
    if pendengar.hex_siaran:
        print(f"Siaran {pendengar.hex_siaran}")
    if pendengar.hex_gatt:
        print(f"GATT {pendengar.hex_gatt}")
    if sesi.hasil is None:
        return 1
    print("Bandingkan berat dan komposisi ini dengan aplikasi OKOK pada timbangan yang sama.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Satu sesi ukur OKOK")
    parser.add_argument("--berkas", type=Path, default=_BERKAS)
    sub = parser.add_subparsers(dest="perintah", required=True)

    tubuh = sub.add_parser("tubuh", help="simpan tinggi, umur, dan jenis kelamin")
    tubuh.add_argument("--tinggi", type=float, required=True)
    tubuh.add_argument("--umur", type=int, required=True)
    tubuh.add_argument("--kelamin", type=int, choices=(0, 1), required=True, help="0 perempuan, 1 laki-laki")

    sub.add_parser("profil", help="tampilkan data tubuh terakhir")

    ukur = sub.add_parser("ukur", help="satu sesi dari hex siaran dan GATT")
    ukur.add_argument("--mac", default="")
    ukur.add_argument("--siaran", required=True)
    ukur.add_argument("--gatt", action="append", required=True)
    ukur.add_argument("--tinggi", type=float)
    ukur.add_argument("--umur", type=int)
    ukur.add_argument("--kelamin", type=int, choices=(0, 1))

    hidup = sub.add_parser("sesi", help="satu sesi dari timbangan lewat Bluetooth")
    hidup.add_argument("--detik", type=float, default=120)
    hidup.add_argument("--mac", default="")
    hidup.add_argument("--tinggi", type=float)
    hidup.add_argument("--umur", type=int)
    hidup.add_argument("--kelamin", type=int, choices=(0, 1))

    sub.add_parser("daftar", help="daftar hasil ukur")

    args = parser.parse_args(argv)
    simpan = Penyimpan(args.berkas)
    try:
        if args.perintah == "tubuh":
            tubuh_baru = DataTubuh(args.tinggi, args.umur, args.kelamin)
            simpan.simpan_tubuh(tubuh_baru)
            print(f"Tinggi {tubuh_baru.tinggi_cm} cm, umur {tubuh_baru.umur}, kelamin {tubuh_baru.jenis_kelamin}")
            return 0
        if args.perintah == "profil":
            tubuh_tersimpan = simpan.muat_tubuh()
            if tubuh_tersimpan is None:
                print("Data tubuh belum ada.")
                return 1
            print(
                f"Tinggi {tubuh_tersimpan.tinggi_cm} cm, umur {tubuh_tersimpan.umur}, kelamin {tubuh_tersimpan.jenis_kelamin}"
            )
            return 0
        if args.perintah == "daftar":
            baris = simpan.daftar()
            if not baris:
                print("Hasil ukur belum ada.")
                return 0
            for item in baris:
                lemak = item["laporan"].get("bfp")
                print(f"{item['id']}  {item['dibuat']}  {item['berat_kg']} kg  lemak {lemak}  {item['rumus']}")
            return 0
        tubuh_sesi = _tubuh_dari(args, simpan)
        if tubuh_sesi is None:
            print("Data tubuh belum ada.", file=sys.stderr)
            return 2
        if args.perintah == "sesi":
            return _sesi_ble(args, tubuh_sesi, simpan)
        sesi = SesiUkur(tubuh_sesi, simpan)
        try:
            sesi.terima_siaran(_hex(args.siaran), args.mac)
            for frame in args.gatt:
                sesi.terima_gatt(_hex(frame))
        except (FrameFormatError, ValueError) as exc:
            print(exc, file=sys.stderr)
            return 1
        _cetak_hasil(sesi)
        return 0 if sesi.hasil is not None else 1
    finally:
        simpan.tutup()


if __name__ == "__main__":
    raise SystemExit(main())
