# Frame timbangan OKOK

Peta ini dibaca dari parser Java di `ScaleHealtSource/jadx-protocol`. Angka multi-byte dibaca big-endian: byte pertama adalah byte tinggi (`BytesUtil.bytesToInt`).

Dua kelas yang memotong frame:

- Iklan BLE: `com.chipsea.btlib.protocal.chipseaBroadcastFrame`
- Data GATT setelah tersambung: `com.chipsea.btlib.protocal.chipseaStraightFrame`

Keduanya memakai header `0xCA` (`-54`), `0xC0` (`-64`), atau `0xFF` (`-1`). Parser GATT hanya menerima `0xCA`.

## Byte properti timbangan

`BytesUtil.byteToBit` menyusun bit dari bit 7 ke bit 0. Arti yang dipakai parser OKOK:

| Bit | Fungsi |
|---|---|
| bit 0 | Kunci pengukuran. `getCmdId` membaca bit ini. Nilai 1 berarti hasil sudah stabil. |
| bit 5 | Jenis perangkat pada siaran `0xC0`. `0` = timbangan berat (`deviceType` 0), selain itu = timbangan lemak (`deviceType` 2). |
| bit 4–3 | Satuan: `00` kg, `01` jin, `10` lb, `11` stone. |
| bit 2–1 | Digit standar OKOK: `01` bilangan utuh, `10` dibagi 100, selain itu dibagi 10. |
| bit 2–1 | Digit cloud biasa (arti berbeda): `01` utuh, `10` dibagi 10, selain itu dibagi 100. |
| bit 6–5 | Digit cloud V4: `01` utuh, `10` dibagi 10, selain itu dibagi 100. |

Berat dua byte masuk `WeightUnitUtil`. Hasil `kgWeight` sudah dikonversi ke kilogram. Stone tidak memakai bilangan utuh itu: tampilannya `byteTinggi:byteRendah/10`.

Pada frame GATT, nilai kilogram dikali 10 lalu `CsFatScale.setWeight` membagi 10 lagi, jadi yang tersimpan tetap kilogram. Pada frame siaran, `chipseaBroadcastFrame.weight` langsung menyimpan kilogram.

## Siaran `0xCA`

Byte kedua memilih parser.

### Versi bukan `0x20`

`okokParser`.

| Offset | Versi 16 | Versi 17 |
|---|---|---|
| 0 | `0xCA` | `0xCA` |
| 1 | versi | versi |
| 2 | panjang | panjang |
| 3 | `deviceType` | byte properti |
| 4 | byte properti | `deviceType` |

Jika `deviceType` bukan 0, berat ada di offset 5–6 dan product id 4 byte ada di offset 7–10. Parser ini berhenti di situ. Lemak dan impedansi tidak ada di jalur ini.

Jika `deviceType` 0 dan versi 16, berat adalah uint16 di offset 8–9 lalu dibagi 10. Satuan tidak dibaca.

Jika `deviceType` 0 dan versi 17, layout-nya sama dengan `deviceType` bukan 0: berat di 5–6, product id di 7–10.

### Versi `0x20`

`okokBroadcastParser`.

| Offset | Isi |
|---|---|
| 3–6 | product id, 4 byte |
| 7 | `0` berarti `deviceType` 0, selain itu 2 |
| 8 | byte properti |
| 9 | nomor urut, hanya jika bit kunci = 1 |
| 10–11 | berat |
| 12–13 | impedansi `r1`, uint16 dibagi 10 |

Jika bit kunci = 0, berat, nomor urut, dan impedansi diisi kosong.

## Siaran `0xC0`

`okokBroadcasetV2Parser`. Versi dipaksa 1 dan panjang dipaksa 9. Frame lebih pendek dari 9 byte diabaikan.

| Offset | Isi |
|---|---|
| 1 | nomor urut |
| 2–3 | berat |
| 4–5 | impedansi. Bit 7 byte 4 adalah tanda terenkripsi |
| 6–7 | product id, 2 byte |
| 8 | byte properti |
| 9–14 | hanya jika terenkripsi dan panjang minimal 15 |

Impedansi setelah dekripsi di-mask `0x7FFF` lalu dibagi 10.

Jika bit enkripsi menyala, berat dan impedansi didekripsi dengan kunci 4 byte. Kunci itu hex string dari `com.chipsea.code.util.OkokScaleEncryptedKeyUtils.getOkokScaleEncryptedKeySync(mac)`, dipanggil lewat refleksi. Kelas itu ada di `classes3.dex` dan `classes4.dex`, belum ada di `jadx-protocol`. Kalau kunci tidak ada, berat dan impedansi dipaksa 0.

MAC pada frame terenkripsi memakai bahan lain: 2 byte pertama dari offset 9 didekripsi dengan 4 byte sesudahnya, lalu 2 byte hasil itu digabung dengan 4 byte tersebut menjadi MAC.

Dekripsi menjaga bit 15, lalu pada 15 bit sisanya: XOR byte kunci 0, putar kiri 14 bit, XOR byte 1, putar kiri 12 bit, XOR byte 2, putar kiri 13 bit, XOR byte 3. Putaran dibatasi 15 bit.

## Siaran `0xFF`

`okokCloudParser`. `deviceType` dipaksa 1.

| Offset | Isi |
|---|---|
| 2 | versi |
| 3 | byte properti |
| 4–5 | berat, urutan byte dibalik terhadap parser lain |
| 6–9 | product id |

Product id khusus `0xFA 0xFB 0xFC 0xFD` diganti angka `997264800` dan properti dipaksa 4. Product id `1104000001` juga memaksa properti 4.

