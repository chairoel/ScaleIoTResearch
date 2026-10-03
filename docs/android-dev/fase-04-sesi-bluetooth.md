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

Di `app/.../data/ble/`:

- `SessionListener` — meneruskan muatan iklan dan notify ke `AcceptTransmissionUseCase` dan `AcceptGattUseCase` lewat `ScaleTransmissionRepository` dan `ScaleGattRepository`. Tidak mengimpor `android.*`, supaya uji host dari `aplikasi/test_sesi_ble.py` bisa jalan di `:app:testDebugUnitTest`.
- `BleSession` — `BluetoothLeScanner` dan `BluetoothGatt`. Ini yang boleh mengimpor API platform.

`presentation/session` memegang status. ViewModel menyuntik `ScaleSessionRepository` di `domain/repository`. Implementasinya di `data` memegang `BleSession` dan memanggil use case sesi. Keadaan ada di `MeasurementSession`. ViewModel tidak mengimpor `BluetoothGatt`.

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

- API 28–30: `BLUETOOTH`, `BLUETOOTH_ADMIN`, dan `ACCESS_FINE_LOCATION` saat memindai.
- API 31+: `BLUETOOTH_SCAN` dan `BLUETOOTH_CONNECT`.
- Izin runtime diminta di layar sesi, sebelum pindai.

## Layar sesi

Status: `menunggu impedansi`, `menunggu berat`, `selesai`, atau kode rumus. Berat yang bergerak ikut tampil. Pesan siaran terenkripsi dan pesan waktu sambungan habis tampil di sini.

Layar hasil (`presentation/result`, `ResultRoute`) pada fase ini menampilkan berat, daftar indeks dari fungsi pembulatan [fase 2](fase-02-rumus-v235-mesin-sesi.md), hex siaran terakhir, dan hex GATT terakhir. Tanpa daftar itu, banding di timbangan tidak bisa ditutup. Angka tidak dihitung ulang di Compose. Riwayat yang membuka hasil lama menyusul di fase 5.

## Uji host sebelum timbangan

Salin dari `PendengarSesiTest` di `aplikasi/test_sesi_ble.py`:

- iklan lalu GATT menutup sesi
- perangkat lain diabaikan
- sambungan boleh begitu siaran terbaca, termasuk sebelum impedansi terkunci
- siaran tidak connectable menutup berat
- siaran berulang tidak mengulang pesan

`test_tanda_sambungan_iklan` dan `test_perintah_sesi_tanpa_profil` tidak dipindahkan. Yang pertama milik CoreBluetooth. Yang kedua milik perintah Python; kunci tanpa profil sudah ditutup di fase 3.

## Pintu keluar

Di timbangan yang sama dengan uji 27 Sep 2026, pada siaran tidak terenkripsi: berat dan daftar indeks cocok dengan aplikasi OKOK. Bila iklan tidak connectable, berat siaran terkunci tetap menghasilkan laporan. Hex siaran dan hex GATT terakhir tampil di layar hasil. Profil uji banding itu tinggi 166 cm, umur 29, kelamin 1, bila sesi yang dibandingkan adalah sesi 68,7 kg.

## Belum dikerjakan

Riwayat yang membuka hasil lama, dan `vA019`.
