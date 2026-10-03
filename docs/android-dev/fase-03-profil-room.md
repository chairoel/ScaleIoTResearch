# Fase 3 — Profil dan Room

Syarat mulai: pintu keluar [fase 2](fase-02-rumus-v235-mesin-sesi.md).

Sumber kolom: [simpan.py](../../aplikasi/simpan.py). Waktu disimpan UTC. Nama tabel Android `body` dan `measurement` (bahasa Inggris). Padanan Python-nya `tubuh` dan `ukur`. Jangan membuat tabel dengan nama Python itu.

Aturan paket: `HealthTrack/.cursor/rules/sm-architecture.mdc`, `sm-data-layer.mdc`, `sm-dependency-injection.mdc`, `sm-navigation.mdc`, `sm-viewmodel-ui.mdc`.

## Yang dihasilkan

### Room dan DataStore

Entitas di `data/model/entity`. DAO dan DataStore di `data/datasource/local`. Database di `data/di/DatabaseModule`. DataStore di `data/di/DataStoreModule`. `AppDispatcher` di `util`, disediakan `data/di/DispatcherModule`.

Dua tabel. `impedance_ohm` dan `report` adalah teks JSON, sama seperti `json.dumps` di Python. Serialization memakai `kotlinx.serialization`.

```text
body(id, height_cm, age, sex, created_at)
measurement(id, created_at, mac, product_id, weight_kg, scale_weight,
     impedance_ohm, formula, code, report)
```

Antarmuka domain, tanpa tipe Room:

- `BodyRepository` — `save` menulis baris `body` baru; `latest` mengambil `id` terbesar.
- `MeasurementRepository` — `save` dari fase 2 mendapat implementasi Room; `list` mengembalikan `measurement` terbaru di atas (`id` menurun). Python mengurutkan menaik; layar riwayat membaliknya di query ini.

UseCase di `domain/usecase`: simpan tubuh, muat tubuh terbaru, simpan hasil, daftar hasil. ViewModel menerima UseCase, bukan DAO dan bukan `*RepositoryImpl`.

Jenis kelamin selain 0 dan 1 ditolak di `BodyData` sebelum insert.

Berkas preferensi `healthtrack_prefs` dibuat di fase ini. Tidak ada kunci wajib. Profil dan hasil tidak ditulis ke prefs.

Binding baru ditambah `@Binds` di `RepositoryModule` yang sudah ada. Jangan membuat paket `com.mascill.healthtrack.di`.

### Layar

Navigasi Compose dengan Navigation 3 di `presentation/navigation/`:

- `Routes.kt` — `NavKey`: `ProfileRoute`, `SessionRoute`, `HistoryRoute`. `ResultRoute` boleh sudah terdaftar; isinya dilengkapi di fase 5.
- `AppNavHost.kt` — `NavDisplay`, `rememberNavBackStack`. Bukan `NavHost` dan bukan `androidx.navigation:navigation-compose`.
- `NavExtensions.kt` — `navigateTo`, `navigateBack`, `navigateToTopLevel`.

Tiga tujuan fase ini adalah tab. `navigateToTopLevel` berpindah tab. Hasil nanti didorong dengan `navigateTo`, bukan tab.

Tema yang ada, `ui/theme/HealthTrackTheme`, dipindah ke `presentation/theme` saat `MainActivity` memasang `AppNavHost`. Jangan membuat tema kedua. Composable tetap `HealthTrackTheme`.

Teks Indonesia. Satu paket per fitur: `*Screen`, `*ViewModel`, `model/*UIState`. `@HiltViewModel`, `StateFlow`, `collectAsStateWithLifecycle`, `androidx.hilt.lifecycle.viewmodel.compose.hiltViewModel`.

1. **Profil** (`presentation/profile`). Tinggi (cm), umur, jenis kelamin. Simpan menulis baris `body` baru lewat UseCase. Layar menampilkan baris terbaru.
2. **Sesi** (`presentation/session`). Tombol mulai. Tanpa profil, sesi tidak masuk keadaan mengukur. Bluetooth belum disambungkan; tombol hanya membuka alur yang fase 4 isi.
3. **Riwayat** (`presentation/history`). Daftar kosong bila belum ada baris `measurement`. Membuka hasil tersimpan menyusul di fase 5.

## Langkah

1. Tambah Room, DataStore, Navigation 3, dan plugin serialization ke version catalog. Versi cocok dengan Kotlin `2.2.10`. Jangan menurunkan AGP atau Kotlin. Jangan menambah supabase-kt, OkHttp, atau Retrofit.
2. Entity, DAO, database, dan DataStore seperti di atas. Implementasi `BodyRepository` dan `MeasurementRepository` di `data/repository`.
3. Uji JVM di `app` (bukan emulator): simpan profil, muat baris terbaru, tolak jenis kelamin 2, simpan satu hasil lewat `MeasurementRepository`, baca kembali JSON laporan.
4. Layar profil dan riwayat kosong, serta kunci mulai sesi bila `latest` kosong.

## Pintu keluar

Menyimpan profil, memuat baris terbaru, menolak jenis kelamin selain 0 dan 1, dan sesi tidak mulai tanpa profil.

## Belum dikerjakan

Pemindaian, GATT, daftar indeks, dan `vA019`.
