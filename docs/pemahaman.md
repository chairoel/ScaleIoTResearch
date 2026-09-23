# Hal yang perlu dipahami

Catatan ini menjelaskan apa yang sedang dihadapi dan bagaimana membacanya. Riwayat pekerjaan ada di `activity_log.md`.

Setiap judul bagian memuat waktu pencatatan dalam WIB, format `YYYY-MM-DD HH:mm WIB`. Bagian yang sudah tertulis tidak diubah. Fakta baru atau koreksi ditambah sebagai bagian baru di atas bagian lama. Jika dua bagian bentrok, waktu pencatatan yang lebih baru yang berlaku.

Catatan baru yang menyebut class, method, atau simbol lain dari kode hasil bongkaran menyertakan tautan berkas dan cuplikan. Catatan lama tidak diubah untuk itu. Lokasi berkas untuk nama yang sudah tertulis ada di catatan terbaru dan di `protokol-frame-okok.md`.

## 2026-09-23 22:18 WIB — Berkas untuk nama class yang sudah disebut

Cuplikan layout frame OKOK ada di `docs/protokol-frame-okok.md`. Tiap parser di sana menaut ke berkas Java dan mengutip barisnya.

Nama class pada catatan sebelum ini berada di berkas berikut.

| Nama | Berkas |
|---|---|
| `CSApplication` | [`AndroidManifest.decoded.txt`](../ScaleHealtSource/base/AndroidManifest.decoded.txt) baris 167. Belum ada Java. |
| `com.chipsea.shell.MainActivity` | manifest yang sama, baris 178. Belum ada Java. |
| `com.chipsea.btcontrol.activity.MainActivity` | manifest yang sama, baris 414. Belum ada Java. |
| `BluetoothLeScannerCompat.getProtocalTypeByBroadcast` | [`BluetoothLeScannerCompat.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java) |
| `CsBtUtil_v11.Protocal_Type` | [`CsBtUtil_v11.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java) |
| `straightFrameFactory` | [`straightFrameFactory.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/straightFrameFactory.java) |
| `chipseaBroadcastFrame`, `chipseaStraightFrame` | folder [`protocal/`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/) |
| `XSBleAdvParser` | [`XSBleAdvParser.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/xsdevice/XSBleAdvParser.java) |
| `LeFuScaleManager` | [`LeFuScaleManager.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/lefu/LeFuScaleManager.java) |
| `OkokFoodScaleProtocol` | [`OkokFoodScaleProtocol.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/nutriscale/connection/protocol/okok/OkokFoodScaleProtocol.java) |
| `xincore` | [`XinCoreProtocol.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/wearable/connection/protocol/xincore/XinCoreProtocol.java) |
| `com.lstech.ble` | [`sources/com/lstech/ble/`](../ScaleHealtSource/jadx-protocol/sources/com/lstech/ble/) |
| `Protocol` / `libprotocol.so` | [`Protocol.java`](../ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java) dan [`libprotocol.so`](../ScaleHealtSource/split_config.arm64_v8a/lib/arm64-v8a/libprotocol.so) |
| `Myndk` | [`Myndk.java`](../ScaleHealtSource/jadx-protocol/sources/com/example/jnipack/Myndk.java) |
| `chipsea.bias.v235.CSBiasAPI` | [`v235/CSBiasAPI.java`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java) |
| `chipsea.bias.vA019.CSBiasAPI` | [`vA019/CSBiasAPI.java`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java) |
| `Authorization` | [`Authorization.java`](../ScaleHealtSource/jadx-protocol/sources/com/lstech/auth/Authorization.java) |
| `OkokScaleEncryptedKeyUtils` | belum jadi Java. Titik panggil: [`ScaleEncryptedKeyUtils.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/ScaleEncryptedKeyUtils.java). String nama class ada di [`classes3.dex`](../ScaleHealtSource/base/classes3.dex) dan [`classes4.dex`](../ScaleHealtSource/base/classes4.dex). |

