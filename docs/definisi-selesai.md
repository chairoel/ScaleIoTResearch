# Definisi selesai

Dokumen ini menetapkan kapan suatu cakupan boleh disebut selesai, dan kapan pembangunan aplikasi sendiri dimulai.

Fakta hasil bongkaran ada di `pemahaman.md`. Peta byte timbangan ada di `protokol-frame-okok.md`. Riwayat pekerjaan ada di `activity_log.md`.

## Arah

ScaleIoT membangun aplikasi sendiri. OKOK International 3.1.66 (`com.chipsea.btcontrol.en`) adalah bahan untuk memahami perilaku timbangan dan, pada tahap kemudian, fitur lain.

Urutan yang dipakai:

1. Selesaikan cakupan timbangan, dengan syarat di bawah.
2. Bangun aplikasi sendiri untuk satu sesi ukur.
3. Setelah aplikasi itu bisa mengukur, tiap fitur lain dibongkar secukupnya lalu dibangun.

Pembongkaran seluruh OKOK International selesai dibaca bukan syarat untuk mulai membangun. Tiap modul produk lain punya protokol sendiri. Uji di timbangan nyata adalah pemeriksaan yang membuktikan peta frame. Menunda uji sampai seluruh DEX terbaca menunda pemeriksaan itu.

## Cakupan awal: timbangan

Selesai ketika empat syarat ini terpenuhi.

1. Parser siaran dan GATT keluarga OKOK cukup untuk berat, impedansi, dan komposisi pada versi yang sudah dipetakan di `protokol-frame-okok.md`.
2. Ada satu contoh nilai kunci siaran `0xC0`, atau keputusan tertulis bahwa timbangan terenkripsi tidak masuk rilis pertama. [`OkokScaleEncryptedKeyUtils.getOkokScaleEncryptedKeySync`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java) hanya membaca prefs. Empat byte itu tidak dihitung di APK.

```41:45:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
    public static String getOkokScaleEncryptedKeySync(String str) {
        Context contexts = MyAplication.getContexts();
        if (contexts != null && !TextUtils.isEmpty(str)) {
            try {
                return PrefsUtil.getInstance(contexts.getApplicationContext()).getOkokScaleEncryptedKey(str);
```

3. Rumus komposisi sudah terbaca dari native dan bisa ditulis ulang. Rumus utama ada di [`Myndk`](../ScaleHealtSource/jadx-protocol/sources/com/example/jnipack/Myndk.java), yang memuat `libBodyFatScaleAlg.so`. Koreksi bias ada di [`chipsea.bias.v235.CSBiasAPI`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java) (`libchipsea_bias_v235.so`) dan [`chipsea.bias.vA019.CSBiasAPI`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java) (`libchipsea_bias_vA019.so`). Memanggil ketiga library itu dari aplikasi sendiri tidak memenuhi syarat ini.

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

4. Satu sesi ukur di perangkat nyata. Keluaran aplikasi sendiri cocok dengan aplikasi sumber pada timbangan yang sama, untuk berat dan untuk komposisi dari rumus yang ditulis ulang.

`libprotocol.so` masuk cakupan ini hanya jika targetnya perangkat Xiangshan atau `KAYOFIT_CS8`. Parser itu [`Protocol.parseScan`](../ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java).

```7:9:ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java
    static {
        System.loadLibrary("protocol");
    }
```

```24:26:ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java
    public native void parseData(String str, byte[] bArr, int i);

    public native DeviceInfo parseScan(byte[] bArr, String str);
```

Langkah engineering yang masih berlaku untuk syarat 2 ada di rekomendasi terbaru `pemahaman.md`: satu nilai `data` dari bind, atau entri `okok_scale_encrypted_key_` ditambah MAC.

## Aplikasi sendiri, tahap pertama

Dimulai setelah cakupan timbangan selesai.

Isi tahap ini: kenali siaran OKOK, baca berat, sambung GATT, hitung komposisi dari rumus yang sudah ditulis ulang, simpan hasil ukur, dan simpan data tubuh yang rumus butuhkan (tinggi, umur, jenis kelamin).

Di luar tahap ini: dapur (`nutriscale`), minum (`waterdrink`), olahraga, wearable, tali, puasa, VIP, iklan, dan akun di server Chipsea. Aplikasi sendiri menyimpan hasil ukurnya sendiri.

## Cakupan kemudian

Setelah tahap pertama bisa mengukur, tiap fitur lain mengikuti pola yang sama: alur klien modul itu terbaca, kebutuhan modul itu diketahui, fitur ada di aplikasi sendiri, lalu lolos uji banding pada skenario modul itu.

Seluruh perilaku OKOK International yang dipakai untuk pengguna timbangan kesehatan disebut selesai ketika setiap modul produk itu punya padanan yang lolos uji tersebut. SDK iklan, analitik, dan PDF tetap di luar.

Membongkar `classes.dex` sampai habis, atau mengemas ulang APK sumber, tidak memenuhi definisi di dokumen ini.
