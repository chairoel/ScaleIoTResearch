# Activity Log

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
