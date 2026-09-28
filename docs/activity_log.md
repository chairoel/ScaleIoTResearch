# Activity Log

## 2026-09-28 10:15 WIB — Prefs dan Room di HealthTrack

### Tujuan
Menyelaraskan rules HealthTrack dengan keputusan penyimpanan: DataStore untuk preferensi dan Room untuk profil serta hasil ukur.

### Perubahan
- `docs/rencana-aplikasi-android.md`: preferensi lokal memakai DataStore `healthtrack_prefs`; tabel `tubuh` dan `ukur` tetap di Room.
- `HealthTrack/.cursor/rules/` dan skills terkait: larangan menambah Room dihapus. DataStore dan Room sama-sama bagian aplikasi.

### Status
Selesai. Urutan bangun tidak berubah. Langkah berikut tetap fase 1 parser di rekomendasi terbaru `docs/pemahaman.md`.

## 2026-09-28 09:12 WIB — Rencana aplikasi Android

### Tujuan
Menulis rencana tahap pertama HealthTrack supaya pembangunan satu sesi ukur mengikuti definisi selesai dan perilaku Python yang sudah ada.

### Perubahan
- `docs/rencana-aplikasi-android.md`: rencana modul `inti`, alur sesi, layar, penyimpanan, dan enam fase beserta pintu keluarnya.

### Status
Selesai. Pembangunan belum dimulai. Langkah berikut ada di rekomendasi terbaru `docs/pemahaman.md`.

## 2026-09-27 12:00 WIB — Daftar indeks OKOK terbaca

### Tujuan
Mencocokkan daftar indeks yang terbaca dengan laporan v235 pada berat 68,7 kg, tinggi 166 cm, umur 29, kelamin 1.

### Perubahan
- `docs/definisi-selesai.md`: syarat 4 tertutup untuk daftar indeks ini.

### Temuan
Setiap baris daftar sama dengan v235 pada impedansi 600 ohm dan jumlah desimal di layar, termasuk viseral 10,0, tulang 2,77 kg, dan metabolisme 1502,0. Skor tidak ada di daftar itu.

### Status
Selesai untuk daftar indeks pengukuran ini.

## 2026-09-27 11:55 WIB — Banding layar OKOK 68,7 kg

### Tujuan
Membandingkan laporan v235 dengan layar OKOK pada berat 68,7 kg, tinggi 166 cm, umur 29.

### Perubahan
- `data/scaleiot.sqlite`: profil tubuh terbaru menjadi tinggi 166 cm, umur 29, kelamin 1.

### Temuan
Layar 27 Sep 2026 11:48 cocok pada satu desimal untuk BMI 24,9, lemak 23,1, massa lemak 15,9, rasio otot rangka 38,2, rasio otot 72,8, air 54,2, massa air 37,3, dan umur metabolik 36. Impedansi tidak tampil. Nilai 600 ohm yang menghasilkan pasangan lemak dan air itu. Kelamin 0 menghasilkan lemak 34,8. Tulang 2,8 kg, BMR 1502, viseral 10, dan skor 61 belum terbaca dari foto.

### Status
Sebagian. Syarat 4 menunggu tulang, BMR, viseral, dan skor dari layar yang sama.

## 2026-09-26 20:09 WIB — Berat dari siaran yang tidak menerima sambungan

### Tujuan
Sesi pada timbangan nyata berhenti di menunggu berat karena setiap iklan bertanda tidak bisa disambung.

### Perubahan
- `aplikasi/sesi_ukur.py`: `pakai_berat_siaran` menutup sesi dari berat siaran terkunci bila GATT belum ada.
- `aplikasi/sesi_ble.py`: `putuskan_berat` memakai jalur itu saat `kCBAdvDataIsConnectable` salah.
- `aplikasi/test_sesi_ukur.py`, `aplikasi/test_sesi_ble.py`: uji berat siaran dan uji GATT yang sudah masuk tetap dipakai.