Versi 16 dan 17 memakai digit cloud V4. Versi lain memakai digit cloud biasa. Setelah berat terbaca, properti diubah ke bentuk standar lewat `changeCloudProperty2Standard`.

## GATT, versi 16

`chipseaStraightFrame`, satu paket. Offset 3 tidak dibaca.

| Offset | Isi |
|---|---|
| 0 | `0xCA` |
| 1 | 16 |
| 2 | panjang, tidak dipakai untuk memotong field |
| 4 | byte properti |
| 5–6 | berat |
| 7–8 | lemak |
| 9–10 | air |
| 11–12 | otot |
| 13–14 | BMR |
| 15–16 | lemak visceral |
| 17 | tulang, 1 byte |

Komposisi tubuh hanya diisi jika bit kunci pada byte properti = 1. Kalau tidak, yang terisi hanya berat.

## GATT, versi 17

Perintah ada di offset 3, bukan di byte properti.

| Perintah | Arti |
|---|---|
| 0 atau 1 | Berat langsung. Angka ini juga menjadi tanda kunci. Properti di offset 11, berat di offset 5–6. Tidak ada komposisi. |
| 18 | Pengukuran sekarang, beberapa paket, ada komposisi. |
| 19 | Riwayat, beberapa paket, ada waktu timbang. |
| 20 | Daftar pengguna yang cocok. |

Paket perintah 18, 19, dan 20: panjang muatan = byte panjang minus 2, muatan mulai di offset 5. Offset 4 adalah indeks paket. Nibble tinggi = nomor paket mulai dari 1. Nibble rendah = jumlah paket. Paket nomor 1 mengosongkan buffer. Rakitan selesai ketika nomor paket sama dengan jumlah paket dan isi buffer sama dengan jumlah itu.

Urutan rakitan perintah 18 dan 19:

| Offset | Isi |
|---|---|
| 0–3 | waktu Unix dalam detik. Hanya dipakai perintah 19 |
| 4 | byte properti |
| 5 | tidak dibaca |
| 6–9 | id peran, 4 byte |
| 10–11 | berat |
| 12–13 | lemak |
| 14–15 | air |
| 16–17 | otot |
| 18–19 | BMR |
| 20–21 | lemak visceral |
| 22 | tulang, 1 byte |

Sesudah itu otot dihitung ulang: `(otot / berat) * 100`. Jika hasilnya di bawah 50, angka itu disimpan sebagai persen. Jika 50 atau lebih, nilai otot yang sudah tersimpan dipakai dan dibatasi 50.

Rakitan perintah 20: offset 0–1 berat, offset 2 byte properti, lalu id peran 4 byte berulang. Hasilnya `CsFatConfirm`, bukan `CsFatScale`.

## Skala komposisi di `CsFatScale`

Nilai mentah dibagi 10, lalu dibatasi:

| Field | Batas yang lolos | Di luar batas |
|---|---|---|
| Lemak | 5 sampai 45 persen. `65535` langsung 0 | 0 |
| Air | 20 sampai 85, dan di bawah 100 | 0 |
| Otot | di bawah 100 | 0 |
| Lemak visceral | tidak di atas 59 dan di bawah 100 | 0. Nilai mentah tetap di `ori_visceral_fat` |
| Tulang | 1 sampai 4 | di bawah 1 menjadi 0, di atas 4 menjadi 4. `65535` menjadi 0 |
| BMR | `65535` menjadi 0. Jika mentah `5000` atau lebih, dibagi 10. Selain itu mentah disimpan utuh | — |

Di `CsBtUtil_v11`, data stabil dengan lemak di atas 0 menandai jenis perangkat: `ori_visceral_fat == 25600` menjadi tipe 2, selain itu tipe 1. Berat yang sampai ke listener dibuang jika `<= 0` atau `>= 6000` kilogram. Riwayat dibuang jika tanggalnya sebelum `2010-01-01` atau lebih dari 5 menit di depan jam ponsel.

## Perintah ponsel ke timbangan

`syncChipseaInstruction` menyusun frame `0xCA`. Checksum adalah XOR dari byte 1 sampai byte sebelum checksum. Header `0xCA` tidak ikut XOR. Sisa byte hingga panjang 20 diisi 0 pada perintah yang memakai buffer 20 byte.

| Perintah | Versi | Byte perintah | Isi |
|---|---|---|---|
| Ambil riwayat | 17 | 17 | panjang 2, byte indeks 1 |
| Pilih pengguna | 17 | 21 | panjang 5, id peran 4 byte |
| Kirim semua peran | 17 | 16 | waktu Unix, lalu tiap peran 8 byte: id, umur dengan bit 7 = jenis kelamin 1, tinggi, berat |
| Kirim satu peran, v10 | 16 | 1 | `yy MM dd HH mm ss`, id peran, jenis kelamin, umur, tinggi |

Peran jamak dipecah. Tiap paket memuat paling banyak 14 byte muatan, dengan nibble indeks yang sama seperti penerimaan.

## Checksum

`chipseaBroadcastFrame` dan `chipseaStraightFrame` tidak memeriksa XOR saat menerima.

Pemeriksaan XOR ada di `com.chipsea.btlib.model.Frame`, dan kelas itu hanya dipakai parser lama `CsBtUtil`. Syaratnya: header `0xCA`, byte panjang sama dengan panjang frame minus 4, dan checksum sama dengan `versi XOR panjang XOR xor(deviceType, perintah, muatan)`. Pada bentuk itu, offset 3 adalah device type dan offset 4 adalah perintah.

## Yang belum tertutup peta ini

Kunci siaran `0xC0` belum terbaca karena kelasnya di luar dekompilasi jalur protokol. Parser XS tetap di `libprotocol.so`.