`parseScan` tidak dipanggil dari isi method `SdkPresenter`. Instance `Protocol` ada di [`SdkPresenter`](../ScaleHealtSource/jadx-protocol/sources/com/ss/bluetooth/sscore/SdkPresenter.java), dan pemanggilan `parseScan` ada di [`XsBluetoothManager`](../ScaleHealtSource/jadx-protocol/sources/com/ss/bluetooth/sscore/XsBluetoothManager.java). `parseData` dan `getFuncBuffer` hanya deklarasi native di `Protocol.java`. Di `jadx-protocol` tidak ada pemanggil Java untuk keduanya.

```7:9:ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java
    static {
        System.loadLibrary("protocol");
    }
```

```18:18:ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java
    public native byte[] getFuncBuffer(String str, String str2, String str3);
```

```24:26:ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java
    public native void parseData(String str, byte[] bArr, int i);

    public native DeviceInfo parseScan(byte[] bArr, String str);
```

```85:86:ScaleHealtSource/jadx-protocol/sources/com/ss/bluetooth/sscore/XsBluetoothManager.java
    public boolean isXsDevice(byte[] bArr, String str) {
        return SdkPresenter.getInstance().protocol.parseScan(bArr, str) != null;
```

```109:110:ScaleHealtSource/jadx-protocol/sources/com/ss/bluetooth/sscore/XsBluetoothManager.java
    public DeviceInfo parseDevice(byte[] bArr, String str) {
        return SdkPresenter.getInstance().protocol.parseScan(bArr, str);
```

## 2026-09-23 22:00 WIB — Rekomendasi berikut: kunci siaran OKOK terenkripsi

Langkah berikut: dekompilasi `com.chipsea.code.util.OkokScaleEncryptedKeyUtils` dari `classes3.dex` dan `classes4.dex`.

Kelas itu yang memasok kunci 4 byte untuk berat dan impedansi pada siaran header `0xC0`. Tanpa kelas ini, frame terenkripsi hanya menghasilkan berat 0. `libprotocol.so` belum dibuka: itu jalur perangkat XS, dan dikerjakan hanya jika targetnya Xiangshan atau `KAYOFIT_CS8`.

## 2026-09-23 22:00 WIB — Layout frame OKOK

Peta field ada di `docs/protokol-frame-okok.md`.

Siaran `0xCA` versi biasa hanya membawa berat dan product id. Komposisi tubuh (lemak, air, otot, BMR, lemak visceral, tulang) ada di GATT `chipseaStraightFrame`: versi 16 dalam satu paket, versi 17 perintah 18 dan 19 dalam beberapa paket. Impedansi `r1` ada di siaran versi `0x20` dan siaran `0xC0`, bukan di parser GATT itu.

`chipseaBroadcastFrame` dan `chipseaStraightFrame` tidak memeriksa XOR saat menerima. XOR diperiksa di `com.chipsea.btlib.model.Frame`, dan kelas itu hanya dipakai parser lama `CsBtUtil`. Perintah ponsel ke timbangan di `syncChipseaInstruction` tetap menaruh XOR di byte terakhir data.

## 2026-09-23 21:16 WIB — Aplikasi yang dibongkar

Sumbernya adalah aplikasi OKOK International, paket `com.chipsea.btcontrol.en`, versi **3.1.66** (versionCode 173), dikompilasi untuk Android SDK 36. Ini aplikasi timbangan kesehatan Chipsea, bukan proyek ScaleIoT sendiri.

Aplikasi ini mengurus lebih dari satu produk:

- Timbangan berat dan komposisi tubuh
- Timbangan dapur / nutrisi (`nutriscale`)
- Catatan minum air (`waterdrink`)
- Olahraga, laporan, widget, dan langganan VIP

Titik masuk proses adalah `com.chipsea.btcontrol.CSApplication`. Ikon launcher membuka `com.chipsea.shell.MainActivity`. Layar utama aplikasi ada di `com.chipsea.btcontrol.activity.MainActivity`. Keduanya berbeda dan jangan dicampur.

## 2026-09-23 21:16 WIB — Bentuk file sumber

`OKOK international.apk` bukan satu APK. Itu wadah split APK dengan header `MID`, berisi tiga berkas:

