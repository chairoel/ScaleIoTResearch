# Fase 3 — Profil dan Room

Syarat mulai: pintu keluar [fase 2](fase-02-rumus-v235-mesin-sesi.md).

Sumber kolom: [simpan.py](../../aplikasi/simpan.py). Waktu disimpan UTC.

## Yang dihasilkan

### Room

Dua tabel. `impedansi_ohm` dan `laporan` adalah teks JSON, sama seperti `json.dumps` di Python. Serialization memakai `kotlinx.serialization`.

```text
body(id, height_cm, age, sex, created_at)
measurement(id, created_at, mac, product_id, weight_kg, scale_weight,
     impedance_ohm, formula, code, report)
```

`loadBody` mengambil baris `body` dengan `id` terbesar. `listMeasurements` mengembalikan `measurement` terbaru di atas (`id` menurun; Python mengurutkan menaik, layar riwayat membaliknya).

Jenis kelamin selain 0 dan 1 ditolak sebelum insert, sama seperti `BodyData`.

### DataStore

Berkas preferensi `healthtrack_prefs` dibuat di fase ini. Tidak ada kunci wajib. Profil dan hasil tidak ditulis ke prefs.

### Layar

Navigasi Compose dengan Navigation 3: `NavDisplay` dan `NavKey` di `presentation/navigation/`. Tujuan fase ini: Profil, Sesi, Riwayat. Tujuan Hasil boleh sudah terdaftar; isinya dilengkapi di fase 5.

Teks Indonesia.

1. **Profil.** Tinggi (cm), umur, jenis kelamin. Simpan menulis baris `body` baru. Layar menampilkan baris terbaru.
2. **Sesi.** Tombol mulai. Tanpa profil, sesi tidak masuk keadaan mengukur. Bluetooth belum disambungkan; tombol hanya membuka alur yang fase 4 isi.
3. **Riwayat.** Daftar kosong bila belum ada baris `measurement`. Membuka hasil tersimpan menyusul di fase 5.

ViewModel memegang `StateFlow` dan memakai `@HiltViewModel`. Hilt sudah dipasang. Binding repository baru ditambah di `RepositoryModule`.

## Langkah

1. Tambah Room, DataStore, dan plugin serialization ke version catalog. Jangan menambah supabase, OkHttp, atau Retrofit.
2. Entity, DAO, dan database untuk `body` dan `measurement`.
3. Uji JVM di `app` (bukan emulator): simpan profil, muat baris terbaru, tolak jenis kelamin 2, simpan satu hasil lewat `ResultStore`, baca kembali JSON laporan.
4. Layar profil dan riwayat kosong, serta kunci mulai sesi bila `loadBody` kosong.

## Pintu keluar

Menyimpan profil, memuat baris terbaru, menolak jenis kelamin selain 0 dan 1, dan sesi tidak mulai tanpa profil.

## Belum dikerjakan

Pemindaian, GATT, daftar indeks, dan `vA019`.
