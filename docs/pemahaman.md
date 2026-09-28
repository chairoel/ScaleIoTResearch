# Hal yang perlu dipahami

Catatan ini menjelaskan apa yang sedang dihadapi dan bagaimana membacanya. Riwayat pekerjaan ada di `activity_log.md`.

Setiap judul bagian memuat waktu pencatatan dalam WIB, format `YYYY-MM-DD HH:mm WIB`. Bagian yang sudah tertulis tidak diubah. Fakta baru atau koreksi ditambah sebagai bagian baru di atas bagian lama. Jika dua bagian bentrok, waktu pencatatan yang lebih baru yang berlaku.

Catatan baru yang menyebut class, method, atau simbol lain dari kode hasil bongkaran menyertakan tautan berkas dan cuplikan. Catatan lama tidak diubah untuk itu. Lokasi berkas untuk nama yang sudah tertulis ada di catatan terbaru dan di `protokol-frame-okok.md`.

## 2026-09-28 17:41 WIB — Rencana eksekusi HealthTrack dipecah per fase

Urutan bangun tetap enam fase di [rencana aplikasi Android](rencana-aplikasi-android.md). Rincian kerja ada di [android-dev/00-rencana-besar.md](android-dev/00-rencana-besar.md), lalu `fase-01` sampai `fase-06`. Pintu keluar tidak berubah. Langkah berikut tetap fase 1 parser; daftar kerjanya ada di [fase-01-modul-inti-parser.md](android-dev/fase-01-modul-inti-parser.md).

Baris layar 68,7 kg (tinggi 166 cm, umur 29, kelamin 1, impedansi 600 ohm) pada [`parse_default_z`](../rumus/cs_bias_v235.py) dipetakan sebagai berikut. BMI adalah `berat / (tinggi * tinggi) * 10000` (24,9). Lemak `bfp` (23,1). Massa lemak `bfp * berat / 100` (15,9). Rasio otot rangka `smm / berat * 100` (38,2). Otot rangka `smm` (26,2). Rasio otot `slp` (72,8). Massa otot `slm` (50,0). Air `bwp` (54,2). Massa air `bwp * berat / 100` (37,3). Viseral `vfl` (10,0). Tulang `bmc` dua desimal (2,77). Metabolisme `bmr` (1502,0). Protein `pp` (18,5). Tingkat kegemukan `(berat - swt) / swt * 100` (14,1). Umur tubuh `ma` (36,0). Berat tanpa lemak `berat - massa lemak`, dua desimal (52,84). Skor `sbc` (61) ikut dihitung dan tidak masuk daftar banding OKOK. Lemak kelamin 0 pada vektor yang sama 34,8. Pembulatan layar `HALF_UP`.

## 2026-09-28 10:15 WIB — HealthTrack memakai prefs dan Room

HealthTrack memakai keduanya. Preferensi lokal ada di DataStore bernama `healthtrack_prefs`. Profil tubuh dan hasil ukur ada di Room, tabel `tubuh` dan `ukur`, seperti [rencana aplikasi Android](rencana-aplikasi-android.md). Prefs tidak menyimpan baris ukur. Rules di `HealthTrack/.cursor` tidak melarang Room.

## 2026-09-28 09:12 WIB — Rekomendasi berikut: fase 1 parser HealthTrack

Langkah berikut: buat modul Gradle `inti` di [HealthTrack](../HealthTrack) dan pindahkan parser iklan, siaran, serta GATT ke Kotlin, dengan uji JUnit dari vektor Python. Rencana dan pintu keluarnya ada di [rencana aplikasi Android](rencana-aplikasi-android.md) fase 1. Jangan mulai profil, Bluetooth, rumus, atau modul produk lain sebelum pintu keluar itu terpenuhi.

## 2026-09-28 09:12 WIB — Rencana tahap pertama ada di berkas sendiri

Aplikasi Android tahap pertama adalah [HealthTrack](../HealthTrack). Rencana bangunnya ada di [rencana aplikasi Android](rencana-aplikasi-android.md): modul JVM `inti` untuk parser dan rumus, Room untuk profil serta hasil, Bluetooth lewat API platform, v235 sebelum vA019, siaran terenkripsi ditolak. Modul di luar satu sesi ukur tetap belum dimulai.

## 2026-09-27 12:00 WIB — Rekomendasi berikut: biarkan rumus v235

Daftar indeks OKOK pada 68,7 kg sudah cocok dengan [`parse_default_z`](../rumus/cs_bias_v235.py). Rumus itu tidak diubah. Skor tidak ada di daftar indeks. Modul di luar satu sesi ukur belum dimulai. Yang berikutnya adalah memilih satu modul produk dan membaca alur kliennya. Jangan membongkar seluruh DEX sebelum modul itu dipilih.

## 2026-09-27 12:00 WIB — Daftar indeks 68,7 kg cocok

