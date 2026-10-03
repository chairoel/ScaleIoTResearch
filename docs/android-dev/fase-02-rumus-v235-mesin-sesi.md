# Fase 2 — Rumus v235 dan mesin sesi

Syarat mulai: pintu keluar [fase 1](fase-01-modul-inti-parser.md), sudah terpenuhi di kode.

Sumber perilaku: [cs_bias_v235.py](../../rumus/cs_bias_v235.py) dan [sesi_ukur.py](../../aplikasi/sesi_ukur.py). `getVFR` di Java tidak dipindahkan. Viseral yang disimpan `parse_default_z` adalah field `vfl`.

Lapisan: `domain` saja. Tidak mengimpor `android.*`, `data`, Room, atau Compose. Tidak memakai `ProtocolUtils.f32`; pembantu float rumus tinggal di `domain/formula`. Tidak menambah modul Gradle, Hilt, atau layar.

## Yang dihasilkan

Di `com.mascill.healthtrack.domain.formula`:

- `CsBiasV235` — `csBiasV235` dan `parseDefaultZ`.
- Pembantu float yang setara `_f32` dan `_fma`: tiap operasi yang di Python dipaksa binary32 memakai `Float`.

Di `com.mascill.healthtrack.domain.model` dan `domain/session`:

- `BodyData` — tinggi cm, umur, jenis kelamin. Jenis kelamin selain 0 dan 1 ditolak.
- `MeasurementResult` — mac, product id, berat kg, tampilan berat, impedansi, nama rumus, kode, laporan.
- `MeasurementRepository` — antarmuka domain. Satu method `save` untuk hasil. Implementasi Room menyusul di fase 3. Uji fase ini memakai penyimpan palsu di memori. Jangan menamai tipe ini `ResultStore`.
- `calculateReport` — satu nilai ohm memanggil `parseDefaultZ` dan mengembalikan nama `v235`. Sepuluh nilai belum punya rumus; cabang itu ditutup di [fase 6](fase-06-frekuensi-ganda.md). Jumlah selain 1 dan 10 menolak sesi.
- `MeasurementSession` — keadaan `menunggu impedansi`, `menunggu berat`, `selesai`, atau `rumus` plus kode.

Aturan mesin, sudah terbukti di Python:

1. Impedansi laporan adalah `impedanceOhm` pada siaran terkunci (`ScaleTransmission.locked`). Siaran belum kunci tidak menimpa impedansi yang sudah ada.
2. Berat yang disimpan adalah `ScaleGatt` dengan `lockFlag == 1` dan `history == false`. Berat GATT yang sudah masuk tidak diganti siaran.
3. `applyBroadcastWeight` menutup sesi dari siaran terkunci bila GATT belum ada. Nama method ini bukan tipe frame. Tipe framenya tetap `ScaleTransmission`.
4. Sesi ditutup hanya bila rumus mengembalikan kode 0. Hasil pertama yang berhasil tetap, termasuk bila frame berat berikutnya datang.
5. Angka komposisi di dalam `ScaleGatt` (`axunge`, `water`, `muscle`, dan seterusnya) tidak mengisi laporan.

UseCase belum dibuat di fase ini. ViewModel belum ada. `MeasurementSession` memakai `MeasurementRepository` domain, bukan DAO.

## Pembulatan layar

Fungsi tampilan di `domain` (dipakai lagi oleh layar pada fase 5) membulatkan dengan `HALF_UP`. Uji membandingkan nilai yang sudah dibulatkan. Teks di layar nanti memakai koma desimal.

Vektor: `parseDefaultZ(1, 29, 166, 68.7, 600)`. Kelamin 0 pada vektor yang sama: lemak 34,8.

| Baris layar | Sumber | Tampil |
|---|---|---|
| BMI | `berat / (tinggi * tinggi) * 10000` | 24,9 |
| Lemak | `bfp` | 23,1 |
| Massa lemak | `bfp * berat / 100` | 15,9 |
| Rasio otot rangka | `smm / berat * 100` | 38,2 |
| Otot rangka | `smm` | 26,2 |
| Rasio otot | `slp` | 72,8 |
| Massa otot | `slm` | 50,0 |
| Air | `bwp` | 54,2 |
| Massa air | `bwp * berat / 100` | 37,3 |
| Viseral | `vfl` | 10,0 |
| Tulang | `bmc`, dua desimal | 2,77 |
| Metabolisme | `bmr`, satu desimal | 1502,0 |
| Protein | `pp` | 18,5 |
| Tingkat kegemukan | `(berat - swt) / swt * 100` | 14,1 |
| Umur tubuh | `ma` | 36,0 |
| Berat tanpa lemak | `berat - massa lemak`, dua desimal | 52,84 |
| Skor | `sbc` | 61 |

Skor ditampilkan karena rumus menghasilkannya. Daftar OKOK yang dibandingkan tidak memuat skor. Berat laporan memakai tampilan berat dari frame, bukan pembulatan ulang.

Nilai mentah pada vektor laki-laki itu, sebelum pembulatan layar: `bfp` 23,07963752746582, `smm` 26,2417049407959, `slp` 72,75165557861328, `slm` 49,980384826660156, `bwp` 54,229583740234375, `bmc` 2,7662100791931152, `pp` 18,53265953063965, `swt` 60,20000076293945, `vfl` 10, `bmr` 1502, `ma` 36, `sbc` 61. Lemak kelamin 0: 34,7588005065918.

## Langkah

1. Port `cs_bias_v235` beserta koefisien dan `parse_default_z` ke `domain/formula`.
2. Salin uji `rumus/test_cs_bias_v235.py` ke `app/src/test/java`: nilai sama dengan library, kode galat berurutan, laporan Java memotong float (`bfp` 21,062211990356445 pada masukan 1 / 30 / 170,9 / 70,56 / 500,4).
3. Port `MeasurementSession` dan `calculateReport` untuk satu ohm.
4. Salin `aplikasi/test_sesi_ukur.py` kelas `SesiUkurTest` kecuali `test_sepuluh_impedansi`. Uji itu menunggu `vA019`.
5. Tambah uji pembulatan tabel di atas, plus lemak 34,8 untuk kelamin 0.

Uji memakai JUnit 4 yang sudah di modul (`testImplementation(libs.junit)`), satu tugas `testDebugUnitTest` bersama uji parser. Jangan menambah runner kedua.

`SimpanDanPerintahTest` adalah perintah baris Python. Perintah itu tidak dipindahkan. Perilaku simpan profil dan hasil ditutup di fase 3 lewat Room.

## Pintu keluar

`./gradlew :app:testDebugUnitTest` lulus, termasuk v235 dan sesi satu ohm. Vektor 68,7 kg / 166 cm / 29 / kelamin 1 / 600 ohm menghasilkan angka tabel pada jumlah desimal yang sama.

## Belum dikerjakan

Layar, Room, DataStore, Bluetooth, UseCase, dan port `cs_bias_vA019.py`.
