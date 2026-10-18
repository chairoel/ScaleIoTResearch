# Yang belum selesai

Daftar ini memisahkan yang sudah selesai pada timbangan satu ohm dari yang masih terbuka. Riwayat pekerjaan ada di [activity_log.md](activity_log.md). Fakta dan rekomendasi yang berlaku ada di [pemahaman.md](pemahaman.md).

Setiap judul bagian memuat waktu pencatatan dalam WIB. Bagian yang sudah tertulis tidak diubah. Koreksi ditambah sebagai bagian baru di atas bagian lama.

## 2026-10-18 22:35 WIB — Daftar setelah timbangan satu ohm selesai

Timbangan yang sudah diuji mengirim satu ohm. Satu sesi ukur HealthTrack pada timbangan itu sudah selesai: berat dan daftar indeks cocok dengan OKOK pada umur utuh yang sama, profil tersimpan, hasil ada di riwayat, dan angka tetap sama setelah aplikasi ditutup lalu dibuka lagi. Uji itu lulus pada 18 Oktober 2026. Jalur rumusnya `v235`.

Uji host fase 6 juga sudah lulus. Sepuluh ohm di komputer memilih `vA019`. Ketiadaan timbangan sepuluh ohm bukan kegagalan dan tidak membuka pekerjaan kode.

Kalimat "vA019 masih fase 6" di berkas fase 1–5 adalah batas fase pada saat berkas itu ditulis. Yang masih terbuka pada frekuensi ganda hanya sesi timbangan sepuluh ohm.

### Menunggu timbangan sepuluh ohm

Sesi pembanding belum ada. Contoh uji host 500, 480, 30, 450, 460, 510, 490, 28, 440, 470 ohm bukan sesi timbangan. Daftar baris OKOK untuk sepuluh ohm belum dikunci. Rekomendasi 2026-10-18 01:29 WIB di [pemahaman.md](pemahaman.md) tetap berlaku bila perangkat itu ada.

Enam data yang masih kurang dari satu penimbangan nyata:

- Berat (kg)
- Tinggi (cm)
- Jenis kelamin OKOK (0 perempuan, 1 laki-laki)
- Umur utuh OKOK, yaitu umur yang sudah terlewati dari tanggal lahir sampai tanggal ukur
- Sepuluh ohm berurutan: tangan kanan, tangan kiri, batang, kaki kanan, kaki kiri, lalu frekuensi kedua dengan urutan yang sama
- Baris yang OKOK tampilkan, satu baris satu angka, beserta satuan dan jumlah desimal

Tanggal ukur, tanggal lahir, hex siaran, dan hex GATT ikut dicatat bila ada. Ketiadaan hex tidak menahan hitungan bila enam data di atas sudah ada.

Tanda frame sepuluh ohm ada di GATT OKOK berheader `0xCB` (`-53`), dua paket. Jenis impedansinya `7`, delapan elektroda dua frekuensi. HealthTrack saat ini hanya membaca GATT berheader `0xCA`.

```34:35:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/okCloudV4StraightFrame.java
        if (b == -53) {
            return processCB(bArr, str, i);
```

```18:18:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/ImpedanceType.java
    DUAL_FREQUENCY_EIGHT_ELECTRODES(7),
```

```43:45:HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/gatt/GattParser.kt
        if (frame.u8(GattConst.HEADER) != GattConst.HEADER_CA) {
            throw FrameFormatError("GATT header is not 0xCA")
        }
```

Sepuluh angka itu diisi OKOK dari [`toParserMultiFrequencyData`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) ke [`cs_bias_vA019`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java).

```691:698:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
        int[] iArr = {(int) (assemblyBodyImpedance.getRightHandImpedance1() * 10.0f), (int) (assemblyBodyImpedance.getLeftHandImpedance1() * 10.0f), (int) (assemblyBodyImpedance.getTrunkImpedance1() * 10.0f), (int) (assemblyBodyImpedance.getRightFootImpedance1() * 10.0f), (int) (assemblyBodyImpedance.getLeftFootImpedance1() * 10.0f), (int) (assemblyBodyImpedance.getRightHandImpedance2() * 10.0f), (int) (assemblyBodyImpedance.getLeftHandImpedance2() * 10.0f), (int) (assemblyBodyImpedance.getTrunkImpedance2() * 10.0f), (int) (assemblyBodyImpedance.getRightFootImpedance2() * 10.0f), (int) (assemblyBodyImpedance.getLeftFootImpedance2() * 10.0f)};
        CSBiasAPI.CSBiasPersonalInfoVA019 cSBiasPersonalInfoVA019 = new CSBiasAPI.CSBiasPersonalInfoVA019();
        cSBiasPersonalInfoVA019.age = this.Age;
        cSBiasPersonalInfoVA019.sex = this.Sex;
        cSBiasPersonalInfoVA019.height = Math.round(this.H * 10.0f);
        cSBiasPersonalInfoVA019.weight = Math.round(this.Wt * 10.0f);
        cSBiasPersonalInfoVA019.mode = 0;
        cSBiasPersonalInfoVA019.impedance = iArr;
```

Sebelum sesi itu ada, yang tidak dikerjakan:

- Parser siaran, GATT, dan [`MeasurementSession.impedanceOhm`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) tetap satu ohm
- Sepuluh ohm tidak dikumpulkan dari radio
- Daftar baris di [`ResultViewModel.rows`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/presentation/result/ResultViewModel.kt) tidak diganti
- [`DisplayMeasurementUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/DisplayMeasurementUseCase.kt) tidak diubah sebelum baris turunan yang sudah ada berubah
- Baris segmental, `icw`, `ecw`, layar baru, tabel Room, dan migrasi tidak ditambah
- [`CalculateReportUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/CalculateReportUseCase.kt), [`CsBiasVA019`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/util/CsBiasVA019.kt), dan urutan float tidak diubah

