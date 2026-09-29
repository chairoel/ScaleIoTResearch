# Fase 5 — Hasil dan riwayat

Syarat mulai: pintu keluar [fase 4](fase-04-sesi-bluetooth.md). Tahap pertama untuk timbangan satu frekuensi selesai di fase ini.

## Yang dihasilkan

Layar **Hasil** dari fase 4 tetap memakai fungsi pembulatan di `domain`. Fase ini tidak menghitung ulang angka di Compose.

Layar **Riwayat** memakai `listMeasurements` Room, terbaru di atas. Satu baris membuka kembali layar hasil dari JSON `report` dan `impedance_ohm` yang tersimpan, termasuk hex bila ikut tersimpan. Hasil yang dibuka dari riwayat tidak memulai sesi Bluetooth.

Teks Indonesia, koma desimal, sesuai tabel fase 2.

## Langkah

1. Isi tujuan Hasil dari `MeasurementResult` yang baru saja ditutup dan dari baris `measurement` yang dibaca kembali.
2. Sambungkan baris riwayat ke tujuan Hasil.
3. Tutup aplikasi, buka lagi, buka hasil yang sama dari riwayat.

## Pintu keluar

Satu pengukuran tersimpan, muncul di riwayat, dan tetap ada setelah aplikasi ditutup. Angka yang terbuka lagi sama dengan angka saat sesi selesai, termasuk tulang 2,77 dan metabolisme 1502,0 pada vektor 68,7 kg bila sesi itu yang tersimpan.

## Belum dikerjakan

`vA019` dan modul produk di luar satu sesi ukur.
