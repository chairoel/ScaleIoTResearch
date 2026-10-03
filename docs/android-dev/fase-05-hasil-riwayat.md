# Fase 5 — Hasil dan riwayat

Syarat mulai: pintu keluar [fase 4](fase-04-sesi-bluetooth.md). Tahap pertama untuk timbangan satu frekuensi selesai di fase ini.

## Yang dihasilkan

Layar **Hasil** (`presentation/result`) dari fase 4 tetap memakai `DisplayMeasurementUseCase` dari [`UseCaseModule`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/di/UseCaseModule.kt). Fase ini tidak menghitung ulang angka di Compose.

Layar **Riwayat** (`presentation/history`) memakai `MeasurementRepository.list`, terbaru di atas. Satu baris mendorong `ResultRoute` dan membuka kembali layar hasil dari JSON `report` dan `impedance_ohm` yang tersimpan, termasuk hex bila ikut tersimpan. Hasil yang dibuka dari riwayat tidak memulai sesi Bluetooth.

ViewModel hasil dan riwayat menyuntik `MeasurementRepository`. Keduanya tidak mengimpor Room atau `BluetoothGatt`.

Teks Indonesia, koma desimal, sesuai tabel fase 2.

## Langkah

1. Isi `ResultRoute` dari `MeasurementResult` yang baru saja ditutup dan dari baris `measurement` yang dibaca kembali.
2. Sambungkan baris riwayat ke `ResultRoute` lewat `backStack.navigateTo`.
3. Tutup aplikasi, buka lagi, buka hasil yang sama dari riwayat.

## Pintu keluar

Satu pengukuran tersimpan, muncul di riwayat, dan tetap ada setelah aplikasi ditutup. Angka yang terbuka lagi sama dengan angka saat sesi selesai, termasuk tulang 2,77 dan metabolisme 1502,0 pada vektor 68,7 kg bila sesi itu yang tersimpan.

## Belum dikerjakan

`vA019` dan modul produk di luar satu sesi ukur.
