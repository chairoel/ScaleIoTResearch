# Fase 1 — Parser di modul `app`

Syarat mulai: tidak ada. Kode fase ini sudah ada. Jangan membuat paket `domain.protocol`, dan jangan mengembalikan nama `ScaleBroadcast`.

Sumber perilaku: [iklan_okok.py](../../rumus/iklan_okok.py), [siaran_okok.py](../../rumus/siaran_okok.py), [gatt_okok.py](../../rumus/gatt_okok.py). Peta byte ada di [protokol frame OKOK](../protokol-frame-okok.md).

## Yang ada

Pintu domain, tanpa `android.*`:

- [`ScaleTransmissionRepository`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleTransmissionRepository.kt): `scalePayload`, `payloadFromManufacturer`, `parseTransmission`.
- [`ScaleGattRepository`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleGattRepository.kt): `parseGatt` (buffer baru tiap frame) dan `parse` (buffer sesi).

Model di `domain/model`:

- `ScaleTransmission`. Berat siaran `weightKg` bertipe `Float`.
- `GattResult`, dengan `ScaleGatt` dan `GattConfirmation`. Berat GATT bertipe `Double`.
- `FrameFormatError`. Siaran terenkripsi adalah `EncryptedTransmissionError`, subtipe `FrameFormatError`. `UnsupportedGatt` juga subtipe itu. `IncompleteGatt` bukan subtipe `FrameFormatError`.

Implementasi di `data`, diikat `@Singleton` di [`RepositoryModule`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/RepositoryModule.kt):

- [`ScaleTransmissionRepositoryImpl`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleTransmissionRepositoryImpl.kt) memilih `NativeProtocol.isLoaded`. Header iklan yang diterima disuntik `@ScaleFrameHeaders` dari [`DataModule.scaleHeaders`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/DataModule.kt): `TxConst.HEADER_CA` dan `TxConst.HEADER_C0`.
- Pembaca Kotlin `0xCA`, `0xC0`, dan `0xFF` ada di `data/repository/transmission`. Mereka mengembalikan `RawTransmission`. [`TransmissionMapper`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/TransmissionMapper.kt) yang membangun `ScaleTransmission`.
- [`ScaleGattRepositoryImpl`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt) memegang [`GattParser`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/gatt/GattParser.kt) dari `DataModule` untuk `parse`. `parseGatt` membuat `GattParser` baru. Pembaca frame ada di `data/repository/gatt`. [`GattMapper`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/GattMapper.kt) membangun `ScaleGatt` dan `GattConfirmation`, termasuk penjepit komposisi.
- Konversi berat ada di [`WeightMapper`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/WeightMapper.kt).

[`NativeProtocol`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/NativeProtocol.kt) adalah `internal object` di `data.datasource`. Uji host tidak memanggilnya. Uji memanggil repository.

| Python | Kotlin |
|---|---|
| `muatan_okok`, `muatan_dari_pabrik` | `ScaleTransmissionRepository.scalePayload`, `payloadFromManufacturer` |
| `parse_broadcast`, `SiaranOkok` | `parseTransmission`, `ScaleTransmission` |
| `GattParser`, `parse_gatt`, `GattOkok`, `GattKonfirmasi` | `data/repository/gatt/GattParser`, `parse` / `parseGatt`, `ScaleGatt`, `GattConfirmation` |
| `EncryptedBroadcastError` | `EncryptedTransmissionError` |

Uji ada di `app/src/test/java`, paket `data.protocol` dan `data.repository`:

- `ScaleAdvertisementParserTest`
- `ScaleTransmissionParserTest` (`ParseWeightTest`, `TransmissionTest`)
- `ScaleGattParserTest` (`GattV16Test`, `GattV17Test`, `GattRejectedTest`, `GattAssemblyTest`, `GattRoleTest`)
- `ScaleTransmissionRepositoryImplTest`, `ScaleGattRepositoryImplTest`

Berat siaran yang lewat `_f32` di Python memakai `Float`, bukan `Double`. Siaran `0xC0` ditolak bila bit 7 pada byte offset 4 menyala, untuk frame pendek dan frame yang ditambah enam byte.

## Perilaku yang uji kunci

Vektor hex dan nilai harapan disalin dari uji Python. Jangan menulis vektor baru sebagai pengganti.

1. Iklan, dari `rumus/test_iklan_okok.py`: muatan setelah bendera, UUID di depan data pabrik, pabrik lain dilewati, bukan OKOK, rekaman terpotong, id pabrik little-endian.
2. Berat dan siaran, dari `rumus/test_siaran_okok.py`: kilogram, jin, pon, stone lewat float32, `0xC0` terkunci, `0xC0` terenkripsi, `0xCA` versi 32 terkunci dan belum kunci, versi 17, versi 16, versi lain kosong, cloud, cloud product khusus, frame ditolak.
3. GATT, dari `rumus/test_gatt_okok.py`: versi 16, versi 17 perintah 0 dan 1, frame ditolak, rakitan perintah 18 dan 19, perintah 20 untuk konfirmasi peran.

## Pintu keluar

`./gradlew :app:testDebugUnitTest` lulus untuk berkas uji di atas. Siaran terenkripsi melempar `EncryptedTransmissionError`.

## Belum dikerjakan

Room, DataStore, Compose di luar sapaan templat, izin Bluetooth, dan `vA019`. Rumus `v235` dan `MeasurementSession` sudah ada di [fase 2](fase-02-rumus-v235-mesin-sesi.md).
