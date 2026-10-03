# Fase 6 — Frekuensi ganda

Syarat mulai: pintu keluar [fase 5](fase-05-hasil-riwayat.md).

Sumber perilaku: [cs_bias_vA019.py](../../rumus/cs_bias_vA019.py). Berkas ini memuat interpreter program (sekitar 2.000 baris). Ini bagian terbesar dari tahap timbangan. Jangan memecahnya menjadi modul Gradle lain, dan jangan menaruhnya di `data`.

## Yang dihasilkan

`com.mascill.healthtrack.domain.model.CsBiasVA019`, satu berkas di paket `model` yang sudah ada:

- `csBiasVA019`
- `parseMultiFrequency`
- interpreter yang menjalankan citra program di berkas Python

Pembantu float tetap yang di `domain/model` pada fase 2. Urutan operasi binary32 tidak diubah. Jangan membuat paket `domain/formula`.

`calculateReport` memilih `vA019` bila impedansi berisi sepuluh nilai. Satu nilai tetap `v235`. Jumlah lain tetap menolak sesi.

Laporan frekuensi ganda disimpan di kolom JSON `measurement.report` yang sudah ada. Tabel Room tidak ditambah untuk fase ini. Layar hasil yang sudah ada menampilkan field itu; tidak ada paket `presentation` baru.

Pembulatan sama: sebagian besar satu desimal, tulang dua desimal, metabolisme satu desimal. Daftar baris OKOK untuk sepuluh ohm menyusul bila ada sesi timbangan pembanding. Sampai sesi itu ada, pintu keluar fase ini adalah uji host, bukan layar baru.

## Langkah

1. Port interpreter dan rumus tanpa mengubah urutan float.
2. Salin `rumus/test_cs_bias_vA019.py` ke `app/src/test/java`: nilai sama dengan library, kode galat berurutan, regresi mode nol, laporan Java memotong float.
3. Pindahkan `test_sepuluh_impedansi` dari `aplikasi/test_sesi_ukur.py`. Sepuluh nilai contoh di uji itu: 500, 480, 30, 450, 460, 510, 490, 28, 440, 470 ohm (mentah 5000, 4800, 300, 4500, 4600, 5100, 4900, 280, 4400, 4700 dibagi 10). Nama rumus `vA019`, kode 0, data sama dengan `parseMultiFrequency` langsung.
4. `MeasurementSession` yang menerima sepuluh ohm lewat jalur itu menutup sesi hanya bila kode 0.

Uji tetap pada `./gradlew :app:testDebugUnitTest`.

## Pintu keluar

`./gradlew :app:testDebugUnitTest` lulus untuk uji `vA019` dan sepuluh impedansi. `MeasurementSession` memilih `vA019` bila impedansi berisi sepuluh nilai.

Fase ini menutup timbangan yang mengirim sepuluh ohm pada jalur rumus. Uji di timbangan sepuluh ohm dilakukan bila perangkat itu ada; ketiadaan perangkat itu tidak menahan pintu keluar host di atas.

## Belum dikerjakan

Modul di luar timbangan: dapur, minum, olahraga, wearable, tali, puasa, VIP, iklan, analitik, PDF, dan akun server Chipsea.
