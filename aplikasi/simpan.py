"""Penyimpan data tubuh dan hasil ukur aplikasi sendiri."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from aplikasi.sesi_ukur import DataTubuh, HasilUkur


class Penyimpan:
    def __init__(self, berkas: str | Path) -> None:
        path = Path(berkas)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.berkas = path
        self._db = sqlite3.connect(path)
        self._db.row_factory = sqlite3.Row
        self._siapkan()

    def tutup(self) -> None:
        self._db.close()

    def _siapkan(self) -> None:
        self._db.executescript(
            """
            CREATE TABLE IF NOT EXISTS tubuh (
                id INTEGER PRIMARY KEY,
                tinggi_cm REAL NOT NULL,
                umur INTEGER NOT NULL,
                jenis_kelamin INTEGER NOT NULL,
                dibuat TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS ukur (
                id INTEGER PRIMARY KEY,
                dibuat TEXT NOT NULL,
                mac TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                berat_kg REAL NOT NULL,
                tampilan_berat TEXT NOT NULL,
                impedansi_ohm TEXT NOT NULL,
                rumus TEXT NOT NULL,
                kode INTEGER NOT NULL,
                laporan TEXT NOT NULL
            );
            """
        )
        self._db.commit()

    def simpan_tubuh(self, tubuh: DataTubuh) -> int:
        dibuat = datetime.now(timezone.utc).isoformat()
        cursor = self._db.execute(
            """
            INSERT INTO tubuh (tinggi_cm, umur, jenis_kelamin, dibuat)
            VALUES (?, ?, ?, ?)
            """,
            (tubuh.tinggi_cm, tubuh.umur, tubuh.jenis_kelamin, dibuat),
        )
        self._db.commit()
        return int(cursor.lastrowid)

    def muat_tubuh(self) -> DataTubuh | None:
        row = self._db.execute(
            """
            SELECT tinggi_cm, umur, jenis_kelamin
            FROM tubuh
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            return None
        return DataTubuh(row["tinggi_cm"], row["umur"], row["jenis_kelamin"])

    def simpan_hasil(self, hasil: HasilUkur) -> int:
        dibuat = datetime.now(timezone.utc).isoformat()
        cursor = self._db.execute(
            """
            INSERT INTO ukur (
                dibuat, mac, product_id, berat_kg, tampilan_berat,
                impedansi_ohm, rumus, kode, laporan
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dibuat,
                hasil.mac,
                hasil.product_id,
                hasil.berat_kg,
                hasil.tampilan_berat,
                json.dumps(hasil.impedansi_ohm),
                hasil.rumus,
                hasil.kode,
                json.dumps(asdict(hasil.laporan)),
            ),
        )
        self._db.commit()
        return int(cursor.lastrowid)

    def daftar(self) -> list[dict]:
        rows = self._db.execute(
            """
            SELECT id, dibuat, mac, product_id, berat_kg, tampilan_berat,
                   impedansi_ohm, rumus, kode, laporan
            FROM ukur
            ORDER BY id
            """
        ).fetchall()
        hasil = []
        for row in rows:
            item = dict(row)
            item["impedansi_ohm"] = json.loads(item["impedansi_ohm"])
            item["laporan"] = json.loads(item["laporan"])
            hasil.append(item)
        return hasil
