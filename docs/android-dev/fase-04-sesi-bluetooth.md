# Fase 4 — Sesi Bluetooth

Syarat mulai: pintu keluar [fase 3](fase-03-profil-room.md).

Sumber perilaku: [sesi_ble.py](../../aplikasi/sesi_ble.py) dan `HealthTrack/.cursor/rules/bluetooth.mdc`. UUID dari [`BtGattAttr`](../../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/BtGattAttr.java):

```44:46:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/BtGattAttr.java
        CHIPSEA_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb";
        CHIPSEA_CHAR_RX_UUID = "0000fff1-0000-1000-8000-00805f9b34fb";
        CHIPSEA_CHAR_TX_UUID = "0000fff2-0000-1000-8000-00805f9b34fb";
```

Sesi tidak menulis ke TX. UUID itu tidak diganti.

## Yang dihasilkan

Di `app/.../data/datasource/`:

- [`BleDataSource`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleDataSource.kt) — satu kontrak pindai dan GATT. `startScan` mengembalikan `Flow<BleScanEvent>`. `connect` mengembalikan `Flow<BleConnectEvent>`. Null bila radio atau izin menolak. Uji host sesi menyuntik `ScaleRadioRepository`, bukan kelas platform ini.
- [`BleDataSourceImpl`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleDataSourceImpl.kt) — satu implementasi. `BluetoothLeScanner` dan `BluetoothGatt`. Ini yang boleh mengimpor API platform. [`DataSourceModule`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/DataSourceModule.kt) mengikatnya ke `BleDataSource`.

Peristiwa radio ada di [`BleEvent.kt`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt). `BleManufacturerBlock.remainder`, `BleScanEvent.Advertisement.record`, dan `BleConnectEvent.Notification.value` bertipe `List<Byte>`.

[`ScaleRadioRepository`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleRadioRepository.kt) di `domain/repository` adalah pintu radio. Metodenya `begin`, `startScan` (Boolean), `stopScan`, `connect` (epoch), `disconnect`, `awaitEvent`, dan `end`. Pintu ini tidak mengembalikan `Flow`. [`ScaleRadioRepositoryImpl`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleRadioRepositoryImpl.kt) mengumpulkan flow `BleDataSource`, memilih blok timbangan, dan mengirim [`ScaleRadioEvent`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleRadioEvent.kt). `remainder` dan `value` diubah dengan `toByteArray()` sebelum parser. `ScaleAdvertisement.payload` dan `ScaleNotification.value` bertipe `ByteArray`. Kelas itu tidak memanggil use case.

[`MeasureScaleUseCase`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/MeasureScaleUseCase.kt) adalah kelas konkret, sama seperti use case lain. `invoke` mengembalikan `Flow<ScaleSessionStatus>`. Kelas itu menunggu `awaitEvent`, lalu [`ScaleFrames`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/ScaleFrames.kt) memanggil `AcceptTransmissionUseCase`, `AcceptGattUseCase`, dan `ApplyBroadcastWeightUseCase`. Teks keadaan memakai `MeasurementStateUseCase`. Batas 15 detik, tiga percobaan, dua putaran, dan batas sesi 120 detik ada di `MeasureScaleUseCase`. [`UseCaseModule`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/di/UseCaseModule.kt) menyediakan kelas itu. `ScaleFrames` dibuat di dalam `MeasureScaleUseCase`, satu instance per sesi, dan tidak mengimpor `android.*`. Tanda frame berulang, `BroadcastSign` dan `GattSign`, adalah kelas privat di berkas itu. Hex siaran dan hex GATT dihitung di situ, huruf kecil tanpa pemisah.

`presentation/session` memegang status. ViewModel menyuntik `MeasureScaleUseCase`. Keadaan ukur ada di `MeasurementSession`. Cuplikan yang tampil ada di `ScaleSessionStatus`. ViewModel tidak mengimpor `BluetoothGatt`. Sesi yang selesai mengirim `FinishedSession` dan membuka `ResultRoute`.

`menerima_sambungan` di Python membaca `kCBAdvDataIsConnectable` milik CoreBluetooth. Di Android tandanya `ScanResult.isConnectable()`. Pengurai `platform_data` macOS tidak dipindahkan.

Alamat yang disimpan adalah MAC radio (`ScanResult.device.address`).

## Urutan satu sesi

