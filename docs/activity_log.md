# Activity Log

## 2026-09-23 — Atur rules catatan proyek

### Tujuan
Agar agent menulis riwayat kerja dan fakta yang harus diingat ke file yang benar.

### Perubahan
- `.cursor/rules/activity-log.mdc`: arahkan log ke `docs/activity_log.md`, perluas cakupan ke investigasi, dan tulis aturan dalam bahasa Inggris.
- `.cursor/rules/project-understanding.mdc`: tambah aturan untuk mencatat fakta yang bertahan di `docs/pemahaman.md`.

### Status
Selesai.

## 2026-09-23 — Bongkar APK OKOK International

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