Layar OKOK yang terbaca memuat berat 68,7 kg, BMI 24,9, lemak 23,1, massa lemak 15,9, rasio otot rangka 38,2, otot rangka 26,2 kg, rasio otot 72,8, massa otot 50,0 kg, air 54,2, massa air 37,3 kg, viseral 10,0, tulang 2,77 kg, metabolisme 1502,0, protein 18,5, tingkat kegemukan 14,1, umur tubuh 36,0, berat tanpa lemak 52,84 kg, umur 29, tinggi 166 cm. Semuanya sama dengan v235 pada kelamin 1 dan impedansi 600 ohm, pada jumlah desimal yang layar tampilkan. Tulang 2,77 adalah nilai rumus pada dua desimal. Skor tidak ada di daftar ini. Syarat 4 untuk daftar indeks ini tertutup.

## 2026-09-27 11:55 WIB — Rekomendasi berikut: cocokkan tulang, BMR, viseral, skor

Langkah berikut: baca tulang, BMR, viseral, dan skor pada layar OKOK yang sama (berat 68,7 kg, 27 Sep 2026 11:48) dan cocokkan dengan 2,8 kg, 1502, 10, dan 61. Profil OKOK untuk perbandingan ini tinggi 166 cm, umur 29, kelamin 1. Jangan mulai modul lain sebelum keempat angka itu cocok.

## 2026-09-27 11:55 WIB — Layar 68,7 kg cocok pada lemak dan air

Layar OKOK pukul 11:48 menunjukkan berat 68,7 kg. Tinggi 166 cm dan umur 29. Kelamin 1: pada kelamin 0 lemak v235 menjadi 34,8, bukan 23,1. Impedansi tidak tampil di layar. Impedansi 600 ohm menghasilkan lemak 23,1 dan air 54,2 sekaligus. Pada 590 ohm lemak menjadi 23,0. Pada 610 ohm lemak menjadi 23,2.

Satu desimal yang sama dengan layar: BMI 24,9, lemak 23,1, massa lemak 15,9, rasio otot rangka 38,2, rasio otot 72,8, air 54,2, massa air 37,3, umur metabolik 36. Massa lemak mengikuti [`getFM`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java). BMI mengikuti [`getBMI`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java).

```909:911:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getFM() {
        return (getBFR() * this.Wt) / 100.0f;
    }
```

```903:907:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getBMI() {
        float f = this.Wt;
        float f2 = this.H;
        return (f / (f2 * f2)) * 100.0f * 100.0f;
    }
```

Tulang, BMR, viseral, dan skor di foto selebar 126 piksel tidak terbaca cukup untuk dicocokkan. Nilai rumusnya 2,8 kg, 1502, 10, dan 61. Syarat 4 belum tertutup.

## 2026-09-26 20:09 WIB — Rekomendasi berikut: bandingkan laporan 68,65 kg

Bandingkan berat 68,65 kg dan komposisi laporan v235 dengan aplikasi OKOK pada timbangan yang sama. Profil yang dipakai tinggi 170 cm, umur 30, kelamin 1. Siaran timbangan ini tidak menerima sambungan, jadi notify GATT tidak masuk. GATT dipakai lagi hanya bila ada iklan yang menerima sambungan.

## 2026-09-26 20:09 WIB — Siaran terkunci tidak menerima sambungan