| Berkas | Peran |
|---|---|
| `base.apk` | Kode, manifest, resource umum, dan aset |
| `split_config.arm64_v8a.apk` | Library native khusus CPU ARM 64-bit |
| `split_config.xxhdpi.apk` | Gambar untuk kerapatan layar xxhdpi |

Hanya ABI `arm64-v8a` dan kerapatan `xxhdpi` yang ada di file ini. Perangkat dengan CPU atau kerapatan lain tidak terwakili di hasil bongkaran.

`unzip` langsung ke file induk gagal dibaca utuh karena setelah ZIP pertama masih ada split berikutnya. Tiap split harus dipotong dulu, baru diekstrak.

## 2026-09-23 21:16 WIB — Apa yang sudah terbaca, dan apa yang belum

Hasil di `ScaleHealtSource` adalah isi arsip, bukan kode sumber.

- `AndroidManifest.xml` di dalam `base` masih XML biner Android. Yang bisa dibaca manusia adalah `AndroidManifest.decoded.txt` dan `badging.txt`.
- `classes.dex` sampai `classes10.dex` masih bytecode. Belum ada Java atau Smali. `classes2.dex` jauh lebih kecil dari yang lain (sekitar 5 KB), jadi isinya hampir pasti bukan modul utama.
- Resource gambar, layout, dan string sebagian besar masih dalam bentuk resource Android (`resources.arsc` dan `res/`), belum berupa proyek yang bisa dibuka di Android Studio.
- Library `.so` ada di `split_config.arm64_v8a/lib/arm64-v8a/`, bukan di dalam folder `base`.

Folder `ScaleHealtSource` dan APK asli diabaikan Git lewat `.gitignore`.

## 2026-09-23 21:27 WIB — Di mana logika penting berada

Timbangan tidak punya satu parser. Ada jalur Java untuk keluarga OKOK, dan jalur native terpisah untuk perangkat Xiangshan (XS). Rumus komposisi tubuh tetap di native.

Sumber Java hasil dekompilasi jalur ini ada di `ScaleHealtSource/jadx-protocol` (235 berkas). Itu bukan seluruh aplikasi: layar, akun, dan iklan belum didekompilasi.

| Library | Kelas yang memuatnya | Peran |
|---|---|---|
| `libprotocol.so` | `com.xshq.sdk.Protocol` | Parser native perangkat XS. Dipakai `com.ss.bluetooth.sscore.SdkPresenter`. Method penting: `parseScan`, `parseData`, `getFuncBuffer`. |
| `libBodyFatScaleAlg.so` | `com.example.jnipack.Myndk` | Perhitungan komposisi tubuh (4 elektroda, 8 elektroda, arus searah). |
| `libchipsea_bias_v235.so` | `chipsea.bias.v235.CSBiasAPI` | Koreksi bias, keluarga v235. |
| `libchipsea_bias_vA019.so` | `chipsea.bias.vA019.CSBiasAPI` | Koreksi bias, keluarga vA019. |
| `libdevice_auth.so` | `com.lstech.auth.Authorization` | Autentikasi perangkat (`getAuthKeyFromNative`). |
| `libpdfium*.so` | — | Pratinjau PDF, bukan protokol timbangan. |
| `libumeng-spy.so`, `libpglarmor.so`, `libnms.so` | — | SDK pihak ketiga (analitik, iklan, pelindung). Bukan inti produk timbangan. |

## 2026-09-23 21:27 WIB — Dua jalur protokol timbangan

Jenis protokol dipilih saat scan, di `com.chipsea.btlib.scanner.BluetoothLeScannerCompat.getProtocalTypeByBroadcast`. Enum-nya `CsBtUtil_v11.Protocal_Type`.