1. Izin sudah diberikan dan Bluetooth menyala. Sesi berjalan di Activity yang terlihat. Layar tetap menyala (`FLAG_KEEP_SCREEN_ON`) selama sesi. Foreground service tidak dipakai.
2. Muatan iklan: company id 16-bit little-endian ditambah sisa byte pabrik, diterima bila byte pertama `0xCA` atau `0xC0`. Rekam pemindaian dibaca sampai habis. Pembacaan muatan memakai `ScaleTransmissionRepository`, bukan parser baru.
3. Simpan alamat siaran OKOK pertama. Iklan lain diabaikan setelah alamat itu terpasang.
4. Sambungan dimulai pada siaran OKOK pertama yang `isConnectable()` benar. Kunci impedansi bukan syarat sambungan.
5. Hentikan pemindaian, lalu `connectGatt(autoConnect = false)`. Pemindaian dan `connectGatt` tidak berjalan bersamaan.
6. Temukan layanan Chipsea, pasang notify pada RX, tulis descriptor CCCD, lalu nyalakan pemindaian lagi supaya impedansi terkunci tetap masuk.
7. Tiga percobaan sambungan, batas 15 detik, lalu paling banyak dua putaran pindai. Sesi berakhir pada 120 detik atau saat hasil tersimpan.
8. Bila waktu sambungan habis, layar memberitahu bahwa aplikasi OKOK di ponsel perlu ditutup bila timbangan sedang tersambung di sana.
9. Iklan yang tidak bisa disambung menutup sesi lewat `ApplyBroadcastWeightUseCase`. Berat GATT yang sudah masuk tidak diganti.
10. Siaran terenkripsi (`EncryptedTransmissionError`) menampilkan pesan di layar sesi dan tidak masuk rumus.

Pesan ke pengguna memakai `AppError` di `presentation/common/model`.

Mode sumber `Alway_Conn` untuk ponsel Xiaomi yang `DEVICE`-nya diawali `HM` tidak mengubah `autoConnect` pada tahap ini. Kalimat Android di rencana memakai `autoConnect = false`.

## Izin

- API 28–30: `BLUETOOTH`, `BLUETOOTH_ADMIN`, dan `ACCESS_FINE_LOCATION` saat memindai. Ketiganya `maxSdkVersion` 30.
- API 31+: `BLUETOOTH_SCAN` dengan `neverForLocation`, dan `BLUETOOTH_CONNECT`.
- Daftar runtime ada di [`BluetoothAccess`](../../HealthTrack/app/src/main/java/com/mascill/healthtrack/presentation/session/BluetoothAccess.kt). Izin diminta di layar sesi, sebelum pindai.

## Layar sesi

Status: `menunggu impedansi`, `menunggu berat`, `selesai`, atau kode rumus. Berat yang bergerak ikut tampil. Pesan siaran terenkripsi dan pesan waktu sambungan habis tampil di sini.

Layar hasil (`presentation/result`, `ResultRoute`) menampilkan berat, daftar indeks dari fungsi pembulatan [fase 2](fase-02-rumus-v235-mesin-sesi.md), hex siaran terakhir, dan hex GATT terakhir. Tanpa daftar itu, banding di timbangan tidak bisa ditutup. Angka tidak dihitung ulang di Compose. Sesi yang baru selesai mengisi tinggi dan hex pada rute itu. Riwayat di [fase 5](fase-05-hasil-riwayat.md) membuka baris yang sama dengan `measurementId` saja; hex kosong tampil `tidak ada`.

## Uji host sebelum timbangan

Uji host ada di `ScaleFramesTest` dan `MeasureScaleUseCaseTest`, disalin dari `PendengarSesiTest` di `aplikasi/test_sesi_ble.py`:

- iklan lalu GATT menutup sesi
- perangkat lain diabaikan
- sambungan boleh begitu siaran terbaca, termasuk sebelum impedansi terkunci
- siaran tidak connectable menutup berat
- siaran berulang tidak mengulang pesan

`test_tanda_sambungan_iklan` dan `test_perintah_sesi_tanpa_profil` tidak dipindahkan. Yang pertama milik CoreBluetooth. Yang kedua milik perintah Python; kunci tanpa profil sudah ditutup di fase 3.

## Pintu keluar

Di timbangan yang sama dengan uji 27 Sep 2026, pada siaran tidak terenkripsi: berat dan daftar indeks cocok dengan aplikasi OKOK. Bila iklan tidak connectable, berat siaran terkunci tetap menghasilkan laporan. Hex siaran dan hex GATT terakhir tampil di layar hasil. Profil uji banding itu tinggi 166 cm, umur 29, kelamin 1, bila sesi yang dibandingkan adalah sesi 68,7 kg.

## Di luar fase ini

Riwayat yang membuka hasil lama ada di [fase 5](fase-05-hasil-riwayat.md). `vA019` masih [fase 6](fase-06-frekuensi-ganda.md). Banding 18 Okt 2026 pada 68,95 kg, tinggi 166 cm, laki-laki, 600 ohm cocok dengan v235. OKOK memakai umur 29 dari tanggal lahir. Aplikasi ini memakai umur 30 yang diketik.