Pada `D92E955D-DA1E-5928-BD8B-D23EDAD2CD92`, setiap iklan selama dua kali naik timbangan membawa `kCBAdvDataIsConnectable` salah. Notify tidak dipasang. Sesi tanpa berat siaran berhenti di menunggu berat. Frame terkunci `c06b1ad117700a0125f8f2f038ca3a` adalah header `0xC0` versi 1, product id 2561, device type 2, impedansi 600 ohm, berat 68,65 kg. Berat itu [`okokBroadcasetV2Parser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java) `weight`.

```169:171:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        WeightParserReturn weightParserReturnParser = WeightUnitUtil.Parser(bArr2[0], bArr2[c], this.scaleProperty, false);
        this.weight = weightParserReturnParser.kgWeight;
        this.scaleWeight = weightParserReturnParser.scaleWeight;
```

[`pakai_berat_siaran`](../aplikasi/sesi_ukur.py) menutup sesi dari berat itu bila GATT belum ada. [`putuskan_berat`](../aplikasi/sesi_ble.py) memanggilnya saat iklan tidak menerima sambungan. Berat GATT yang sudah masuk tidak diganti. Dengan profil tersimpan 170 cm, umur 30, kelamin 1, laporan v235: lemak 21,151988983154297, otot 27,247825622558594, air 54,7817497253418, viseral 9, skor 67. Syarat 4 belum tertutup.

## 2026-09-26 18:27 WIB — Rekomendasi berikut: naik ke timbangan, lalu sesi

Langkah berikut: naik ke timbangan supaya siaran OKOK muncul, tutup aplikasi OKOK di ponsel, lalu jalankan `python -m aplikasi sesi`. Sambungan dimulai pada siaran pertama yang menerima koneksi, pemindaian berhenti, notify dipasang, lalu pemindaian dinyalakan lagi untuk impedansi terkunci. Syarat 4 tetap perbandingan berat dan komposisi pada timbangan yang sama.

## 2026-09-26 18:27 WIB — FSAC menyambung pada siaran pertama

[`getConnectMode`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/ConfigurableDeviceUtil.java) memakai FSAC, kecuali ponsel Xiaomi yang `DEVICE`-nya diawali `HM`. Pada FSAC, [`handleBroadcastInfo`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java) memanggil `success` begitu MAC cocok. Callback itu menghentikan pemindaian lalu [`connectGATT`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java). Kunci impedansi bukan syarat sambungan.

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

[`boleh_sambung`](../aplikasi/sesi_ble.py) sekarang mengikuti itu. Siaran macOS dengan `kCBAdvDataIsConnectable` salah tidak disambung. Setelah notify RX aktif, pemindaian dinyalakan lagi supaya impedansi terkunci tetap masuk. Sesi 70 detik pada 18:27 tidak menerima siaran OKOK dan berhenti di menunggu impedansi. Pemindaian singkat sesudahnya melihat perangkat BLE lain, jadi radio berjalan. Timbangan saat itu tidak menyiarkan. Syarat 4 belum tertutup.

## 2026-09-26 16:02 WIB — GATT tetap habis waktu setelah pemindaian berhenti

Enam percobaan `BleakClient` ke `D92E955D-DA1E-5928-BD8B-D23EDAD2CD92` habis waktu setelah pemindaian dihentikan. Siaran terkunci tetap masuk, impedansi 600 ohm, berat sekitar 68,5–68,9 kg. Notify belum tercatat. Sesi berhenti di menunggu berat.

## 2026-09-26 15:58 WIB — Rekomendasi berikut: ulang sesi GATT

Langkah berikut: hentikan perintah `sesi` yang sedang berjalan, lalu jalankan `python -m aplikasi sesi` lagi. Sambungan menunggu siaran terkunci, pemindaian berhenti, lalu notify dicoba sampai tiga kali. Bila waktu sambungan habis, tutup aplikasi OKOK di ponsel. Syarat 4 tetap perbandingan berat dan komposisi pada timbangan yang sama.

## 2026-09-26 15:58 WIB — Sambungan GATT habis waktu

Pesan `sambungan gagal:` tanpa teks adalah `TimeoutError`. Percobaan itu jalan bersama pemindaian dan tidak diulang. Siaran terkunci dari `D92E955D-DA1E-5928-BD8B-D23EDAD2CD92` sudah membawa impedansi 600 ohm. Notify belum tercatat. [`dengar`](../aplikasi/sesi_ble.py) sekarang menghentikan pemindaian sebelum `BleakClient`.

## 2026-09-26 15:52 WIB — Siaran timbangan terdekat belum terkunci

Pemindaian 15 detik menerima siaran OKOK dari alamat `D92E955D-DA1E-5928-BD8B-D23EDAD2CD92`. Siaran itu terbuka, impedansi 0 ohm, dan beratnya bergerak. Notify GATT belum tercatat. Sesi tetap menunggu impedansi. Izin Bluetooth proses itu cukup untuk menerima iklan. Catatan 15:51 yang menyebut pemindaian berhenti di izin Bluetooth tidak berlaku.

## 2026-09-26 15:51 WIB — Rekomendasi berikut: sesi Bluetooth pada timbangan nyata

Langkah berikut: jalankan `python -m aplikasi sesi` dari terminal yang diizinkan mengakses Bluetooth, naik ke timbangan, lalu bandingkan berat dan komposisi dengan aplikasi OKOK pada timbangan yang sama. Syaratnya siaran tidak terenkripsi yang membawa impedansi (`0xCA` versi 32 atau `0xC0`) dan berat GATT terkunci. Perintah itu mengisi [`SesiUkur`](../aplikasi/sesi_ukur.py) lewat [`PendengarSesi`](../aplikasi/sesi_ble.py). Aplikasi Android dan `libprotocol.so` menunggu hasil sesi nyata itu.

## 2026-09-26 15:51 WIB — Sesi dari iklan dan notify GATT

Perintah `python -m aplikasi sesi` memindai iklan dan memasang notify. Berat dan impedansi tetap lewat [`SesiUkur`](../aplikasi/sesi_ukur.py). Muatan iklan untuk [`parse_broadcast`](../rumus/siaran_okok.py) disusun [`muatan_dari_pabrik`](../rumus/iklan_okok.py) dari id pabrik 16-bit little-endian plus sisa byte. Pada scan record mentah, [`muatan_okok`](../rumus/iklan_okok.py) mengambil byte setelah tipe `0xFF` bila byte pertama `0xCA` atau `0xC0`.

[`getProtocalTypeByBroadcast`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java) berhenti pada blok pabrik atau daftar UUID 16-bit yang pertama. Pengambil muatan di repositori ini membaca rekaman sampai habis, jadi muatan OKOK tetap ketemu bila daftar UUID ada di depan.

```165:170:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java
                        if (b2 == -1) {
                            scanMsg.manufacturerData = new byte[bArrSubBytes.length - 1];
                            scanMsg.manufacturerData = BytesUtil.subBytes(bArrSubBytes, 1, scanMsg.manufacturerData.length);
                            byte b3 = bArrSubBytes[1];
                            if (b3 == -54 || b3 == -64) {
                                scanMsg.protocalType = CsBtUtil_v11.Protocal_Type.OKOK;
```

```205:207:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/scanner/BluetoothLeScannerCompat.java
                        if (z) {
                            break;
                        }
```

Notify OKOK dipasang pada RX layanan Chipsea. Sesi ini tidak menulis TX.

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

```861:864:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java
                    if ((properties | 16) > 0 && string.compareToIgnoreCase(getCharacteristicUUID(true)) == 0) {
                        this.mNotifyCharacteristic = bluetoothGattCharacteristic;
                        setCharacteristicNotification(bluetoothGattCharacteristic, true);
                        LogUtil.i(TAG, "-------- got NOTIFY characteristic --------");
```

Alamat yang disimpan adalah alamat dari tumpukan Bluetooth komputer. Pada macOS itu UUID CoreBluetooth, bukan MAC radio timbangan. Pembandingan syarat 4 memakai berat dan komposisi. Syarat 4 belum tertutup.

## 2026-09-26 14:29 WIB — Rekomendasi berikut: sesi pada timbangan nyata

Langkah berikut: jalankan satu sesi pada timbangan nyata, lalu bandingkan berat dan komposisi [`SesiUkur`](../aplikasi/sesi_ukur.py) dengan aplikasi sumber pada timbangan yang sama. Syaratnya siaran tidak terenkripsi yang membawa impedansi (`0xCA` versi 32 atau `0xC0`) dan berat GATT terkunci. Profil tinggi, umur, dan jenis kelamin sudah tersimpan lewat [`Penyimpan`](../aplikasi/simpan.py). `libprotocol.so` dan fitur di luar satu sesi ukur menunggu hasil sesi nyata itu.

## 2026-09-26 14:29 WIB — Aplikasi satu sesi ukur

Sesi tahap pertama ada di [`SesiUkur`](../aplikasi/sesi_ukur.py). Berat yang disimpan adalah berat GATT dengan `lock_flag == 1` dan `history == False`. Impedansi yang masuk rumus adalah `impedance_ohm` pada siaran terkunci. Satu nilai memakai [`parse_default_z`](../rumus/cs_bias_v235.py). Sepuluh nilai memakai [`parse_multi_frequency`](../rumus/cs_bias_vA019.py). Angka komposisi paket GATT tetap di parser dan tidak mengisi laporan. Data tubuh serta hasil ukur ada di [`Penyimpan`](../aplikasi/simpan.py). Perintahnya `python -m aplikasi`. Syarat 4 belum tertutup.

## 2026-09-26 14:10 WIB — getVFR dari classes4.dex

[`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) di Java hanya sisa `throw`. Badan method ada di [`classes4.dex`](../ScaleHealtSource/base/classes4.dex). Tulis ulang ada di [`rumus/vfr_okok.py`](../rumus/vfr_okok.py).

Method ini yang masuk skor lewat [`getScoreWithAge`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java). Field laporan `vfl` tetap angka native. Pada `cs_bias_v235`, angka itu field `VFR` yang disimpan [`setVfl`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java).

```1389:1389:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
            float scoreWithAge = getScoreWithAge(this.H, this.Wt, this.Sex, this.Age, getBFR(), getSLM(), getVFR());
```

```851:851:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
            setVfl((float) cSBiasV235RespCs_bias_v235.data.VFR);
```

`DualFrequency` dan `MultiFrequency` mengembalikan `vfl`. Selain itu, umur 17 atau kurang menghasilkan 0 sebelum pilihan bias. Rumus umur di atas 17 memakai float32: tinggi, berat, umur, impedansi, lalu konstanta. Jenis kelamin 1 laki-laki. Pada 8 elektroda perempuan, konstanta dikurangi. Jalur lain menambahkan konstanta. Jalur yang bukan 8 elektroda mengalikan umur dengan `1.0f` dulu.

Bagian pecahan di bawah 0,5 tetap bilangan bulat. Selain itu ditambah 0,5, tanpa naik ke bilangan berikutnya. Hasil di bawah 1 menjadi 1. Hasil di atas 59 menjadi 59. Pada 8 elektroda, angka itu yang dikembalikan. Pada timbangan lain, `mBIASV235Success` mengembalikan `vfl`, termasuk bila umur 17 atau kurang.

Koefisien yang bukan 8 elektroda sama dengan baris viseral [`_COEFFICIENT`](../rumus/cs_bias_v235.py) dibagi 10000. Perkaliannya tetap pada field float, bukan jalur int berskala di dalam `.so`.

## 2026-09-26 13:52 WIB — Rakitan GATT perintah 20

Perintah 20 di [`chipseaStraightFrame.process`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java) menambah byte muatan ke `lstRoleBuffer` sesuai urutan datang. Paket nomor 1 tidak mengosongkan buffer itu. Rakitan selesai bila kedua nibble bertanda sama, tanpa memeriksa ukuran buffer. Indeks `0x00` dan `0x88` ikut selesai. Setelah berhasil, buffer dikosongkan lalu diisi null. Hasilnya [`CsFatConfirm`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatConfirm.java): berat di offset 0–1, properti di offset 2, id peran 4 byte dari offset 3. [`setWeight`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatConfirm.java) membagi 10 lagi. Id yang tidak muat 4 byte, dan id di atas 2147483647, menjadi 0. Parser ada di [`GattParser`](../rumus/gatt_okok.py). Frame yang tidak memuat byte muatan yang diumumkan ditolak sebelum byte itu masuk buffer.

```162:172:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                case 20:
                    byte[] bArrSplitPackInfo = splitPackInfo(bArr[4]);
                    int i2 = b2 - 2;
                    if (this.lstRoleBuffer == null) {
                        this.lstRoleBuffer = new ArrayList<>();
                    }
                    for (int i3 = 0; i3 < i2; i3++) {
                        this.lstRoleBuffer.add(Byte.valueOf(bArr[i3 + 5]));
                    }
                    if (bArrSplitPackInfo[0] == bArrSplitPackInfo[1]) {
```

```16:18:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatConfirm.java
    public void setWeight(double d) {
        this.weight = d / 10.0d;
    }
```

[`CsBtUtil_v11`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java) meneruskan objek itu lewat `matchUserMsg`. Di hasil dekompilasi ini, [`BoundDeviceActivity.matchUserMsg`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java) kosong.

```1024:1028:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java
            if (enumprocessresultProcess == enumProcessResult.Match_User_Msg && (straightframefactory instanceof chipseaStraightFrame)) {
                chipseaStraightFrame chipseastraightframe = (chipseaStraightFrame) straightframefactory;
                OnBluetoothListener onBluetoothListener5 = bluetoothListener;
                if (onBluetoothListener5 != null) {
                    onBluetoothListener5.matchUserMsg(chipseastraightframe.getFatConfirm());
```

```104:106:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java
    public void matchUserMsg(CsFatConfirm csFatConfirm) {
    }
```

## 2026-09-26 13:30 WIB — Rekomendasi berikut: aplikasi satu sesi ukur

Langkah berikut: bangun aplikasi tahap pertama untuk satu sesi ukur. Siaran lewat [`parse_broadcast`](../rumus/siaran_okok.py), berat GATT lewat [`GattParser`](../rumus/gatt_okok.py), laporan lewat [`rumus/cs_bias_v235.py`](../rumus/cs_bias_v235.py) atau [`rumus/cs_bias_vA019.py`](../rumus/cs_bias_vA019.py). Impedansi laporan datang dari siaran, bukan dari angka lemak paket. Aplikasi menyimpan hasil ukur dan data tubuh yang rumus butuhkan. Perintah 20, [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java), dan `libprotocol.so` bukan langkah ini. Syarat 4 baru tertutup setelah satu sesi pada timbangan nyata.

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

## 2026-09-26 13:30 WIB — Rakitan GATT perintah 18 dan 19

Rakitan ada di [`GattParser`](../rumus/gatt_okok.py). Perintah 18 dan 19 punya buffer sendiri. Paket nomor 1 mengosongkan buffer. Rakitan selesai bila nomor paket sama dengan jumlah paket dan isi buffer sama dengan jumlah itu. Paket terakhir yang datang sebelum jumlahnya lengkap mengosongkan buffer. Setelah berhasil, buffer diisi null; paket berikutnya yang bukan nomor 1 ditolak.

[`splitPackInfo`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java) menggeser byte bertanda. Nibble 8 sampai 15 menjadi negatif, jadi jumlah paket 8 atau lebih tidak lolos pemeriksaan ukuran buffer.

```22:24:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
    private byte[] splitPackInfo(byte b) {
        return new byte[]{(byte) (((byte) (b << 4)) >> 4), (byte) (b >> 4)};
    }
```

```226:231:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
            if (bArrSplitPackInfo[0] == bArrSplitPackInfo[1]) {
                if (this.lstBuffer.size() == bArrSplitPackInfo[0]) {
                    return true;
                }
                this.lstBuffer.clear();
                return false;
```

Pada hasil rakitan, tanda kunci dipaksa 1. Perintah 19 menyimpan waktu Unix detik dari offset 0–3 sebagai tanggal, dan menandai riwayat. Perintah 18 tidak memakai waktu itu. Otot dihitung ulang dari otot dibagi berat, hanya di jalur ini. Hasil di bawah 50 disimpan sebagai persen. Hasil 50 atau lebih memakai nilai otot yang sudah tersimpan dan dibatasi 50. Angka itu lalu dikali 10, dipotong ke int, dan [`setMuscle`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java) membagi 10 lagi. Angka lemak paket tetap bukan laporan.

```143:150:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                        double muscle = (this.fatScale.getMuscle() / this.fatScale.getWeight()) * 100.0d;
                        if (muscle >= 50.0d) {
                            muscle = this.fatScale.getMuscle();
                            if (muscle >= 50.0d) {
                                muscle = 50.0d;
                            }
                        }
                        this.fatScale.setMuscle((int) (muscle * 10.0d));
```

[`bytesToInt`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) memakai `Integer.parseInt`. Empat byte di atas 2147483647 menjadi 0. Id peran dan waktu Unix setelah 2038-01-19 03:14:07 UTC ikut aturan itu.

```75:80:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
    public static int bytesToInt(byte[] bArr) {
        try {
            return Integer.parseInt(bytesToHexString(bArr), 16);
        } catch (NumberFormatException unused) {
            return 0;
        }
```

## 2026-09-26 13:22 WIB — Rekomendasi berikut: parser GATT perintah 18 dan 19

Langkah berikut: rakitan beberapa paket untuk perintah 18 dan 19 di [`chipseaStraightFrame.process`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java), di [`rumus/gatt_okok.py`](../rumus/gatt_okok.py). Berat sesi versi 16 serta perintah 0 dan 1 pada versi 17 sudah ada di berkas itu. Perintah 20 adalah daftar peran, bukan berat. Setelah rakitan, otot dihitung ulang dari otot dibagi berat. Angka lemak paket tetap bukan laporan. Laporan tetap [`rumus/cs_bias_v235.py`](../rumus/cs_bias_v235.py) atau [`rumus/cs_bias_vA019.py`](../rumus/cs_bias_vA019.py). Antarmuka aplikasi, [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java), dan `libprotocol.so` bukan langkah ini.

```113:121:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
            switch (b4) {
                case BtStatus.CHARACTER_NOTIFI_SUCCESS /* 18 */:
                case 19:
                    if (packageProcess(bArr)) {
                        if (b4 == 18) {
                            bArrConvertMap2ByteArray = ConvertMap2ByteArray(false);
                        } else {
                            bArrConvertMap2ByteArray = ConvertMap2ByteArray(true);
                        }
```

```143:150:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                        double muscle = (this.fatScale.getMuscle() / this.fatScale.getWeight()) * 100.0d;
                        if (muscle >= 50.0d) {
                            muscle = this.fatScale.getMuscle();
                            if (muscle >= 50.0d) {
                                muscle = 50.0d;
                            }
                        }
                        this.fatScale.setMuscle((int) (muscle * 10.0d));
```

## 2026-09-26 13:22 WIB — Parser GATT versi 16 dan perintah 0 serta 1

Parser ada di [`rumus/gatt_okok.py`](../rumus/gatt_okok.py). Versi 16 membaca berat dari offset 5–6 dan properti dari offset 4. Tanda kunci adalah bit 0 properti itu. Komposisi paket hanya diisi bila bit itu 1, lalu disempitkan [`CsFatScale`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java). Angka itu bukan laporan `cs_bias`. Pada versi 16 otot tidak dihitung ulang dari berat.

```86:96:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
            byte cmdId = BytesUtil.getCmdId(b3);
            this.fatScale.setLockFlag(cmdId);
            WeightParserReturn weightParserReturnParser = WeightUnitUtil.Parser(bArr[5], bArr[6], b3, false);
            this.fatScale.setWeight(weightParserReturnParser.kgWeight * 10.0d);
            this.fatScale.setScaleWeight(weightParserReturnParser.scaleWeight);
            this.fatScale.setScaleProperty(b3);
            if (cmdId > 0) {
                this.fatScale.setAxunge(BytesUtil.bytesToInt(bArrSubBytes));
                this.fatScale.setWater(BytesUtil.bytesToInt(bArrSubBytes2));
                this.fatScale.setMuscle(BytesUtil.bytesToInt(bArrSubBytes3));
```

Pada versi 17 perintah 0 dan 1, tanda kunci adalah byte perintah di offset 3, bukan bit kunci properti. Properti ada di offset 11. Tidak ada komposisi. [`setWeight`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java) membagi 10 lagi, jadi kilogram yang tersimpan sama dengan `kgWeight`.

```101:110:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
            if (b4 == 0 || b4 == 1) {
                byte[] bArrSubBytes7 = BytesUtil.subBytes(bArr, 5, 2);
                CsFatScale csFatScale2 = new CsFatScale();
                this.fatScale = csFatScale2;
                csFatScale2.setHistoryData(false);
                this.fatScale.setLockFlag(b4);
                this.fatScale.setScaleProperty(bArr[11]);
                WeightParserReturn weightParserReturnParser2 = WeightUnitUtil.Parser(bArrSubBytes7[0], bArrSubBytes7[1], this.fatScale.getScaleProperty(), false);
                this.fatScale.setWeight(weightParserReturnParser2.kgWeight * 10.0d);
                this.fatScale.setScaleWeight(weightParserReturnParser2.scaleWeight);
```

[`subBytes`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) mengembalikan null bila potongan tidak muat. [`bytesToInt`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) pada null menjadi 0. Parser mengisi komposisi 0 untuk potongan yang tidak muat pada versi 16 yang terkunci. Frame yang tidak memuat byte yang diindeks langsung ditolak. Perintah 18, 19, 20, dan versi lain ditolak, bukan dikembalikan sebagai data tunggu.

```19:22:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
    public static byte[] subBytes(byte[] bArr, int i, int i2) {
        int i3;
        if (i2 <= 0 || bArr.length < (i3 = i + i2)) {
            return null;
```

```75:80:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
    public static int bytesToInt(byte[] bArr) {
        try {
            return Integer.parseInt(bytesToHexString(bArr), 16);
        } catch (NumberFormatException unused) {
            return 0;
        }
```

`ori_visceral_fat` menyimpan nilai mentah sebelum dibagi 10. Nilai 25600 tetap di sana walaupun lemak visceral yang ditampilkan menjadi 0. Pemeriksaan jenis perangkat di [`CsBtUtil_v11.handleConnectedInfo`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java) memakai angka mentah itu.

```192:198:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java
    public void setVisceral_fat(double d) {
        this.ori_visceral_fat = d;
        double d2 = d / 10.0d;
        if (d2 >= 100.0d || d2 > 59.0d) {
            d2 = 0.0d;
        }
        this.visceral_fat = d2;
```

## 2026-09-26 13:15 WIB — Rekomendasi berikut: parser GATT sesi ukur

Langkah berikut: tulis parser GATT [`chipseaStraightFrame.process`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java) untuk versi 16 dan perintah 0 serta 1 pada versi 17. Siaran tidak terenkripsi sudah ada di [`rumus/siaran_okok.py`](../rumus/siaran_okok.py). Berat sesi yang tersambung dibaca dari GATT ini. Angka lemak pada paket versi 16 bukan komposisi laporan. Laporan tetap [`rumus/cs_bias_v235.py`](../rumus/cs_bias_v235.py) atau [`rumus/cs_bias_vA019.py`](../rumus/cs_bias_vA019.py). Antarmuka aplikasi, [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java), dan `libprotocol.so` bukan langkah ini.

```71:74:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
        if (b == 16) {
            byte b3 = bArr[4];
            BytesUtil.subBytes(bArr, 5, 2);
            byte[] bArrSubBytes = BytesUtil.subBytes(bArr, 7, 2);
```

```99:102:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
        if (b == 17) {
            byte b4 = bArr[3];
            if (b4 == 0 || b4 == 1) {
                byte[] bArrSubBytes7 = BytesUtil.subBytes(bArr, 5, 2);
```

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

## 2026-09-26 13:15 WIB — Timbangan terenkripsi di luar rilis pertama

Keputusan syarat 2 di `definisi-selesai.md`: timbangan terenkripsi tidak masuk rilis pertama. Bit itu bit 7 pada byte offset 4 siaran `0xC0`. Repositori tidak memuat nilai `data` bind maupun entri `okok_scale_encrypted_key_`. Siaran `0xCA`, siaran `0xC0` tanpa bit itu, dan GATT header `0xCA` tetap masuk.

```129:129:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        boolean z = (bArr[4] & (-128)) == -128;
```

[`parse_broadcast`](../rumus/siaran_okok.py) menolak siaran terenkripsi. Java mengisi berat 0 bila kunci kosong. Parser itu juga menolak frame yang lebih pendek dari field yang dibaca. Pada `0xC0` lebih pendek dari 9 byte, Java kembali lebih awal dan berat tetap 0.

```126:128:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        if (bArr.length < 9) {
            return;
        }
```

```160:164:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        if (z) {
            int iOkokBroadcasetV2ParserDecrypt2 = okokBroadcasetV2ParserDecrypt(BytesUtil.bytesToInt(bArr2), bytesFromHexStr);
            if (bytesFromHexStr == null) {
                iOkokBroadcasetV2ParserDecrypt2 = 0;
            }
```

Di [`classes4.dex`](../ScaleHealtSource/base/classes4.dex), `bytesToHexString` memakai `and-int/lit16` dengan literal `0xFF`. [`DataType.EXTEND`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/DataType.java) bertipe byte bernilai -1. Tampilan dekompilasi `b & DataType.EXTEND` memakai topeng 8 bit itu.

```49:51:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
        for (byte b : bArr) {
            String hexString = Integer.toHexString(b & DataType.EXTEND);
            if (hexString.length() < 2) {
```

```5:5:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/DataType.java
    public static final byte EXTEND = -1;
```

## 2026-09-26 11:26 WIB — Rekomendasi berikut: contoh kunci siaran 0xC0

Langkah berikut: penuhi syarat 2 di `definisi-selesai.md`. Butuh satu nilai `data` dari bind, atau satu entri `okok_scale_encrypted_key_` ditambah MAC. Bila contoh dari perangkat tidak ada, keputusan tertulis bahwa timbangan terenkripsi tidak masuk rilis pertama. Kedua rumus bias laporan OKOK sudah ada di [`rumus/cs_bias_v235.py`](../rumus/cs_bias_v235.py) dan [`rumus/cs_bias_vA019.py`](../rumus/cs_bias_vA019.py). Aplikasi sendiri belum dimulai. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) belum terdekompilasi dan bukan langkah ini.

```969:974:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVFR() {
        /*
            Method dump skipped, instructions count: 248
            To view this dump add '--comments-level debug' option
        */
        throw new UnsupportedOperationException("Method not decompiled: com.chipsea.code.algorithm.CsAlgoBuilder.getVFR():float");
```

## 2026-09-26 11:26 WIB — cs_bias_vA019 ditulis ulang

Tulis ulang ada di [`rumus/cs_bias_vA019.py`](../rumus/cs_bias_vA019.py). [`cs_bias_vA019`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java) menerima jenis kelamin, umur, tinggi dalam persepuluhan sentimeter, berat dalam persepuluhan kilogram, mode, dan sepuluh impedansi dalam persepuluhan ohm. Jenis kelamin 0 perempuan, 1 laki-laki.

```7:10:ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java
    public static native CSBiasVA019Resp cs_bias_vA019(CSBiasPersonalInfoVA019 cSBiasPersonalInfoVA019);

    static {
        System.loadLibrary("chipsea_bias_vA019");
```

Pemanggil Java menyetel mode 0. Tinggi dan berat lewat `Math.round` setelah dikali 10. Urutan impedansi: tangan kanan, tangan kiri, batang, kaki kanan, kaki kiri, lalu frekuensi kedua dengan urutan yang sama.

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

Kode gagal positif dan berurutan: 1 masukan kosong, 2 berat di luar 20,0–250,0 kg, 3 tinggi di luar 90,0–220,0 cm, 4 umur di luar 6–99, 5 jenis kelamin selain 0 dan 1, 6 impedansi. Pemeriksaan impedansi hanya berjalan pada mode 0. Tungkai harus 100,0–750,0 ohm. Batang, indeks 2 dan 7, harus 10,0–65,0 ohm.

`metric_regression` menghitung satu metrik mode 0. Skala campuran regresi dan polinomial adalah float32 `0x3e99999a`. `parse_multi_frequency` mengikuti penyempitan [`toParserMultiFrequencyData`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java). Field yang di-cast `(float)` disimpan sebagai float32. `sfm`, `sfp`, `icw`, `ecw`, massa sel, dan derajat obesitas tetap double. [`setVfl`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) menerima float, jadi `vfl` yang aslinya bilangan bulat disimpan sebagai float.

```704:704:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
                setBfp((float) cSBiasVA019RespCs_bias_vA019.data.bfp);
```

```310:312:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public void setVfl(float f) {
        this.vfl = f;
    }
```

```739:744:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
                setSfm(cSBiasVA019RespCs_bias_vA019.data.sfm);
                setSfp(cSBiasVA019RespCs_bias_vA019.data.sfp);
                setIcw(cSBiasVA019RespCs_bias_vA019.data.icw);
                setEcw(cSBiasVA019RespCs_bias_vA019.data.ecw);
                setBody_cell_mass(cSBiasVA019RespCs_bias_vA019.data.body_cell_mass);
                setObesity_degree(cSBiasVA019RespCs_bias_vA019.data.obesity_degree);
```

## 2026-09-26 08:42 WIB — Rekomendasi berikut: bongkar cs_bias_vA019

Langkah berikut: tulis ulang `cs_bias_vA019` di [`libchipsea_bias_vA019.so`](../ScaleHealtSource/split_config.arm64_v8a/lib/arm64-v8a/libchipsea_bias_vA019.so). Pada frekuensi ganda dan multi, [`getBFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) mengembalikan `getBfp()`, dan nilai itu diisi dari native ini.

```700:702:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
        try {
            CSBiasAPI.CSBiasVA019Resp cSBiasVA019RespCs_bias_vA019 = CSBiasAPI.cs_bias_vA019(cSBiasPersonalInfoVA019);
            if (cSBiasVA019RespCs_bias_vA019.result == 0) {
```

Timbangan satu frekuensi yang bukan 8 elektroda sudah tertutup [`rumus/cs_bias_v235.py`](../rumus/cs_bias_v235.py). Syarat langkah ini adalah kelas pemanggil yang sudah didekompilasi. Aplikasi sendiri belum dimulai. Library asli tidak dipanggil dari aplikasi. Syarat 2, satu nilai `data` dari bind atau entri `okok_scale_encrypted_key_` ditambah MAC, tetap terbuka.

## 2026-09-26 08:42 WIB — cs_bias_v235 ditulis ulang

Tulis ulang ada di [`rumus/cs_bias_v235.py`](../rumus/cs_bias_v235.py). [`cs_bias_v235`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java) menerima jenis kelamin, umur, tinggi dalam cm, berat kali 100, dan impedansi kali 10. Jenis kelamin 0 perempuan, 1 laki-laki.

```5:8:ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java
    public static native CSBiasV235Resp cs_bias_v235(int i, int i2, int i3, int i4, int i5);

    static {
        System.loadLibrary("chipsea_bias_v235");
```

Rentang yang menghasilkan `result == 0`: berat 20–250 kg, tinggi 90–220 cm, umur 18–99, impedansi 200–1500 ohm. Kode gagal: -2 berat, -3 tinggi, -4 umur, -5 jenis kelamin, -6 impedansi. Pemeriksaan berjalan dalam urutan itu.

`parse_default_z` di modul yang sama memotong masukan seperti [`parseDefaultZ`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java), menyimpan hasil sebagai float, dan menyimpan BMR sebagai int. SLP dihitung di Java: SLM dibagi berat, kali 100. Itu tidak ada di dalam `.so`.

Lemak viseral yang disimpan laporan adalah field `vfl`. [`getVfl`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) mengembalikan field itu. [`getVFR`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) belum terdekompilasi. Pemanggilnya [`getScoreWithAge`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java).

```306:307:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
    public float getVfl() {
        return this.vfl;
```

```1389:1389:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
            float scoreWithAge = getScoreWithAge(this.H, this.Wt, this.Sex, this.Age, getBFR(), getSLM(), getVFR());
```

Inti JNI adalah ekspor `bia_calc` di [`libchipsea_bias_v235.so`](../ScaleHealtSource/split_config.arm64_v8a/lib/arm64-v8a/libchipsea_bias_v235.so). Library yang sama juga mengekspor `bia_bmc`, `bia_bmi`, dan `bia_round_off`. `bia_calc` tidak memanggil ketiganya. String versi di library itu `BIA_V2355`.

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