| Jenis | Cara dikenali dari iklan BLE | Parser |
|---|---|---|
| `OKOK` | Manufacturer byte `0xCA` atau `0xC0` | Java: `chipseaBroadcastFrame`, koneksi GATT `chipseaStraightFrame` |
| `OKOKCloud` | Manufacturer `0xFF 0xF0`, versi bukan 16/17 | Java: `okCloudStraightFrame` |
| `OKOKCloudV4` | Manufacturer `0xFF 0xF0`, versi 16 atau 17 | Java: `okCloudV4StraightFrame` |
| `ALIBABA` | Manufacturer `0xA8 0x01` | Java: `aliStraightFrame` |
| `JD` | UUID `0x18 0xD6` | Java: `jdStraightFrame` |
| `LEXIN` | UUID `0x02 0xA6` | Java: `lxStraightFrame` |
| `LEAONE` | Nama diawali `lnv_111` atau `lnv_112` | Java: `leaoneStraightFrame` |
| `LEFU` | Nama lolos `LeFuScaleManager.isBelongToLeFuScale1` | Java: `LeFuScaleManager` |
| `XS` / `XS_SUB_1` | `XSBleAdvParser`. `XS_SUB_1` khusus nama `KAYOFIT_CS8` | Native `libprotocol.so` lewat `com.ss.bluetooth` |

Frame GATT keluarga Chipsea (bukan XS) berawalan `0xCA`. Byte kedua adalah versi, byte ketiga panjang data, byte terakhir XOR. Versi 16 pada `chipseaStraightFrame` sudah memuat berat, lemak, air, otot, BMR, lemak visceral, dan tulang di Java.

`straightFrameFactory` hanya membuat parser OKOK, JD, OKOKCloud, OKOKCloudV4, ALIBABA, LEXIN, dan LEAONE. LEFU dan XS tidak lewat factory itu.

Produk lain punya protokol sendiri dan jangan dicampur dengan timbangan berat:

- Dapur: `com.chipsea.btcontrol.nutriscale.connection.protocol.okok.OkokFoodScaleProtocol`
- Wearable: `com.chipsea.wearable.connection.protocol.xincore`
- Tali skipping: `com.lstech.ble`

## 2026-09-23 21:27 WIB — Peta modul dari manifest

Dari 292 komponen, 196 milik `com.chipsea`. Ikon launcher membuka `com.chipsea.shell.MainActivity`. Layar utama aplikasi adalah `com.chipsea.btcontrol.activity.MainActivity`.

Modul yang terlihat dari activity: timbangan berat dan laporan, dapur (`nutriscale`), minum air (`waterdrink`), olahraga, wearable, tali (`rope`), puasa, VIP, dan akun. Service milik Chipsea hanya lima: widget, musik, pembaruan (`UpdataServer`), pengingat, dan pengingat puasa. Tidak ada service BLE yang didaftarkan di manifest; pemindaian hidup di kode `com.chipsea.btlib`, bukan sebagai service manifest.

Di `assets/` ada animasi timbangan, font, HTML, dan tiga berkas `*_skin_pack_*.apk` (green, pink, purple). Berkas skin itu paket tampilan yang dibawa di dalam aplikasi, bukan APK utama dan bukan split CPU.

## 2026-09-23 21:16 WIB — Izin yang menjelaskan perilaku

Izin Bluetooth (`BLUETOOTH_SCAN`, `BLUETOOTH_CONNECT`, plus izin lama `BLUETOOTH`) menegaskan hubungan ke perangkat lewat BLE. Izin lokasi menyertai pemindaian Bluetooth di Android lama. Izin kamera dan media dipakai alur makanan (foto dan barcode). Izin billing dipakai alur VIP. Izin ini menggambarkan kemampuan aplikasi, bukan bukti bahwa setiap izin dipakai pada setiap layar.

## 2026-09-23 21:27 WIB — Urutan memahami yang masuk akal

1. Peta manifest `com.chipsea` sudah dibaca.
2. DEX jalur timbangan sudah didekompilasi ke `ScaleHealtSource/jadx-protocol`. Layar dan akun belum.
3. Langkah berikut untuk protokol XS: telusuri `libprotocol.so` lewat `parseScan`, `parseData`, dan `getFuncBuffer`. Frame OKOK bisa dilanjutkan dari `chipseaBroadcastFrame` dan `chipseaStraightFrame` tanpa membuka `.so`.
4. Library iklan, analitik, dan PDF tetap kode pendukung.

Nama class di manifest untuk layar yang belum didekompilasi masih petunjuk, bukan bukti isi implementasinya.
