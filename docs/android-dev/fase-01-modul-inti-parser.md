# Fase 1 — Parser di modul `app`

Syarat mulai: belum ada. Ini fase pertama.

Sumber perilaku: [iklan_okok.py](../../rumus/iklan_okok.py), [siaran_okok.py](../../rumus/siaran_okok.py), [gatt_okok.py](../../rumus/gatt_okok.py). Peta byte ada di [protokol frame OKOK](../protokol-frame-okok.md).

## Yang dihasilkan

Paket di modul `app` yang sudah ada: `com.mascill.healthtrack.domain.protokol`. Berkas ada di `app/src/main/java`. Uji ada di `app/src/test/java`. Paket ini tidak mengimpor `android.*`. Modul Gradle lain tidak ditambah. `settings.gradle.kts` tetap hanya `include(":app")`.

| Python | Kotlin |
|---|---|
| `muatan_okok`, `muatan_dari_pabrik` | `IklanOkok.kt` |
| `parse_broadcast`, `parse_weight`, `SiaranOkok` | `SiaranOkok.kt` |
| `GattParser`, `parse_gatt`, `GattOkok`, `GattKonfirmasi` | `GattOkok.kt` |

Kesalahan format dan siaran terenkripsi punya tipe sendiri. Siaran terenkripsi adalah subtipe kesalahan format, sama seperti `EncryptedBroadcastError` terhadap `FrameFormatError`. Uji menolak siaran `0xC0` bila bit 7 pada byte offset 4 menyala, untuk frame pendek dan frame yang ditambah enam byte.

Berat siaran yang lewat `_f32` di Python memakai `Float`, bukan `Double`.

## Langkah

1. Pastikan `./gradlew :app:testDebugUnitTest` jalan pada modul `app` yang sudah ada.
2. Pindahkan iklan. Uji dari `rumus/test_iklan_okok.py`: muatan setelah bendera, UUID di depan data pabrik, pabrik lain dilewati, bukan OKOK, rekaman terpotong, id pabrik little-endian.
3. Pindahkan parser berat dan siaran. Uji dari `rumus/test_siaran_okok.py`: kilogram, jin, pon, stone lewat float32, `0xC0` terkunci, `0xC0` terenkripsi, `0xCA` versi 32 terkunci dan belum kunci, versi 17, versi 16, versi lain kosong, cloud, cloud product khusus, frame ditolak.
4. Pindahkan GATT, termasuk rakitan perintah 18 dan 19 serta perintah 20 untuk konfirmasi peran. Uji dari `rumus/test_gatt_okok.py`: versi 16, versi 17 perintah 0 dan 1, frame ditolak, rakitan, dan peran.

Vektor hex dan nilai harapan disalin dari uji Python. Jangan menulis vektor baru sebagai pengganti.

## Pintu keluar

`./gradlew :app:testDebugUnitTest` lulus untuk ketiga berkas uji di atas. Siaran terenkripsi melempar tipe yang setara `EncryptedBroadcastError`.

## Belum dikerjakan

Rumus, `SesiUkur`, Room, DataStore, Compose, izin Bluetooth, dan `vA019`.
