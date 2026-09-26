# Hal yang perlu dipahami

Catatan ini menjelaskan apa yang sedang dihadapi dan bagaimana membacanya. Riwayat pekerjaan ada di `activity_log.md`.

Setiap judul bagian memuat waktu pencatatan dalam WIB, format `YYYY-MM-DD HH:mm WIB`. Bagian yang sudah tertulis tidak diubah. Fakta baru atau koreksi ditambah sebagai bagian baru di atas bagian lama. Jika dua bagian bentrok, waktu pencatatan yang lebih baru yang berlaku.

Catatan baru yang menyebut class, method, atau simbol lain dari kode hasil bongkaran menyertakan tautan berkas dan cuplikan. Catatan lama tidak diubah untuk itu. Lokasi berkas untuk nama yang sudah tertulis ada di catatan terbaru dan di `protokol-frame-okok.md`.

## 2026-09-26 07:36 WIB — Rekomendasi berikut: bongkar cs_bias_v235

Langkah berikut: tulis ulang native `cs_bias_v235` di `libchipsea_bias_v235.so`. Pada timbangan yang bukan 8 elektroda, [`CsAlgoBuilder.getBFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) mengembalikan hasil itu ketika `result == 0`. Rumus Java [`getBFR_Raw`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) hanya cadangan.

Syarat 2 tetap butuh satu nilai `data` dari bind, atau entri `okok_scale_encrypted_key_` ditambah MAC. Nilai itu tidak ada di repositori. `libBodyFatScaleAlg.so` dan `libprotocol.so` bukan jalur laporan OKOK ini.

## 2026-09-26 07:36 WIB — Laporan OKOK memakai CsAlgoBuilder

Komposisi pada laporan OKOK dihitung [`CsAlgoBuilder`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) di [`classes4.dex`](../ScaleHealtSource/base/classes4.dex). Konstruktor menerima tinggi, berat, byte jenis kelamin, umur, impedansi `Z`, dan string `rn8`.

Timbangan biasa memanggil [`parseDefaultZ`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java), yang mengisi hasil dari [`cs_bias_v235`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java). Argumennya: jenis kelamin, umur, tinggi dipotong ke int, berat kali 100 dipotong ke int, impedansi kali 10 dipotong ke int. `mBIASV235Success` menyala hanya jika `result == 0` dan `data` tidak null.

```833:841:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    private void parseDefaultZ() {
        LogUtil.i(TAG, "单电阻算法BIASV235");
        float f = this.H;
        int i = this.Age;
        float f2 = this.Wt;
        int i2 = (int) (this.Z * 10.0f);
        byte b = this.Sex;
        LogUtil.i(TAG, "z : " + this.Z + " Age : " + i + " Wt : " + this.Wt + " H : " + this.H + " Sex : " + ((int) this.Sex));
        CSBiasAPI.CSBiasV235Resp cSBiasV235RespCs_bias_v235 = chipsea.bias.v235.CSBiasAPI.cs_bias_v235(b, i, (int) f, (int) (100.0f * f2), i2);
```

[`getBFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) pada tipe frekuensi ganda atau multi mengembalikan field `bfp` dari [`cs_bias_vA019`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java). Pada 8 elektroda ia mengembalikan rumus Java. Pada timbangan lain ia mengembalikan `bfp` native bila bias berhasil, dan rumus Java bila tidak.

```943:960:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getBFR() {
        if (getType() == Type.DualFrequency || getType() == Type.MultiFrequency) {
            LogUtil.i(TAG, "getBfp:" + getBfp());
            return getBfp();
        }
        float bFR_Raw = getBFR_Raw();
        if (bFR_Raw < 5.0f) {
            bFR_Raw = 5.0f;
        }
        if (bFR_Raw > 45.0f) {
            bFR_Raw = 45.0f;
        }
        float fFloatValue = new BigDecimal(bFR_Raw).setScale(2, 4).floatValue();
        if (this.isEightR) {
            return fFloatValue;
        }
        LogUtil.i(TAG, "本地算法和算法库对比 体脂率 : " + fFloatValue + " " + getBfp() + " mBIASV235Success : " + this.mBIASV235Success);
        return this.mBIASV235Success ? getBfp() : fFloatValue;
    }
```

Cadangan Java di [`getBFR_Raw`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java), untuk `isEightR == false`:

- `Sex == 1`: `((-0.3315 * H + 0.6216 * Wt + 0.0183 * Age + 0.0085 * Z + 22.554) / Wt) * 100`
- selain itu: `((-0.3332 * H + 0.7509 * Wt + 0.0196 * Age + 0.0072 * Z + 22.7193) / Wt) * 100`

[`getBMI`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) adalah `(Wt / (H * H)) * 100 * 100`. [`getFM`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) adalah `(getBFR() * Wt) / 100`. [`getTFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) memakai pola penggantian yang sama: native bila bias berhasil, rumus Java bila tidak. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) belum terdekompilasi utuh.

[`Myndk`](../ScaleHealtSource/jadx-protocol/sources/com/example/jnipack/Myndk.java) tidak dipanggil dari `CsAlgoBuilder`. Pemanggilnya adalah [`n.e`](../ScaleHealtSource/jadx-protocol/sources/n/e.java) (`FormulasHelper`, [`classes9.dex`](../ScaleHealtSource/base/classes9.dex)), pada data `XsUserInfo`. Itu jalur XS.

```168:174:ScaleHealtSource/jadx-protocol/sources/n/e.java
    @Deprecated
    public int a(String str, int i2, int i3, XsBodyInfo xsBodyInfo, XsUserInfo xsUserInfo) throws IllegalAccessException, NoSuchFieldException, IllegalArgumentException {
        Info infoA = a(xsUserInfo);
        AlgType algType = new AlgType();
        algType.type = 1;
        algType.algVersion = xsUserInfo.getAlgVersion() == null ? "" : xsUserInfo.getAlgVersion();
        FourElectrodeResult resultFourEleAlg = Myndk.getResultFourEleAlg(infoA, i2, i3, algType);
```

## 2026-09-24 21:06 WIB — Rumus komposisi wajib dibongkar

Syarat 3 di `docs/definisi-selesai.md` mewajibkan rumus komposisi ditulis ulang dari native. Memanggil library aslinya tidak memenuhi syarat selesai cakupan timbangan.

Rumus utama dimuat [`Myndk`](../ScaleHealtSource/jadx-protocol/sources/com/example/jnipack/Myndk.java) dari `libBodyFatScaleAlg.so`. Koreksi bias dimuat [`chipsea.bias.v235.CSBiasAPI`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java) dan [`chipsea.bias.vA019.CSBiasAPI`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java).

```73:75:ScaleHealtSource/jadx-protocol/sources/com/example/jnipack/Myndk.java
    static {
        System.loadLibrary("BodyFatScaleAlg");
    }
```

```6:8:ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java
    static {
        System.loadLibrary("chipsea_bias_v235");
    }
```

```9:11:ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java
    static {
        System.loadLibrary("chipsea_bias_vA019");
    }
```

Bagian “Yang belum tertutup peta ini” di `protokol-frame-okok.md` diselaraskan dengan catatan 23 September 2026 pukul 22:43 WIB: kelas kunci sudah Java. Yang belum ada adalah nilai hex-nya.

Rekomendasi berikut tetap contoh nilai kunci siaran `0xC0`. Itu syarat 2. Pembongkaran rumus adalah syarat 3 dan tidak mengganti langkah itu.

## 2026-09-24 08:55 WIB — Arah proyek: timbangan dulu, lalu aplikasi sendiri

Definisi selesai ada di `docs/definisi-selesai.md`.

Cakupan awal adalah timbangan OKOK. Aplikasi sendiri dimulai setelah cakupan itu selesai dan bisa mengukur. Fitur lain menyusul satu per satu. Membaca seluruh OKOK International bukan syarat untuk mulai membangun.

Rekomendasi berikut tetap contoh nilai kunci siaran `0xC0`. Itu syarat kedua pada cakupan timbangan, dan langkah engineering-nya tidak berubah.

## 2026-09-23 22:43 WIB — Rekomendasi berikut: contoh nilai kunci dari bind

Langkah berikut: ambil satu nilai nyata field `data` pada respons bind, atau entri SharedPreferences `okok_scale_encrypted_key_` ditambah MAC. Itu satu-satunya cara mengetahui bentuk hex yang disimpan.

Kelas kunci sudah didekompilasi. Tidak ada rumus 4 byte di APK. Tanpa contoh nilai itu, siaran `0xC0` terenkripsi tetap menghasilkan berat 0. `libprotocol.so` tetap ditunda sampai targetnya perangkat Xiangshan atau `KAYOFIT_CS8`.

## 2026-09-23 22:43 WIB — Kunci siaran 0xC0 datang dari server

[`OkokScaleEncryptedKeyUtils`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java) ada di [`classes4.dex`](../ScaleHealtSource/base/classes4.dex). [`classes3.dex`](../ScaleHealtSource/base/classes3.dex) hanya memuat pemanggilnya, [`BoundDeviceActivity`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java).

`getOkokScaleEncryptedKeySync` tidak menghitung kunci. Ia membaca SharedPreferences `chipsea`, entri `okok_scale_encrypted_key_` ditambah MAC.

```41:45:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
    public static String getOkokScaleEncryptedKeySync(String str) {
        Context contexts = MyAplication.getContexts();
        if (contexts != null && !TextUtils.isEmpty(str)) {
            try {
                return PrefsUtil.getInstance(contexts.getApplicationContext()).getOkokScaleEncryptedKey(str);
```

```1680:1684:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/PrefsUtil.java
    public String getOkokScaleEncryptedKey(String str) {
        if (TextUtils.isEmpty(str)) {
            return null;
        }
        return getValue("okok_scale_encrypted_key_" + str, (String) null);
```

Pengisian terjadi saat ikat perangkat, hanya jika timbangan terenkripsi. Bind tetap jalan walaupun pengambilan kunci gagal.

```551:556:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java
        ScaleInfo scaleInfo = this.mScaleInfo;
        if (scaleInfo != null && scaleInfo.isEncrypted()) {
            ThreadUtil.executeThread(new Runnable() { // from class: com.chipsea.btcontrol.activity.setting.BoundDeviceActivity$$ExternalSyntheticLambda5
                @Override // java.lang.Runnable
                public final void run() {
                    this.f$0.lambda$toBindCloud$6(runnable);
```

```592:593:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java
    public /* synthetic */ void lambda$toBindCloud$6(final Runnable runnable) {
        com.chipsea.btlib.util.LogUtil.i(TAG, "encryptedKeyGetSuccess : " + OkokScaleEncryptedKeyUtils.getOkokScaleEncryptedKeyFromServerSync(this.mScaleInfo.getMac()));
```

Permintaan GET memakai [`Api.SCALE_ENCRYPTED_KEY_GET`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/Api.java) ditambah MAC tanpa titik dua, huruf kecil. Host rilis adalah `https://intl.chips-cloud.com/v3`. Yang ditulis ke prefs adalah `toString()` dari [`JsonCommonInfo.getData`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/mode/json/JsonCommonInfo.java), dengan MAC asli (bertitik dua). `ApiCallFailInfo` tidak disimpan. `data` null atau string kosong tidak menulis prefs.

```18:18:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
        Object scaleEncryptedKey = new ApiImpl(contexts.getApplicationContext()).getScaleEncryptedKey(str.replace(":", "").toLowerCase(Locale.ENGLISH));
```

```32:32:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
            PrefsUtil.getInstance(contexts.getApplicationContext()).setOkokScaleEncryptedKey(str, string);
```

```155:155:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/Api.java
    public static final String SCALE_ENCRYPTED_KEY_GET = "/device/scale/sn?mac=";
```

```1177:1178:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/ApiImpl.java
    public Object getScaleEncryptedKey(String str) {
        return get(Api.SCALE_ENCRYPTED_KEY_GET + str, null, Api.METHOD_GET);
```

```60:61:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/engine/HttpsEngine.java
            IS_HTTPS = true;
            WEB_IP = "https://intl.chips-cloud.com/v3";
```

```25:26:ScaleHealtSource/jadx-protocol/sources/com/chipsea/mode/json/JsonCommonInfo.java
    public Object getData() {
        return this.data;
```

MAC baca pada frame terenkripsi huruf besar dan bertitik dua, dari [`BytesUtil.bytesToMac`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java). String prefs harus sama persis dengan `chipseaBroadcastFrame.mac`.

```271:271:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
        return !TextUtils.isEmpty(string) ? string.toUpperCase(Locale.ENGLISH) : string;
```

Peta lengkap ada di `docs/protokol-frame-okok.md`.

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