Setelah enam data itu lengkap, langkahnya mengunci daftar baris yang cocok, lalu mengubah `ResultViewModel.rows` agar sepuluh ohm menampilkan daftar itu.

### Modul di luar satu sesi ukur

Tahap pertama aplikasi hanya satu sesi ukur. Modul berikut belum dibangun. Pola tiap modul, setelah tahap timbangan bisa mengukur: alur klien modul itu terbaca, kebutuhan modul itu diketahui, fitur ada di aplikasi sendiri, lalu lolos uji banding pada skenario modul itu. Sumber batasnya [definisi selesai](definisi-selesai.md).

| Modul | Nama di sumber | Keadaan |
|---|---|---|
| Dapur | `nutriscale` | Belum |
| Minum | `waterdrink` | Belum |
| Olahraga | — | Belum |
| Wearable | — | Belum |
| Tali | — | Belum |
| Puasa | — | Belum |
| VIP | — | Belum |
| Akun server Chipsea | — | Belum |

Iklan, analitik, dan PDF tetap di luar, termasuk bila modul produk di atas suatu saat punya padanan. SDK ketiga itu tidak menjadi syarat selesai.

### Sengaja di luar rilis timbangan ini

Ini keputusan, bukan sisa fase 1–5.

Siaran `0xC0` dengan bit enkripsi menyala ditolak. Empat byte kunci tidak ada di APK. [`OkokScaleEncryptedKeyUtils.getOkokScaleEncryptedKeySync`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java) hanya membaca prefs.

```41:45:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
    public static String getOkokScaleEncryptedKeySync(String str) {
        Context contexts = MyAplication.getContexts();
        if (contexts != null && !TextUtils.isEmpty(str)) {
            try {
                return PrefsUtil.getInstance(contexts.getApplicationContext()).getOkokScaleEncryptedKey(str);
```

[`libprotocol.so`](../ScaleHealtSource/split_config.arm64_v8a/lib/arm64-v8a/libprotocol.so) hanya untuk perangkat Xiangshan atau `KAYOFIT_CS8`. Pembungkusnya [`Protocol`](../ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java).

```7:9:ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java
    static {
        System.loadLibrary("protocol");
    }
```

[`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) tidak dipindahkan ke HealthTrack. Viseral laporan `v235` adalah field `vfl`. Tulis ulang Java-nya ada di [rumus/vfr_okok.py](../rumus/vfr_okok.py) dan tidak dipanggil aplikasi. Pada jalur yang bukan frekuensi ganda, method itu masuk skor umur:

```1386:1389:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
        if (getType() == Type.DualFrequency || getType() == Type.MultiFrequency) {
            sbc = getSbc();
        } else {
            float scoreWithAge = getScoreWithAge(this.H, this.Wt, this.Sex, this.Age, getBFR(), getSLM(), getVFR());
```

Sesi tidak menulis ke karakteristik TX. Foreground service tidak masuk tahap ini. supabase-kt, OkHttp, dan Retrofit tidak masuk enam fase.

### Jalur timbangan lain

HealthTrack tidak membaca jalur ini. Timbangan yang sudah diuji tidak memakainya. Jalur ini bukan langkah berikut.

| Jalur | Tanda | Isi ohm |
|---|---|---|
| Delapan elektroda, dua frekuensi | GATT `0xCB`, jenis `7` | Sepuluh angka, dua frekuensi. Menunggu perangkat, bagian di atas |
| Delapan elektroda, satu frekuensi | GATT `0xC8` (`-56`), jenis `1` | Lima angka |
| Empat elektroda, dua frekuensi | Jenis impedansi `4` | Belum dipetakan ke sesi HealthTrack |
| Empat elektroda, tiga frekuensi | Jenis `5` | Belum dipetakan ke sesi HealthTrack |
| Xiangshan, delapan elektroda | Jenis `6`, lewat `libprotocol.so` | Di luar rilis timbangan ini |
| Delapan elektroda, tiga frekuensi | Jenis `8` | Belum dipetakan ke sesi HealthTrack |

Jenis `1` di OKOK menyusun lima angka, bukan sepuluh.

```31:32:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/okCloudV4StraightFrame.java
        if (b == -56) {
            return processC8(bArr, str, i);
```

```12:12:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/ImpedanceType.java
    SINGLE_FREQUENCY_EIGHT_ELECTRODES(1),
```

Pada delapan elektroda, [`getBFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) mengembalikan rumus Java [`getBFR_Raw`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java). HealthTrack tidak memindahkan cadangan itu. Timbangan satu ohm yang sudah diuji memakai `v235`.

```956:960:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
        if (this.isEightR) {
            return fFloatValue;
        }
        LogUtil.i(TAG, "本地算法和算法库对比 体脂率 : " + fFloatValue + " " + getBfp() + " mBIASV235Success : " + this.mBIASV235Success);
        return this.mBIASV235Success ? getBfp() : fFloatValue;
```

### Bukan sisa pekerjaan

Selisih lima baris pada 68,95 kg adalah umur utuh OKOK 29 lawan umur 30 yang diketik di HealthTrack. Rumus tidak diubah. Banding memakai umur utuh yang sama.

Skor (`sbc`) tampil karena rumus menghasilkannya. Daftar OKOK yang dibandingkan tidak memuat skor.

Angka komposisi di dalam paket GATT tidak mengisi laporan.

Contoh sepuluh ohm di uji host bukan sesi timbangan.