### Temuan
Sesi `D92E955D-DA1E-5928-BD8B-D23EDAD2CD92` tidak pernah mencetak “siaran menerima sambungan”. Notify tidak dipasang. Siaran terkunci `c06b1ad117700a0125f8f2f038ca3a` adalah `0xC0` versi 1, berat 68,65 kg, impedansi 600 ohm, product id 2561. Berat itu field [`okokBroadcasetV2Parser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java).

```169:171:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        WeightParserReturn weightParserReturnParser = WeightUnitUtil.Parser(bArr2[0], bArr2[c], this.scaleProperty, false);
        this.weight = weightParserReturnParser.kgWeight;
        this.scaleWeight = weightParserReturnParser.scaleWeight;
```

Laporan dari profil tersimpan 170 cm, umur 30, kelamin 1: lemak 21,151988983154297, otot 27,247825622558594, air 54,7817497253418, viseral 9, skor 67, rumus v235. Hasil itu tersimpan.

### Status
Selesai untuk berat siaran bila GATT tidak tersambung. Syarat 4 menunggu perbandingan angka ini dengan aplikasi OKOK pada timbangan yang sama dan profil tubuh yang sama.

## 2026-09-26 18:27 WIB — Sambungan GATT pada siaran pertama

### Tujuan
Sambungan yang menunggu impedansi terkunci kalah dari jendela koneksi timbangan. FSAC menyambung begitu MAC cocok.

### Perubahan
- `aplikasi/sesi_ble.py`: `boleh_sambung` memakai siaran OKOK pertama. Siaran macOS yang tidak menerima sambungan dilewati. Setelah notify aktif, pemindaian dinyalakan lagi. Putusnya sambungan dicoba ulang.
- `aplikasi/test_sesi_ble.py`: uji sambungan pada siaran terbuka dan tanda `kCBAdvDataIsConnectable`.

### Temuan
[`getConnectMode`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/ConfigurableDeviceUtil.java) memakai FSAC, kecuali Xiaomi HM. [`handleBroadcastInfo`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java) memanggil `success` saat MAC cocok, tanpa melihat kunci. Callback itu menghentikan pemindaian lalu [`connectGATT`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java).

```23:26:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/ConfigurableDeviceUtil.java
    public static CsBtUtil_v11.CONNECT_MODE getConnectMode() {
        CsBtUtil_v11.CONNECT_MODE connect_mode = CsBtUtil_v11.CONNECT_MODE.FSAC;
        return (Build.BRAND.toLowerCase().equals("xiaomi") && Build.DEVICE.startsWith("HM")) ? CsBtUtil_v11.CONNECT_MODE.Alway_Conn : connect_mode;
    }
```

```229:234:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java
            if (!TextUtils.isEmpty(strCheckAndDecryptedMac) && strCheckAndDecryptedMac.equalsIgnoreCase(this.mBoundMac)) {
                byte[] manufacturerData = getManufacturerData(bArr);
                CsBtUtil_v11.SeachDeviceCallback seachDeviceCallback = this.searchCallBack;
                if (seachDeviceCallback != null) {
                    seachDeviceCallback.success(manufacturerData);
                    return;
```

```535:540:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java
            public void success(byte[] bArr) {
                BluetoothScanService.getInstanace().stopSeachBindDevice();
                if (bArr != null) {
                    CsBtUtil_v11.this.mManufacturerData = bArr;
                }
                CsBtUtil_v11.this.connectGATT();
```

`python -m aplikasi sesi --detik 70` selesai di menunggu impedansi. Tidak ada siaran OKOK. Pemindaian 12 detik berikutnya melihat perangkat BLE lain, jadi radio berjalan. Timbangan tidak menyiarkan.

### Status
Selesai untuk urutan sambungan. Syarat 4 belum tertutup. Langkah berikut: naik ke timbangan, tutup aplikasi OKOK di ponsel, lalu jalankan `python -m aplikasi sesi`.

## 2026-09-26 16:02 WIB — GATT tetap habis waktu

### Tujuan
Mencatat hasil `python -m aplikasi sesi` setelah pemindaian dihentikan sebelum sambungan.

### Temuan
Enam percobaan ke `D92E955D-DA1E-5928-BD8B-D23EDAD2CD92` habis waktu. Siaran terkunci tetap 600 ohm. Notify belum tercatat.

### Status
Syarat 4 belum tertutup. Langkah berikut tetap melepas sambungan ponsel, lalu mengulang `sesi`.

## 2026-09-26 15:58 WIB — Sambungan GATT setelah pemindaian berhenti

### Tujuan
Siaran terkunci sudah masuk, tetapi notify GATT habis waktu dan tidak dicoba lagi.

### Perubahan
- `aplikasi/sesi_ble.py`: sambungan menunggu impedansi terkunci, pemindaian berhenti dulu, lalu sampai tiga percobaan dan satu putaran ulang.
- `aplikasi/test_sesi_ble.py`: uji `boleh_sambung` hanya setelah siaran terkunci.

### Temuan
Pesan `sambungan gagal:` kosong karena `TimeoutError`. Siaran `D92E955D-DA1E-5928-BD8B-D23EDAD2CD92` terkunci pada 600 ohm. Notify belum tercatat.

### Status
Selesai untuk urutan sambungan. Syarat 4 menunggu sesi yang notify-nya aktif, lalu perbandingan dengan aplikasi OKOK.

## 2026-09-26 15:52 WIB — Koreksi hasil pemindaian 15 detik

### Tujuan
Mencatat hasil pemindaian yang selesai setelah catatan 15:51 ditulis.

### Temuan
Siaran OKOK masuk dari `D92E955D-DA1E-5928-BD8B-D23EDAD2CD92`. Status siaran terbuka, impedansi 0 ohm, berat bergerak, notify GATT belum tercatat, sesi tetap menunggu impedansi. Izin Bluetooth sudah cukup untuk menerima iklan.

### Status
Syarat 4 belum tertutup. Langkah berikut tetap `python -m aplikasi sesi` sampai siaran terkunci membawa impedansi dan berat GATT terkunci.

## 2026-09-26 15:51 WIB — Pendengar sesi Bluetooth

### Tujuan
Membuka satu sesi ukur dari timbangan: impedansi dari iklan, berat dari notify GATT.

### Perubahan
- `rumus/iklan_okok.py`: muatan pabrik OKOK dari scan record dan dari id pabrik.
- `rumus/test_iklan_okok.py`: uji rekaman, UUID di depan data pabrik, dan id little-endian.
- `aplikasi/sesi_ble.py`: `PendengarSesi` mengisi `SesiUkur`; `dengar` memindai dan memasang notify.
- `aplikasi/test_sesi_ble.py`: uji tutup sesi, saringan alamat, dan perintah tanpa profil.
- `aplikasi/__main__.py`: perintah `sesi`.
- `requirements.txt`: `bleak==3.0.2`.
- `docs/pemahaman.md`: layanan GATT OKOK dan langkah sesi nyata.

### Temuan
Notify OKOK memakai [`CHIPSEA_CHAR_RX_UUID`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/BtGattAttr.java). Untuk protokol OKOK, [`getCharacteristicUUID`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java) dengan argumen benar mengembalikan RX itu.

```44:46:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/BtGattAttr.java
        CHIPSEA_SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb";
        CHIPSEA_CHAR_RX_UUID = "0000fff1-0000-1000-8000-00805f9b34fb";
        CHIPSEA_CHAR_TX_UUID = "0000fff2-0000-1000-8000-00805f9b34fb";
```

```768:771:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java
        if (i == 1) {
            if (z) {
                return BtGattAttr.CHIPSEA_CHAR_RX_UUID;
            }
```

[`getProtocalTypeByBroadcast`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java) berhenti pada blok pabrik atau daftar UUID 16-bit pertama. `muatan_okok` membaca rekaman sampai habis.

```205:207:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java
                        if (z) {
                            break;
                        }
```

### Status
Selesai untuk pendengar pada frame dan sambungan GATT. Syarat 4 masih menunggu satu sesi pada timbangan nyata. Pemindaian dari proses ini berhenti di izin Bluetooth macOS, tanpa dialog yang selesai.

## 2026-09-26 14:29 WIB — Aplikasi satu sesi ukur

### Tujuan
Membangun aplikasi tahap pertama untuk satu sesi ukur: membaca siaran dan berat GATT, menghitung laporan dari rumus yang sudah ditulis ulang, lalu menyimpan data tubuh dan hasil.

### Perubahan
- `aplikasi/sesi_ukur.py`: `SesiUkur` menutup sesi dari impedansi siaran terkunci dan berat GATT terkunci.
- `aplikasi/simpan.py`: `Penyimpan` menyimpan profil tubuh dan hasil ukur di sqlite.
- `aplikasi/__main__.py`: perintah `tubuh`, `profil`, `ukur`, dan `daftar`.
- `aplikasi/test_sesi_ukur.py`: uji sesi, penyimpanan, dan perintah.
- `.gitignore`: `data/` dan `__pycache__/`.

### Temuan
Berat laporan adalah berat GATT dengan `lock_flag == 1` dan `history == False`. Impedansi laporan adalah `impedance_ohm` pada siaran terkunci. Satu ohm memakai [`parse_default_z`](../rumus/cs_bias_v235.py). Sepuluh ohm memakai [`parse_multi_frequency`](../rumus/cs_bias_vA019.py).

### Status
Selesai untuk aplikasi pada frame. Syarat 4 masih menunggu satu sesi pada timbangan nyata.

## 2026-09-26 14:10 WIB — Tulis ulang getVFR

### Tujuan
Membaca tingkat lemak viseral yang masuk ke skor, dari method yang jadx tidak jadi Java.

### Perubahan
- `rumus/vfr_okok.py`: `get_vfr` mengikuti `getVFR` di `classes4.dex`.
- `rumus/test_vfr_okok.py`: cabang jenis timbangan, 8 elektroda, setengah langkah, dan batas 1 sampai 59.
- `rumus/cs_bias_v235.py`: catatan bahwa `vfl` laporan bukan hasil `getVFR`.
- `docs/pemahaman.md`: beda `getVFR` dan field `vfl`.

### Temuan
[`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) dipanggil skor. Badan method ada di [`classes4.dex`](../ScaleHealtSource/base/classes4.dex). `DualFrequency` dan `MultiFrequency` mengembalikan `vfl`. Pada 8 elektroda perempuan, konstanta dikurangi. Hasil di bawah 1 menjadi 1, di atas 59 menjadi 59.

```1389:1389:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
            float scoreWithAge = getScoreWithAge(this.H, this.Wt, this.Sex, this.Age, getBFR(), getSLM(), getVFR());
```

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

### Status
Selesai untuk `getVFR`. Langkah berikut tetap aplikasi tahap pertama untuk satu sesi ukur.

## 2026-09-26 13:52 WIB — Parser GATT perintah 20

### Tujuan
Membaca daftar peran yang cocok dari GATT versi 17, perintah 20.

### Perubahan
- `rumus/gatt_okok.py`: `GattParser` merakit perintah 20 menjadi `GattKonfirmasi`.
- `rumus/test_gatt_okok.py`: vektor satu paket, dua paket, buffer yang tidak direset, dan batas int 32 bit.
- `docs/protokol-frame-okok.md`: beda rakitan perintah 20 dari perintah 18 dan 19.
- `docs/definisi-selesai.md`: perintah 20 sudah diurai.
- `docs/pemahaman.md`: aturan buffer peran dan penerusan `matchUserMsg`.

### Temuan
[`chipseaStraightFrame.process`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java) menambah byte perintah 20 sesuai urutan datang. Paket nomor 1 tidak mengosongkan `lstRoleBuffer`. Rakitan selesai bila kedua nibble bertanda sama.

```168:172:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                    for (int i3 = 0; i3 < i2; i3++) {
                        this.lstRoleBuffer.add(Byte.valueOf(bArr[i3 + 5]));
                    }
                    if (bArrSplitPackInfo[0] == bArrSplitPackInfo[1]) {
```

[`CsBtUtil_v11`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java) meneruskan [`CsFatConfirm`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatConfirm.java). [`BoundDeviceActivity.matchUserMsg`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java) kosong.

```104:106:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java
    public void matchUserMsg(CsFatConfirm csFatConfirm) {
    }
```

### Status
Selesai untuk perintah 20. Langkah berikut tetap aplikasi tahap pertama untuk satu sesi ukur. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) belum terdekompilasi.

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

## 2026-09-26 13:30 WIB — Rakitan GATT perintah 18 dan 19

### Tujuan
Membaca pengukuran dan riwayat GATT yang terpecah beberapa paket, termasuk penghitungan ulang otot.

### Perubahan
- `rumus/gatt_okok.py`: `GattParser` merakit perintah 18 dan 19, lalu menghitung ulang otot.
- `rumus/test_gatt_okok.py`: vektor satu paket, dua paket, buffer terpisah, dan batas int 32 bit.
- `docs/protokol-frame-okok.md`: nibble bertanda, potongan otot, dan batas `bytesToInt`.
- `docs/definisi-selesai.md`: perintah 18 dan 19 sudah diurai. Perintah 20 belum.
- `docs/pemahaman.md`: aturan rakitan dan rekomendasi berikut ke aplikasi satu sesi ukur.

### Temuan
[`splitPackInfo`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java) menggeser byte bertanda. Nibble 8 sampai 15 menjadi negatif, jadi jumlah paket 8 atau lebih gagal pada pemeriksaan ukuran buffer.

```22:24:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
    private byte[] splitPackInfo(byte b) {
        return new byte[]{(byte) (((byte) (b << 4)) >> 4), (byte) (b >> 4)};
    }
```

Otot pada perintah 18 dan 19 dihitung ulang, lalu dipotong lewat `(int)` sebelum [`setMuscle`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java) membagi 10.

```148:150:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                            }
                        }
                        this.fatScale.setMuscle((int) (muscle * 10.0d));
```

### Status
Selesai untuk perintah 18 dan 19. Perintah 20 belum. Langkah berikut: aplikasi tahap pertama untuk satu sesi ukur. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) belum terdekompilasi.

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

## 2026-09-26 13:22 WIB — Parser GATT versi 16 dan perintah 0 serta 1

### Tujuan
Membaca berat sesi yang tersambung dari GATT OKOK, untuk versi 16 dan perintah 0 serta 1 pada versi 17.

### Perubahan
- `rumus/gatt_okok.py`: parser versi 16 dan perintah 0 serta 1 pada versi 17, termasuk penyempitan angka paket.
- `rumus/test_gatt_okok.py`: vektor berat, batas penyempitan, dan penolakan perintah di luar cakupan.
- `docs/protokol-frame-okok.md`: bagian yang belum tertutup menunjuk parser ini.
- `docs/definisi-selesai.md`: lokasi parser GATT. Perintah 18 dan 19 belum.
- `docs/pemahaman.md`: tanda kunci, angka paket yang bukan laporan, dan rekomendasi berikut ke perintah 18 dan 19.

### Temuan
Pada versi 17 perintah 0 dan 1, [`setLockFlag`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java) menerima byte perintah, bukan bit kunci properti. Properti ada di offset 11. Komposisi tidak diisi.

```106:110:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                this.fatScale.setLockFlag(b4);
                this.fatScale.setScaleProperty(bArr[11]);
                WeightParserReturn weightParserReturnParser2 = WeightUnitUtil.Parser(bArrSubBytes7[0], bArrSubBytes7[1], this.fatScale.getScaleProperty(), false);
                this.fatScale.setWeight(weightParserReturnParser2.kgWeight * 10.0d);
                this.fatScale.setScaleWeight(weightParserReturnParser2.scaleWeight);
```

Pada versi 16, komposisi paket hanya diisi bila bit kunci = 1. Otot tidak dihitung ulang dari berat. Penghitungan ulang itu ada di perintah 18 dan 19.

```89:96:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
            if (cmdId > 0) {
                this.fatScale.setAxunge(BytesUtil.bytesToInt(bArrSubBytes));
                this.fatScale.setWater(BytesUtil.bytesToInt(bArrSubBytes2));
                this.fatScale.setMuscle(BytesUtil.bytesToInt(bArrSubBytes3));
                this.fatScale.setBmr(BytesUtil.bytesToInt(bArrSubBytes4));
                this.fatScale.setVisceral_fat(BytesUtil.bytesToInt(bArrSubBytes5));
                this.fatScale.setBone(BytesUtil.bytesToInt(bArrSubBytes6));
            }
```

### Status
Selesai untuk versi 16 dan perintah 0 serta 1 pada versi 17. Langkah berikut: rakitan perintah 18 dan 19. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) belum terdekompilasi.

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

## 2026-09-26 13:15 WIB — Keputusan kunci siaran dan parser siaran

### Tujuan
Menutup syarat 2 cakupan timbangan, lalu menyediakan pembacaan berat dan impedansi dari siaran yang tidak terenkripsi.

### Perubahan
- `docs/definisi-selesai.md`: keputusan bahwa timbangan terenkripsi tidak masuk rilis pertama.
- `rumus/siaran_okok.py`: parser siaran `0xCA`, `0xC0` tanpa bit enkripsi, dan `0xFF`.
- `rumus/test_siaran_okok.py`: vektor berat, impedansi, satuan, dan penolakan siaran terenkripsi.
- `docs/protokol-frame-okok.md`: bagian yang belum tertutup menunjuk keputusan dan parser.
- `docs/pemahaman.md`: keputusan syarat 2, topeng byte `0xFF`, dan rekomendasi berikut ke parser GATT.

### Temuan
Bit enkripsi siaran `0xC0` adalah bit 7 pada byte offset 4. [`okokBroadcasetV2Parser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java) mengisi berat 0 bila kunci kosong. Parser sendiri menolak frame itu.

```129:129:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        boolean z = (bArr[4] & (-128)) == -128;
```

```160:163:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        if (z) {
            int iOkokBroadcasetV2ParserDecrypt2 = okokBroadcasetV2ParserDecrypt(BytesUtil.bytesToInt(bArr2), bytesFromHexStr);
            if (bytesFromHexStr == null) {
                iOkokBroadcasetV2ParserDecrypt2 = 0;
```

Di [`classes4.dex`](../ScaleHealtSource/base/classes4.dex), [`bytesToHexString`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) memakai `and-int/lit16` dengan literal `0xFF`.

```49:51:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
        for (byte b : bArr) {
            String hexString = Integer.toHexString(b & DataType.EXTEND);
            if (hexString.length() < 2) {
```

### Status
Selesai untuk syarat 2 dan parser siaran. Langkah berikut: parser GATT versi 16, plus perintah 0 dan 1 pada versi 17. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) belum terdekompilasi.

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

## 2026-09-26 11:26 WIB — Tulis ulang cs_bias_vA019

### Tujuan
Menulis ulang rumus komposisi laporan frekuensi ganda dan multi dari `libchipsea_bias_vA019.so`, supaya hasilnya tidak bergantung pada pemanggilan library asli.

### Perubahan
- `rumus/cs_bias_vA019.py`: tulis ulang `cs_bias_vA019`, regresi satu metrik, dan penyempitan field laporan.
- `rumus/test_cs_bias_vA019.py`: vektor yang dicocokkan dengan keluaran native.
- `docs/protokol-frame-okok.md`: peta frame menunjuk tulis ulang vA019.
- `docs/definisi-selesai.md`: kedua tulis ulang rumus bias disebut. Langkah yang berlaku mengikuti rekomendasi terbaru.
- `docs/pemahaman.md`: satuan masukan, kode gagal, dan rekomendasi berikut berpindah ke syarat 2.

### Temuan
[`cs_bias_vA019`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java) mengisi laporan frekuensi ganda. Jenis kelamin 0 perempuan dan 1 laki-laki. Berat di luar 20,0–250,0 kg gagal lebih dulu, kode 2. Mode pada pemanggil Java 0. Pemeriksaan impedansi hanya pada mode itu.

```7:10:ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java
    public static native CSBiasVA019Resp cs_bias_vA019(CSBiasPersonalInfoVA019 cSBiasPersonalInfoVA019);

    static {
        System.loadLibrary("chipsea_bias_vA019");
```

### Status
Selesai untuk `cs_bias_vA019`. Langkah berikut: syarat 2, contoh nilai kunci siaran `0xC0`. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) belum terdekompilasi.

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

## 2026-09-26 08:42 WIB — Tulis ulang cs_bias_v235

### Tujuan
Menulis ulang rumus komposisi laporan timbangan satu frekuensi dari `libchipsea_bias_v235.so`, supaya hasilnya tidak bergantung pada pemanggilan library asli.

### Perubahan
- `rumus/cs_bias_v235.py`: tulis ulang `cs_bias_v235` dan penyempitan laporan `parseDefaultZ`.
- `rumus/test_cs_bias_v235.py`: vektor yang dicocokkan dengan `bia_calc`.
- `docs/protokol-frame-okok.md`: peta frame menunjuk tulis ulang v235. `cs_bias_vA019` masih terbuka.
- `docs/definisi-selesai.md`: langkah yang berlaku mengikuti rekomendasi terbaru.
- `docs/pemahaman.md`: rentang masukan, kode gagal, dan rekomendasi berikut berpindah ke `cs_bias_vA019`.

### Temuan
[`cs_bias_v235`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java) mengisi laporan lewat `bia_calc`. Jenis kelamin 0 perempuan dan 1 laki-laki. Berat di luar 20–250 kg gagal lebih dulu, kode -2.

```5:8:ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java
    public static native CSBiasV235Resp cs_bias_v235(int i, int i2, int i3, int i4, int i5);

    static {
        System.loadLibrary("chipsea_bias_v235");
```

### Status
Selesai untuk `cs_bias_v235`. Langkah berikut: tulis ulang `cs_bias_vA019`. `getVFR` belum terdekompilasi. Syarat 2, contoh nilai kunci siaran `0xC0`, tetap terbuka.

## 2026-09-26 07:36 WIB — Jalur rumus laporan OKOK

### Tujuan
Menemukan method yang benar-benar menghitung komposisi pada laporan OKOK, supaya pembongkaran rumus tidak mulai dari library yang salah.

### Perubahan
- `ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java`: hasil dekompilasi dari `classes4.dex`.
- `ScaleHealtSource/jadx-protocol/sources/n/e.java`: `FormulasHelper` dari `classes9.dex`, pemanggil `Myndk` pada data XS.
- `docs/definisi-selesai.md`: syarat 3 sekarang menunjuk `CsAlgoBuilder` dan `cs_bias_v235`, bukan `Myndk`.
- `docs/protokol-frame-okok.md`: bagian yang belum tertutup memisahkan rumus laporan OKOK dari jalur XS.
- `docs/pemahaman.md`: catatan jalur rumus, plus rekomendasi berikut berpindah ke penulisan ulang `cs_bias_v235`.

### Temuan
Pada timbangan yang bukan 8 elektroda, [`getBFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) memakai hasil native bila bias berhasil. Rumus Java hanya cadangan. [`Myndk.getResultFourEleAlg`](../ScaleHealtSource/jadx-protocol/sources/n/e.java) dipakai `FormulasHelper` untuk `XsUserInfo`.

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

```174:174:ScaleHealtSource/jadx-protocol/sources/n/e.java
        FourElectrodeResult resultFourEleAlg = Myndk.getResultFourEleAlg(infoA, i2, i3, algType);
```

### Status
Selesai untuk letak rumus laporan OKOK dan cadangan Java lemak. Langkah berikut: tulis ulang `cs_bias_v235`. `getVFR` belum terdekompilasi utuh. Syarat 2, contoh nilai kunci siaran `0xC0`, tetap terbuka.

### Tujuan
Menyelaraskan definisi selesai dengan keputusan bahwa rumus komposisi native ikut dibongkar pada cakupan timbangan, dan mengoreksi peta frame yang masih menyebut kelas kunci belum didekompilasi.

### Perubahan
- `docs/definisi-selesai.md`: syarat 3 mewajibkan rumus `libBodyFatScaleAlg.so` plus koreksi bias `libchipsea_bias_v235.so` dan `libchipsea_bias_vA019.so` ditulis ulang. Syarat 4 menguji komposisi dari rumus itu.
- `docs/protokol-frame-okok.md`: bagian “Yang belum tertutup peta ini” sekarang menyatakan kelas kunci sudah Java, nilai hex belum ada, dan rumus native belum dibongkar.
- `docs/pemahaman.md`: catatan syarat rumus. Rekomendasi berikut tetap contoh nilai kunci siaran `0xC0`.

### Status
Selesai untuk penyelarasan dokumen. Langkah engineering berikut tidak berubah: satu contoh nilai `data` dari bind, atau entri prefs `okok_scale_encrypted_key_` + MAC.

## 2026-09-24 08:55 WIB — Definisi selesai proyek

### Tujuan
Menetapkan kapan cakupan boleh disebut selesai, supaya pembangunan aplikasi sendiri punya urutan yang tetap.

### Perubahan
- `docs/definisi-selesai.md`: arah proyek, syarat selesai cakupan timbangan, batas tahap pertama aplikasi sendiri, dan pola cakupan kemudian.
- `docs/pemahaman.md`: catatan arah. Rekomendasi berikut tetap contoh nilai kunci siaran `0xC0`.

### Status
Selesai untuk dokumen arah. Langkah engineering berikut tidak berubah: satu contoh nilai `data` dari bind, atau entri prefs `okok_scale_encrypted_key_` + MAC.

## 2026-09-23 22:43 WIB — Dekompilasi kunci siaran OKOK terenkripsi

### Tujuan
Mendapatkan isi `OkokScaleEncryptedKeyUtils`, kelas yang memasok kunci 4 byte untuk siaran header `0xC0`.

### Perubahan
- `ScaleHealtSource/jadx-protocol`: Java baru untuk [`OkokScaleEncryptedKeyUtils`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java), [`PrefsUtil`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/PrefsUtil.java), [`Api`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/Api.java), [`ApiImpl`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/ApiImpl.java), [`HttpsEngine`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/engine/HttpsEngine.java), [`JsonCommonInfo`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/mode/json/JsonCommonInfo.java), dan [`BoundDeviceActivity`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java).
- `docs/protokol-frame-okok.md`: bagian siaran `0xC0` sekarang menjelaskan sumber kunci. Kalimat "kelas belum didekompilasi" diganti.
- `docs/pemahaman.md`: fakta sumber kunci, plus rekomendasi berikut berpindah ke contoh nilai `data` dari bind.

### Temuan
Kelas didefinisikan di [`classes4.dex`](../ScaleHealtSource/base/classes4.dex). [`classes3.dex`](../ScaleHealtSource/base/classes3.dex) hanya memanggilnya dari `BoundDeviceActivity`. Kunci tidak dihitung di perangkat. `getOkokScaleEncryptedKeySync` membaca prefs. Pengisian lewat GET `/device/scale/sn?mac=` saat ikat timbangan terenkripsi.

```41:45:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
    public static String getOkokScaleEncryptedKeySync(String str) {
        Context contexts = MyAplication.getContexts();
        if (contexts != null && !TextUtils.isEmpty(str)) {
            try {
                return PrefsUtil.getInstance(contexts.getApplicationContext()).getOkokScaleEncryptedKey(str);
```

```155:155:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/Api.java
    public static final String SCALE_ENCRYPTED_KEY_GET = "/device/scale/sn?mac=";
```

### Status
Selesai untuk isi kelas kunci. Empat byte kunci tidak ada di APK. Langkah berikut: satu contoh nilai `data` dari respons bind, atau entri prefs `okok_scale_encrypted_key_` + MAC. `libprotocol.so` tetap ditunda.

## 2026-09-23 22:18 WIB — Tautan berkas pada dokumentasi hasil bongkaran

### Tujuan
Agar nama class dan simbol lain dari kode hasil reverse engineering di `docs/` menunjuk ke berkas aslinya, plus cuplikan baris yang mendukung klaim.

### Perubahan
- `docs/protokol-frame-okok.md`: tiap parser, skala `CsFatScale`, dan perintah ponsel sekarang menaut ke berkas Java dan mengutip barisnya. Kelas kunci yang belum didekompilasi menaut ke [`ScaleEncryptedKeyUtils.java`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/ScaleEncryptedKeyUtils.java) serta `classes3.dex` dan `classes4.dex`.
- `docs/pemahaman.md`: catatan baru berisi tabel berkas untuk nama class yang sudah disebut, plus koreksi titik panggil `parseScan`.
- `.cursor/rules/docs-sumber-kode.mdc`: aturan kutipan sumber untuk seluruh `docs/`.
- `.cursor/rules/project-understanding.mdc` dan `.cursor/rules/activity-log.mdc`: menunjuk ke aturan itu.

### Temuan
`parseScan` dipanggil dari [`XsBluetoothManager`](../ScaleHealtSource/jadx-protocol/sources/com/ss/bluetooth/sscore/XsBluetoothManager.java), bukan dari isi method `SdkPresenter`. `parseData` dan `getFuncBuffer` hanya deklarasi native di [`Protocol.java`](../ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java).

```85:86:ScaleHealtSource/jadx-protocol/sources/com/ss/bluetooth/sscore/XsBluetoothManager.java
    public boolean isXsDevice(byte[] bArr, String str) {
        return SdkPresenter.getInstance().protocol.parseScan(bArr, str) != null;
```

### Status
Selesai untuk kutipan sumber pada peta frame OKOK dan indeks berkas. Langkah berikut tetap dekompilasi `OkokScaleEncryptedKeyUtils`. Catatan lama di `pemahaman.md` dan `activity_log.md` tidak disunting.

## 2026-09-23 22:00 WIB — Peta field frame timbangan OKOK

### Tujuan
Melanjutkan reverse engineering pada jalur OKOK yang sudah ada di Java: layout field siaran dan GATT, plus skala nilai komposisi tubuh.

### Perubahan
- `docs/protokol-frame-okok.md`: peta offset frame `0xCA`, `0xC0`, dan `0xFF`, perintah GATT versi 16 dan 17, serta perintah ponsel ke timbangan.
- `docs/pemahaman.md`: fakta layout OKOK dan koreksi soal checksum. Rekomendasi berikut berpindah ke kelas kunci siaran terenkripsi.

### Temuan
- Komposisi tubuh dibaca di `chipseaStraightFrame`, bukan di siaran `0xCA` versi biasa.
- Parser terima `chipseaBroadcastFrame` dan `chipseaStraightFrame` tidak memeriksa XOR. Pemeriksaan XOR ada di `model.Frame` untuk parser lama.
- Kunci siaran `0xC0` ada di `OkokScaleEncryptedKeyUtils`, di `classes3.dex` dan `classes4.dex`, belum didekompilasi.

### Status
Selesai untuk peta field OKOK. Belum: isi kunci enkripsi siaran `0xC0`, dan isi `libprotocol.so` untuk perangkat XS.

## 2026-09-23 21:42 WIB — Isi jam WIB pada record yang sudah ada

### Tujuan
Menambah jam pencatatan pada record lama, karena waktu penulisannya masih bisa dipulihkan dari riwayat chat.

### Perubahan
- `docs/activity_log.md`: jam ditambahkan pada empat judul entri. Isi entri tidak diubah.
- `docs/pemahaman.md`: jam ditambahkan pada delapan judul bagian. Isi fakta tidak diubah. Kalimat pembuka disesuaikan karena record itu sekarang sudah berjam.
- `.cursor/rules/activity-log.mdc` dan `.cursor/rules/project-understanding.mdc`: jam yang sudah dipulihkan tidak diubah lagi.

### Temuan
Jam berikut ketelitian menit, diambil dari cap waktu chat yang menulis record itu:

- `21:06` — entri bongkar APK, ditulis pada giliran yang dimulai 21:06.
- `21:16` — empat bagian pemahaman pertama (aplikasi, bentuk file, batas bacaan, izin), ditulis pada giliran 21:13 dan selesai sebelum 21:17.
- `21:18` — entri aturan catatan, berkas chat terakhir diubah 21:18.
- `21:27` — entri dekompilasi protokol, plus empat bagian pemahaman yang ditulis atau diganti pada giliran itu. Berkas chat terakhir diubah 21:27.
- `21:36` — entri kunci catatan append-only, ditulis setelah 21:33 dan sebelum 21:37.

### Status
Selesai. Detik penyimpanan tidak tersimpan, jadi jam yang diisi adalah menit penulisannya.

## 2026-09-23 21:39 WIB — Tambah jam pencatatan WIB

### Tujuan
Agar setiap record baru memuat tanggal dan jam pencatatan dalam WIB, bukan tanggal saja.

### Perubahan
- `.cursor/rules/activity-log.mdc`: judul entri baru memakai `YYYY-MM-DD HH:mm WIB`.
- `.cursor/rules/project-understanding.mdc`: judul record baru memakai format yang sama. Jika bentrok, waktu pencatatan yang lebih baru yang berlaku.
- `docs/pemahaman.md`: kalimat pembuka menyebut jam WIB. Judul record lama tidak diubah karena jam aslinya tidak tersimpan.

### Status
Selesai. Record yang sudah ada tetap bertanggal `2026-09-23` tanpa jam.

## 2026-09-23 21:36 WIB — Kunci catatan proyek agar hanya bertambah

### Tujuan
Agar `docs/activity_log.md` dan `docs/pemahaman.md` tidak disunting ulang. Keduanya hanya bertambah, dan setiap record memuat tanggal pencatatan.

### Perubahan
- `.cursor/rules/activity-log.mdc`: larang mengubah entri lama; tanggal di judul adalah tanggal pencatatan.
- `.cursor/rules/project-understanding.mdc`: larang mengubah record lama; koreksi ditulis sebagai record baru; record yang lebih baru menang jika bentrok.
- `docs/pemahaman.md`: tambah tanggal pencatatan `2026-09-23` pada judul bagian yang sudah ada, plus kalimat pembuka tentang record yang tidak diubah. Isi fakta tidak ditulis ulang.

### Status
Selesai.

## 2026-09-23 21:27 WIB — Petakan manifest dan dekompilasi jalur protokol

### Tujuan
Melanjutkan reverse engineering setelah bongkar APK: peta komponen `com.chipsea`, lalu dekompilasi kelas yang mengurus timbangan dan pemanggilan native.

### Perubahan
- `docs/pemahaman.md`: perbaiki lokasi parser. Keluarga OKOK ada di Java `com.chipsea.btlib`; `libprotocol.so` khusus perangkat XS lewat `com.xshq.sdk.Protocol`.
- `ScaleHealtSource/jadx-protocol`: 235 berkas Java hasil jadx dari DEX yang disaring (paket `btlib`, `ss.bluetooth`, nutrisi, wearable, tali, serta pembungkus JNI). Folder ini tetap diabaikan Git.

### Temuan
- Jenis protokol dipilih di `BluetoothLeScannerCompat` dari byte manufacturer atau nama perangkat.
- Frame GATT Chipsea berawalan `0xCA`. Versi 16 sudah memuat komposisi tubuh di `chipseaStraightFrame`.
- `System.loadLibrary` yang terikat timbangan: `protocol`, `BodyFatScaleAlg`, `chipsea_bias_v235`, `chipsea_bias_vA019`, `device_auth`.

### Status
Selesai untuk peta manifest dan dekompilasi jalur protokol. Belum: isi `libprotocol.so`, dan dekompilasi layar/akun di luar paket timbangan.

## 2026-09-23 21:06 WIB — Bongkar APK OKOK International

### Tujuan
Membongkar `OKOK international.apk` dan menaruh hasilnya di `ScaleHealtSource`.

### Temuan
- File sumber bukan APK tunggal. Ini wadah split APK (header `MID`).
- Paket: `com.chipsea.btcontrol.en`
- Versi: `3.1.66` (versionCode `173`)
- Target SDK: 36

### Isi wadah
| Split | Ukuran | Hasil ekstrak |
|---|---|---|
| `base.apk` | ~157 MB | `ScaleHealtSource/base` (6.690 file) |
| `split_config.arm64_v8a.apk` | ~7,1 MB | `ScaleHealtSource/split_config.arm64_v8a` |
| `split_config.xxhdpi.apk` | ~154 KB | `ScaleHealtSource/split_config.xxhdpi` |

Salinan APK tiap split disimpan di `ScaleHealtSource/_splits`. Total hasil bongkaran sekitar 358 MB.

### Isi penting
- `ScaleHealtSource/base/AndroidManifest.xml` masih biner.
- Manifest yang bisa dibaca: `ScaleHealtSource/base/AndroidManifest.decoded.txt`
- Ringkasan paket: `ScaleHealtSource/base/badging.txt`
- Bytecode: `classes.dex` sampai `classes10.dex` (belum didekompilasi ke Java)
- Aset: `ScaleHealtSource/base/assets/` (animasi timbangan, font, HTML, paket skin)
- Library native (17 file `.so`): `ScaleHealtSource/split_config.arm64_v8a/lib/arm64-v8a/`
  - `libprotocol.so`
  - `libBodyFatScaleAlg.so`
  - `libchipsea_bias_v235.so`
  - `libchipsea_bias_vA019.so`

### Status
Selesai pada tahap bongkar (ekstrak arsip). Analisis statis (dekompilasi DEX ke Java/Smali) belum dilakukan.
