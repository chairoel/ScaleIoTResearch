# Rencana besar eksekusi HealthTrack

Tahap pertama adalah satu sesi ukur OKOK di [HealthTrack](../../HealthTrack). Isi produk, keputusan, dan pintu keluar ada di [rencana aplikasi Android](../rencana-aplikasi-android.md). Dokumen ini memecah urutan itu menjadi enam fase yang bisa dikerjakan satu per satu. Tiap fase punya berkas sendiri di folder ini.

HealthTrack sekarang templat Compose kosong: namespace `com.mascill.healthtrack`, minSdk 28, targetSdk 36, satu `MainActivity`. Perilaku yang dipindahkan sudah jalan di Python.

## Selesai artinya

Satu pengukuran di timbangan yang sama dengan uji 27 Sep 2026: berat dan daftar indeks cocok dengan aplikasi OKOK, profil tubuh tersimpan, hasil tetap ada setelah aplikasi ditutup. Jalur itu satu nilai ohm (`v235`). Sepuluh nilai ohm (`vA019`) adalah fase 6, sesudah tahap satu frekuensi lolos.

Di luar keenam fase: dapur, minum, olahraga, wearable, tali, puasa, VIP, iklan, analitik, PDF, akun server Chipsea, kunci siaran terenkripsi, `libprotocol.so`, dan pemanggilan library bias Chipsea.

## Urutan

Fase berikutnya dimulai setelah pintu keluar fase berjalan terpenuhi. `./gradlew :app:testDebugUnitTest` adalah pemeriksaan JUnit di komputer. Uji timbangan nyata hanya ada di fase 4.

```mermaid
flowchart LR
  f1[1 Parser] --> f2[2 Rumus v235 dan sesi]
  f2 --> f3[3 Profil dan Room]
  f3 --> f4[4 Sesi Bluetooth]
  f4 --> f5[5 Hasil dan riwayat]
  f5 --> f6[6 Frekuensi ganda]
```

| Fase | Berkas | Pintu keluar singkat |
|---|---|---|
| 1 | [fase-01-modul-inti-parser.md](fase-01-modul-inti-parser.md) | Uji iklan, siaran, dan GATT lulus di JUnit host |
| 2 | [fase-02-rumus-v235-mesin-sesi.md](fase-02-rumus-v235-mesin-sesi.md) | v235 dan mesin sesi satu ohm lulus; angka layar 68,7 kg cocok |
| 3 | [fase-03-profil-room.md](fase-03-profil-room.md) | Profil tersimpan, baris terbaru termuat, sesi terkunci tanpa profil |
| 4 | [fase-04-sesi-bluetooth.md](fase-04-sesi-bluetooth.md) | Berat dan indeks cocok dengan OKOK di timbangan yang sama |
| 5 | [fase-05-hasil-riwayat.md](fase-05-hasil-riwayat.md) | Satu hasil tersimpan, muncul di riwayat, tetap ada setelah aplikasi ditutup |
| 6 | [fase-06-frekuensi-ganda.md](fase-06-frekuensi-ganda.md) | Sepuluh ohm memilih `vA019` dan uji Python-nya lulus |

Fase 5 menutup tahap pertama untuk timbangan satu frekuensi. Fase 6 menutup timbangan yang mengirim sepuluh ohm.

## Letak kode

```text
HealthTrack/app/                satu-satunya modul Gradle
  src/main/java/com/mascill/healthtrack/
    domain/
      protocol/                 iklan, siaran, GATT
      formula/                  v235 pada fase 2, vA019 pada fase 6
      session/                  BodyData, MeasurementSession, MeasurementResult
    data/
      local/                    DataStore healthtrack_prefs dan Room
      ble/                      pemindai dan GATT
    presentation/               empat layar Compose
  src/test/java/                JUnit host, tanpa emulator
```

HealthTrack satu modul Gradle, yaitu `app` yang sudah ada. Parser, rumus, dan mesin sesi tinggal di paket `domain` dan tidak mengimpor `android.*`, Room, atau Compose. Uji mereka ada di `src/test` dan jalan di komputer lewat `./gradlew :app:testDebugUnitTest`. Modul Gradle kedua tidak dibuat.

Tahap ini tidak memasang supabase-kt, Hilt, OkHttp, atau Retrofit. Model sesi adalah `BodyData`, `MeasurementResult`, dan `MeasurementSession` di `domain/session`. Nama kelas, fungsi, dan variabel Kotlin memakai bahasa Inggris.

Layar memakai Navigation 3 (`NavDisplay`, `NavKey`) saat fase 3 menambah tujuan. Versi ditambahkan ke `HealthTrack/gradle/libs.versions.toml` pada rilis yang cocok dengan Kotlin yang sudah terpin. AGP dan Kotlin yang ada tidak diturunkan. ViewModel memakai `StateFlow` dan konstruktor biasa.

Preferensi lokal: DataStore `healthtrack_prefs`. Profil dan hasil: Room, tabel `body` dan `measurement`, setara [Penyimpan](../../aplikasi/simpan.py). Prefs tidak menyimpan baris ukur.

## Yang dipakai bersama

- Peta byte: [protokol frame OKOK](../protokol-frame-okok.md).
- Definisi selesai: [definisi-selesai.md](../definisi-selesai.md).
- Bluetooth di aplikasi: `HealthTrack/.cursor/rules/bluetooth.mdc`.
- Operasi rumus: `Float` (IEEE-754 binary32), urutan sama dengan `rumus/*.py`.
- Angka pembanding layar: berat 68,7 kg, tinggi 166 cm, umur 29, kelamin 1, impedansi 600 ohm. Kelamin 0 pada vektor yang sama menghasilkan lemak 34,8. Pemetaan field ada di fase 2.
- Siaran `0xC0` dengan bit 7 pada byte offset 4 ditolak. Repositori tidak memuat kunci `okok_scale_encrypted_key_`.
- Sesi tidak menulis ke karakteristik TX.
- [`getVFR`](../../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) tidak dipindahkan. Viseral laporan v235 adalah field `vfl`. Pemanggilan `getVFR` di sumber ada pada skor umur, untuk jalur yang bukan frekuensi ganda:

```1386:1389:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java
        if (getType() == Type.DualFrequency || getType() == Type.MultiFrequency) {
            sbc = getSbc();
        } else {
            float scoreWithAge = getScoreWithAge(this.H, this.Wt, this.Sex, this.Age, getBFR(), getSLM(), getVFR());
```

## Risiko yang mengikat urutan

- Urutan float mengikuti Python. Uji membandingkan keluaran yang sudah tercatat, termasuk vektor 68,7 kg.
- Pemindaian dan `connectGatt` tidak berjalan bersamaan.
- Timbangan yang masih tersambung ke aplikasi OKOK menolak GATT. Layar sesi menyebut itu bila waktu sambungan habis.
- Frame GATT riwayat tidak menimpa berat sesi yang sedang berjalan.
- `cs_bias_vA019.py` memuat interpreter program (sekitar dua ribu baris). Itu fase 6, sesudah satu ohm terbukti di timbangan.
