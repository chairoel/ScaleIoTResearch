# Fase 5 — Hasil dan riwayat

Syarat mulai: pintu keluar [fase 4](fase-04-sesi-bluetooth.md). Tahap pertama untuk timbangan satu frekuensi selesai di fase ini.

## Yang dihasilkan

Layar **Hasil** (`presentation/result`) memakai `DisplayMeasurementUseCase` dari [`UseCaseModule`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/di/UseCaseModule.kt). Angka tidak dihitung ulang di Compose.

Sesi yang baru selesai membuka [`ResultRoute`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/presentation/navigation/Routes.kt) lewat `FinishedSession`: `measurementId`, `heightCm`, `broadcastHex`, dan `gattHex`.

Layar **Riwayat** (`presentation/history`) memakai `MeasurementRepository.list`, terbaru di atas. Satu baris mendorong `ResultRoute(measurementId)` saja. [`ResultViewModel`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/presentation/result/ResultViewModel.kt) membaca baris itu dari `list` dan membulatkan lewat `DisplayMeasurementUseCase`. Tabel `measurement` menyimpan `height_cm` dan `age` dari profil yang dipakai saat laporan disimpan. BMI dari riwayat memakai tinggi itu. Baris yang disimpan sebelum kolom itu ada tetap kosong, dan BMI-nya memakai `BodyRepository.latest`. Tulang dan metabolisme datang dari JSON `report`. Hex kosong ditampilkan `tidak ada`. Hasil yang dibuka dari riwayat tidak memulai sesi Bluetooth.

`ResultViewModel` menyuntik `MeasurementRepository`, `BodyRepository`, dan `DisplayMeasurementUseCase`. `HistoryViewModel` menyuntik `MeasurementRepository`. Keduanya tidak mengimpor Room atau `BluetoothGatt`.

Teks Indonesia, koma desimal, sesuai tabel fase 2.

## Langkah

1. `ResultRoute` dari sesi yang baru selesai membawa id, tinggi, dan hex. Baris `measurement` yang dibaca kembali memakai id saja.
2. Baris riwayat membuka `ResultRoute` lewat `backStack.navigateTo`.
3. Tutup aplikasi, buka lagi, buka hasil yang sama dari riwayat.

## Pintu keluar

Satu pengukuran tersimpan, muncul di riwayat, dan tetap ada setelah aplikasi ditutup. Angka yang terbuka lagi sama dengan angka saat sesi selesai, termasuk tulang 2,77 dan metabolisme 1502,0 pada vektor 68,7 kg bila sesi itu yang tersimpan.

Uji tutup-buka pada 18 Okt 2026 lulus: setelah aplikasi ditutup dan dibuka lagi, angka di riwayat sama dengan saat sesi selesai.

## Belum dikerjakan

`vA019` dan modul produk di luar satu sesi ukur.
