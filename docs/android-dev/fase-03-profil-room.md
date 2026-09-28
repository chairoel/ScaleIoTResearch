# Fase 3 — Profil dan Room

Syarat mulai: pintu keluar [fase 2](fase-02-rumus-v235-mesin-sesi.md).

Sumber kolom: [simpan.py](../../aplikasi/simpan.py). Waktu disimpan UTC.

## Yang dihasilkan

### Room

Dua tabel. `impedansi_ohm` dan `laporan` adalah teks JSON, sama seperti `json.dumps` di Python. Serialization memakai `kotlinx.serialization`.

```text
tubuh(id, tinggi_cm, umur, jenis_kelamin, dibuat)
ukur(id, dibuat, mac, product_id, berat_kg, tampilan_berat,
     impedansi_ohm, rumus, kode, laporan)
```

`muatTubuh` mengambil baris `tubuh` dengan `id` terbesar. `daftar` mengembalikan `ukur` terbaru di atas (`id` menurun; Python mengurutkan menaik, layar riwayat membaliknya).

Jenis kelamin selain 0 dan 1 ditolak sebelum insert, sama seperti `DataTubuh`.

### DataStore

Berkas preferensi `healthtrack_prefs` dibuat di fase ini. Tidak ada kunci wajib. Profil dan hasil tidak ditulis ke prefs.

### Layar

Navigasi Compose dengan Navigation 3: `NavDisplay` dan `NavKey` di `presentation/navigation/`. Tujuan fase ini: Profil, Sesi, Riwayat. Tujuan Hasil boleh sudah terdaftar; isinya dilengkapi di fase 5.

Teks Indonesia.

1. **Profil.** Tinggi (cm), umur, jenis kelamin. Simpan menulis baris `tubuh` baru. Layar menampilkan baris terbaru.
2. **Sesi.** Tombol mulai. Tanpa profil, sesi tidak masuk keadaan mengukur. Bluetooth belum disambungkan; tombol hanya membuka alur yang fase 4 isi.
3. **Riwayat.** Daftar kosong bila belum ada baris `ukur`. Membuka hasil tersimpan menyusul di fase 5.

ViewModel memegang `StateFlow`. Dependensi diisi lewat konstruktor dari `MainActivity` atau pabrik kecil di `app`. Hilt tidak dipasang.

## Langkah

1. Tambah Room, DataStore, dan plugin serialization ke version catalog. Jangan menambah supabase, Hilt, OkHttp, atau Retrofit.
2. Entity, DAO, dan database untuk `tubuh` dan `ukur`.
3. Uji JVM di `app` (bukan emulator): simpan profil, muat baris terbaru, tolak jenis kelamin 2, simpan satu hasil lewat `PenyimpanHasil`, baca kembali JSON laporan.
4. Layar profil dan riwayat kosong, serta kunci mulai sesi bila `muatTubuh` kosong.

## Pintu keluar

Menyimpan profil, memuat baris terbaru, menolak jenis kelamin selain 0 dan 1, dan sesi tidak mulai tanpa profil.

## Belum dikerjakan

Pemindaian, GATT, daftar indeks, dan `vA019`.
