# Hal yang perlu dipahami

Catatan ini menjelaskan apa yang sedang dihadapi dan bagaimana membacanya. Riwayat pekerjaan ada di `activity_log.md`.

## Aplikasi yang dibongkar

Sumbernya adalah aplikasi OKOK International, paket `com.chipsea.btcontrol.en`, versi **3.1.66** (versionCode 173), dikompilasi untuk Android SDK 36. Ini aplikasi timbangan kesehatan Chipsea, bukan proyek ScaleIoT sendiri.

Aplikasi ini mengurus lebih dari satu produk:

- Timbangan berat dan komposisi tubuh
- Timbangan dapur / nutrisi (`nutriscale`)
- Catatan minum air (`waterdrink`)
- Olahraga, laporan, widget, dan langganan VIP

Titik masuk proses adalah `com.chipsea.btcontrol.CSApplication`. Ikon launcher membuka `com.chipsea.shell.MainActivity`. Layar utama aplikasi ada di `com.chipsea.btcontrol.activity.MainActivity`. Keduanya berbeda dan jangan dicampur.

## Bentuk file sumber

`OKOK international.apk` bukan satu APK. Itu wadah split APK dengan header `MID`, berisi tiga berkas:

| Berkas | Peran |
|---|---|
| `base.apk` | Kode, manifest, resource umum, dan aset |
| `split_config.arm64_v8a.apk` | Library native khusus CPU ARM 64-bit |
| `split_config.xxhdpi.apk` | Gambar untuk kerapatan layar xxhdpi |

Hanya ABI `arm64-v8a` dan kerapatan `xxhdpi` yang ada di file ini. Perangkat dengan CPU atau kerapatan lain tidak terwakili di hasil bongkaran.

`unzip` langsung ke file induk gagal dibaca utuh karena setelah ZIP pertama masih ada split berikutnya. Tiap split harus dipotong dulu, baru diekstrak.

## Apa yang sudah terbaca, dan apa yang belum

Hasil di `ScaleHealtSource` adalah isi arsip, bukan kode sumber.

- `AndroidManifest.xml` di dalam `base` masih XML biner Android. Yang bisa dibaca manusia adalah `AndroidManifest.decoded.txt` dan `badging.txt`.
- `classes.dex` sampai `classes10.dex` masih bytecode. Belum ada Java atau Smali. `classes2.dex` jauh lebih kecil dari yang lain (sekitar 5 KB), jadi isinya hampir pasti bukan modul utama.
- Resource gambar, layout, dan string sebagian besar masih dalam bentuk resource Android (`resources.arsc` dan `res/`), belum berupa proyek yang bisa dibuka di Android Studio.
- Library `.so` ada di `split_config.arm64_v8a/lib/arm64-v8a/`, bukan di dalam folder `base`.

Folder `ScaleHealtSource` dan APK asli diabaikan Git lewat `.gitignore`.

## Di mana logika penting berada

Logika yang berkaitan langsung dengan timbangan sebagian besar ada di kode native, bukan di layout atau manifest.

| Library | Yang perlu diingat |
|---|---|
| `libprotocol.so` | Parser protokol Bluetooth timbangan. Ada jalur terpisah untuk lemak tubuh, tinggi, dapur, dan beberapa generasi parser BLE. |
| `libBodyFatScaleAlg.so` | Perhitungan komposisi tubuh. |
| `libchipsea_bias_v235.so` dan `libchipsea_bias_vA019.so` | Koreksi bias, masing-masing untuk keluarga perangkat yang berbeda. |
| `libdevice_auth.so` | Autentikasi perangkat. |
| `libpdfium*.so` | Pratinjau PDF, bukan protokol timbangan. |
| `libumeng-spy.so`, `libpglarmor.so`, `libnms.so` | SDK pihak ketiga (analitik, iklan, pelindung). Bukan inti produk timbangan. |

Artinya, membaca DEX saja tidak cukup untuk memahami cara timbangan berbicara dengan ponsel. Protokol dan rumus ada di `.so`. Sebaliknya, alur layar, akun, laporan, dan widget ada di bytecode DEX paket `com.chipsea.*`.

Di `assets/` ada animasi timbangan, font, HTML, dan tiga berkas `*_skin_pack_*.apk` (green, pink, purple). Berkas skin itu paket tampilan yang dibawa di dalam aplikasi, bukan APK utama dan bukan split CPU.

## Izin yang menjelaskan perilaku

Izin Bluetooth (`BLUETOOTH_SCAN`, `BLUETOOTH_CONNECT`, plus izin lama `BLUETOOTH`) menegaskan hubungan ke perangkat lewat BLE. Izin lokasi menyertai pemindaian Bluetooth di Android lama. Izin kamera dan media dipakai alur makanan (foto dan barcode). Izin billing dipakai alur VIP. Izin ini menggambarkan kemampuan aplikasi, bukan bukti bahwa setiap izin dipakai pada setiap layar.

## Urutan memahami yang masuk akal

1. Baca manifest yang sudah didekode untuk peta layar dan service, mulai dari paket `com.chipsea`.
2. Dekompilasi DEX bila perlu mengikuti alur Java: layar, akun, penyimpanan, dan pemanggilan native.
3. Telusuri `libprotocol.so` hanya untuk pertanyaan protokol timbangan, setelah tahu fungsi Java mana yang memanggilnya.
4. Perlakukan library iklan, analitik, dan PDF sebagai kode pendukung, supaya tidak tertukar dengan logika timbangan.

Sampai DEX didekompilasi, nama class di manifest adalah petunjuk, bukan bukti isi implementasinya.
