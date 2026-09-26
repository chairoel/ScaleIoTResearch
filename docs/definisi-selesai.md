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

Keputusan rilis pertama: timbangan terenkripsi tidak masuk rilis pertama. Bit enkripsi adalah bit 7 pada byte offset 4 siaran `0xC0`. Repositori tidak memuat nilai `data` dari bind maupun entri `okok_scale_encrypted_key_`. Siaran `0xCA`, siaran `0xC0` tanpa bit itu, dan GATT header `0xCA` tetap masuk. Parser siaran itu ada di [`rumus/siaran_okok.py`](../rumus/siaran_okok.py).

3. Rumus komposisi laporan OKOK sudah ditulis ulang. Jalur itu [`CsAlgoBuilder`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java). Pada timbangan yang bukan 8 elektroda, [`getBFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) mengembalikan hasil [`cs_bias_v235`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java) bila `result == 0`, dan rumus Java [`getBFR_Raw`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) bila tidak. Frekuensi ganda dan multi memakai [`cs_bias_vA019`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java). Memanggil library bias dari aplikasi sendiri tidak memenuhi syarat ini.

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

[`Myndk`](../ScaleHealtSource/jadx-protocol/sources/com/example/jnipack/Myndk.java) dan `libBodyFatScaleAlg.so` dipanggil [`n.e`](../ScaleHealtSource/jadx-protocol/sources/n/e.java) (`FormulasHelper`) untuk data `XsUserInfo`. Itu jalur XS, bukan syarat laporan OKOK.

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

Tulis ulang `cs_bias_v235` ada di [`rumus/cs_bias_v235.py`](../rumus/cs_bias_v235.py). Tulis ulang `cs_bias_vA019` ada di [`rumus/cs_bias_vA019.py`](../rumus/cs_bias_vA019.py). Parser siaran tidak terenkripsi ada di [`rumus/siaran_okok.py`](../rumus/siaran_okok.py). Parser GATT versi 16 serta perintah 0 dan 1 pada versi 17 ada di [`rumus/gatt_okok.py`](../rumus/gatt_okok.py). Perintah 18, 19, dan 20 belum diurai. Langkah engineering yang masih berlaku ada di rekomendasi terbaru `pemahaman.md`. Syarat 2 tertutup oleh keputusan di atas. Syarat 4 masih menunggu satu sesi ukur pada timbangan nyata.

## Aplikasi sendiri, tahap pertama

Dimulai setelah cakupan timbangan selesai.

Isi tahap ini: kenali siaran OKOK, baca berat, sambung GATT, hitung komposisi dari rumus yang sudah ditulis ulang, simpan hasil ukur, dan simpan data tubuh yang rumus butuhkan (tinggi, umur, jenis kelamin).

Di luar tahap ini: dapur (`nutriscale`), minum (`waterdrink`), olahraga, wearable, tali, puasa, VIP, iklan, dan akun di server Chipsea. Aplikasi sendiri menyimpan hasil ukurnya sendiri.

## Cakupan kemudian

Setelah tahap pertama bisa mengukur, tiap fitur lain mengikuti pola yang sama: alur klien modul itu terbaca, kebutuhan modul itu diketahui, fitur ada di aplikasi sendiri, lalu lolos uji banding pada skenario modul itu.

Seluruh perilaku OKOK International yang dipakai untuk pengguna timbangan kesehatan disebut selesai ketika setiap modul produk itu punya padanan yang lolos uji tersebut. SDK iklan, analitik, dan PDF tetap di luar.

Membongkar `classes.dex` sampai habis, atau mengemas ulang APK sumber, tidak memenuhi definisi di dokumen ini.
