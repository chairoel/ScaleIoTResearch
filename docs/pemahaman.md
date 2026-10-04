# Hal yang perlu dipahami

Catatan ini menjelaskan apa yang sedang dihadapi dan bagaimana membacanya. Riwayat pekerjaan ada di `activity_log.md`.

Setiap judul bagian memuat waktu pencatatan dalam WIB, format `YYYY-MM-DD HH:mm WIB`. Bagian yang sudah tertulis tidak diubah. Fakta baru atau koreksi ditambah sebagai bagian baru di atas bagian lama. Jika dua bagian bentrok, waktu pencatatan yang lebih baru yang berlaku.

Catatan baru yang menyebut class, method, atau simbol lain dari kode hasil bongkaran menyertakan tautan berkas dan cuplikan. Catatan lama tidak diubah untuk itu. Lokasi berkas untuk nama yang sudah tertulis ada di catatan terbaru dan di `protokol-frame-okok.md`.

## 2026-10-04 22:05 WIB — MeasurementSession dipisah dari MeasurementContext

Koreksi catatan 2026-10-04 21:49. [`MeasurementSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) sekarang hanya berisi data publik untuk presentation layer. Detail internal BLE (`mac`, `productId`, `gattWeight`, `broadcastWeight`) dipindah ke [`MeasurementContext`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) yang membungkus `MeasurementSession`.

Use case (`AcceptTransmissionUseCase`, `AcceptGattUseCase`, `ApplyBroadcastWeightUseCase`, `CloseMeasurementUseCase`, `MeasurementStateUseCase`) menerima dan mengembalikan `MeasurementContext`. `ScaleFrames` menyimpan `context` dan menyediakan getter `session` untuk presentation. `MeasureScale` membangun `MeasurementContext` dan mengirim snapshot `session` ke status.

```6:34:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt
data class MeasurementSession(
    val body: BodyData,
    val transmission: ScaleTransmission? = null,
    val impedanceOhm: Double? = null,
    val code: Int? = null,
    val formula: String? = null,
    val result: MeasurementResult? = null,
    val storedId: Int? = null,
    val weightKg: Double? = null,
)

data class MeasurementContext(
    val session: MeasurementSession,
    val mac: String = "",
    val productId: Int = 0,
    val gattWeight: GattResult.ScaleGatt? = null,
    val broadcastWeight: ScaleTransmission? = null,
)
```

## 2026-10-04 21:49 WIB — Sesi ukur dikembalikan lewat copy

Koreksi catatan 2026-10-04 19:47 dan 2026-10-04 21:21. [`MeasurementSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) adalah `data class` yang semua propertinya `val`. `mac`, `productId`, `gattWeight`, dan `broadcastWeight` tetap `internal`. `weightKg` ikut salinan bersama `gattWeight` di [`AcceptGattUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/AcceptGattUseCase.kt), dari kilogram frame GATT terkunci yang bukan riwayat.

[`AcceptTransmissionUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/AcceptTransmissionUseCase.kt), `AcceptGattUseCase`, `ApplyBroadcastWeightUseCase`, dan `CloseMeasurementUseCase` mengembalikan sesi baru. Pemanggil menyimpan nilai kembali itu. [`ScaleFrames.session`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/ScaleFrames.kt) memegang sesi terbaru. [`MeasureScale`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/MeasureScale.kt) membaca sesi dari sana.

Status sesi keluar lewat `channelFlow`. Coroutine radio dan coroutine jam sama-sama memanggil `send`. Di kotlinx-coroutines 1.10, `ProducerScope` tidak menyediakan `emit`.

```13:25:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/AcceptTransmissionUseCase.kt
    suspend operator fun invoke(session: MeasurementSession, frame: ScaleTransmission): MeasurementSession {
        val kept = session.copy(transmission = frame)
        val ohms = frame.impedanceOhm
        if (kept.result == null && frame.locked && ohms != null) {
            return closeMeasurement(
                kept.copy(
                    impedanceOhm = ohms.toDouble(),
                    mac = frame.mac,
                    productId = frame.productId,
                ),
            )
        }
        return kept
    }
```

```44:46:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/MeasureScale.kt
    override fun invoke(body: BodyData): Flow<ScaleSessionStatus> = channelFlow {
        if (!radio.bluetoothEnabled()) {
            send(ScaleSessionStatus(bluetoothOff = true, heightCm = body.heightCm))
```

## 2026-10-04 21:21 WIB — weightKg sesi ada di konstruktor

Koreksi catatan 2026-10-04 19:47. [`MeasurementSession.weightKg`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) adalah properti konstruktor dan ikut `equals`, `hashCode`, serta `copy`. Nilainya diisi di [`AcceptGattUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/AcceptGattUseCase.kt) bersamaan dengan `gattWeight`, dari kilogram frame GATT terkunci yang bukan riwayat. Sebelum frame itu, `weightKg` tetap null.

## 2026-10-04 19:47 WIB — MeasurementSession adalah data class

[`MeasurementSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) adalah `data class`. Keadaan sesi ada di konstruktor, jadi `equals`, `hashCode`, dan `copy` membandingkan serta menyalinnya. `weightKg` dihitung dari `gattWeight` dan tidak ikut ketiga fungsi itu. Konstruktor data class tidak menerima `internal set`. `mac`, `productId`, `gattWeight`, dan `broadcastWeight` tetap `internal`. Properti lain punya setter publik. Use case tetap menulis properti pada objek yang sama.

## 2026-10-04 19:30 WIB — Varian radio dan GATT bersarang

Koreksi catatan 2026-10-04 17:08 pada byte domain. Di [`ScaleRadioEvent`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleRadioEvent.kt) variannya `Advertisement`, `Notification`, `NotifyReady`, `LinkLost`, `NotifyMissing`, `ConnectFailed`, dan `ScanFailed`. `Advertisement.payload` dan `Notification.value` bertipe `List<Byte>`. Parser [`ScaleTransmissionRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleTransmissionRepository.kt) dan [`ScaleGattRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleGattRepository.kt) tetap menerima `ByteArray`. [`MeasureScale`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/MeasureScale.kt) memanggil `toByteArray()` sebelum [`ScaleFrames`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/ScaleFrames.kt).

Di [`ScaleGatt.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleGatt.kt), `Confirmation` dan `ScaleGatt` adalah anggota `GattResult`. [`MeasurementSession.gattWeight`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) bertipe `GattResult.ScaleGatt`.

## 2026-10-04 19:24 WIB — Kesalahan parser tetap exception

Koreksi nama pada catatan 2026-09-29 16:40. [`ScaleProtocolError.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleProtocolError.kt) memuat exception, bukan satu tipe bernama `ScaleProtocolError`. `EncryptedTransmissionError` dan `UnsupportedGatt` adalah subtipe `FrameFormatError`. `IncompleteGatt` mewarisi `Exception` langsung. Hierarki ini tidak menjadi data class dan tidak menjadi sealed interface bernilai seperti [`BleScanEvent`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt). Pemanggil melempar dan menangkapnya. `catch (FrameFormatError)` di [`ScaleFrames.onAdvertisement`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/ScaleFrames.kt) harus tetap melewatkan `IncompleteGatt`.

```3:9:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleProtocolError.kt
open class FrameFormatError(message: String) : IllegalArgumentException(message)

class EncryptedTransmissionError(message: String) : FrameFormatError(message)

class UnsupportedGatt(message: String) : FrameFormatError(message)

class IncompleteGatt(message: String) : Exception(message)
```

```79:86:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/ScaleFrames.kt
        } catch (_: EncryptedTransmissionError) {
            attach(address)
            encrypted = true
            if (!encryptedAddresses.add(address.lowercase())) {
                return null
            }
            return "$address siaran terenkripsi"
        } catch (_: FrameFormatError) {
```

## 2026-10-04 18:38 WIB — Urutan tambah otot rangka v235 memakai dua +=

Koreksi bentuk kode pada catatan 2026-10-03 22:03. Di [`CsBiasV235.csBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/util/CsBiasV235.kt), otot rangka ditambah dua kali: dulu `muscleZ`, kemudian konstanta. Satu `muscle += muscleZ + kSmmConst` tetap menjumlahkan ruas kanan lebih dulu dan menggeser hasil satu ulp pada vektor `(0, 99, 220, 25000, 15000)`.

```355:357:HealthTrack/app/src/main/java/com/mascill/healthtrack/util/CsBiasV235.kt
        // Add muscleZ, then the constant, so each sum rounds on its own.
        muscle += muscleZ
        muscle += kSmmConst
```

## 2026-10-04 17:45 WIB — Project HealthTrack full suspend + Flow + injected Dispatcher

Seluruh rantai data di project HealthTrack sekarang menggunakan pattern `suspend` + injected `AppDispatcher`:

- **DAO** (Room): semua fungsi `suspend`. Room secara internal menjalankannya di executor-nya.
- **Repository interface** (domain): semua fungsi `suspend`. Tidak ada `runBlocking`.
- **Repository impl** (data): memakai `withContext(dispatcher.io)` bukan `runBlocking`.
- **Use case**: fungsi yang memanggil repository juga `suspend` (`CloseMeasurementUseCase`, `AcceptTransmissionUseCase`, `AcceptGattUseCase`, `ApplyBroadcastWeightUseCase`).
- **ScaleRadioRepository**: `awaitEvent()` imperatif dihapus, diganti `val events: Flow<ScaleRadioEvent>`.
- **ScaleRadioRepositoryImpl**: inject `AppDispatcher`, scope internal pakai `dispatcher.default` bukan hardcoded `Dispatchers.Unconfined`.
- **MeasureScale**: collect `radio.events` memakai `launch(dispatcher.default)` dalam `coroutineScope`.
- **ViewModel**: sudah pakai `viewModelScope.launch(dispatcher.io)`, tidak perlu ubah.
- **Satu-satunya tempat `Dispatchers.*`** di-reference langsung: `DispatcherModule` — single source of truth.

Referensi pattern: project obu-mikrotrans (`CommonDispatcher` + `CommonGlobalModule`).

## 2026-10-04 17:26 WIB — Tanda frame berulang ada di ScaleFrames

Koreksi catatan 2026-10-04 09:58. `BroadcastSign` dan `GattSign` adalah kelas privat di [`ScaleFrames`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/ScaleFrames.kt). Berkas `SessionSign.kt` dan `SessionListener` tidak ada. Hex siaran dan hex GATT dihitung di `ScaleFrames`, huruf kecil tanpa pemisah. [`ProtocolUtils.toHex`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/ProtocolUtils.kt) tetap ada di `data/util` untuk parser.

## 2026-10-04 17:19 WIB — fma tidak memanggil Math.fma

[`fma`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/util/BinaryFloat.kt) membulatkan `a * b + c` sekali lewat `BigDecimal`, lalu `toDouble()`. `Math.fma` baru ada di API 33 dan `minSdk` adalah 28, jadi pemanggilan itu tidak dipakai. Hasil untuk bilangan hingga sama dengan fused multiply-add. `f32` tetap `toFloat().toDouble()`.

## 2026-10-04 17:08 WIB — Byte peristiwa BLE adalah List

Koreksi catatan 2026-10-04 16:45. [`BleManufacturerBlock.remainder`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt), `BleScanEvent.Advertisement.record`, dan `BleConnectEvent.Notification.value` bertipe `List<Byte>`. `@Suppress("ArrayInDataClass")` tidak dipakai. `==` membandingkan isi byte. Parser di [`ScaleTransmissionRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleTransmissionRepository.kt) tetap menerima `ByteArray`. [`ScaleRadioRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleRadioRepositoryImpl.kt) memanggil `toByteArray()` sebelum parser. Radio menyalin buffer dengan `toList()` di [`BleDataSourceImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleDataSourceImpl.kt).

## 2026-10-04 16:45 WIB — Peringatan array data class ditekan

Koreksi catatan 2026-10-04 16:42. [`BleManufacturerBlock`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt), `BleScanEvent.Advertisement`, dan `BleConnectEvent.Notification` tidak menimpa `equals` atau `hashCode`. `@Suppress("ArrayInDataClass")` menekan peringatan IDE. `==` pada `ByteArray` kembali membandingkan referensi array. Sesi membaca isi byte lewat properti, bukan lewat `==`.

## 2026-10-04 16:42 WIB — equals peristiwa BLE membandingkan isi byte

Koreksi catatan 2026-10-04 16:16. `==` pada [`BleManufacturerBlock`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt), `BleScanEvent.Advertisement`, dan `BleConnectEvent.Notification` membandingkan isi `ByteArray` lewat `contentEquals`, bukan referensi array. `hashCode` memakai `contentHashCode`. Dua array `null` pada `record` dianggap sama.

## 2026-10-04 16:24 WIB — Blok pabrik BLE tipe sendiri

Koreksi letak pada catatan 2026-10-04 15:50. Blok pabrik bukan `BleScanEvent.Advertisement.ManufacturerBlock`. Tipenya [`BleManufacturerBlock`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt), `data class` di berkas yang sama. [`BleScanEvent.Advertisement`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt) menyimpan `List<BleManufacturerBlock>`.

## 2026-10-04 16:16 WIB — Iklan BLE adalah data class

[`BleScanEvent.Advertisement`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt), `ManufacturerBlock`, dan `BleConnectEvent.Notification` adalah `data class`. Sesi tidak membandingkan objek itu. `==` pada field `ByteArray` membandingkan referensi array, bukan isi byte. Isi byte dibaca lewat `remainder` dan `record` di [`ScaleRadioRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleRadioRepositoryImpl.kt).

## 2026-10-04 15:50 WIB — Varian peristiwa BLE bersarang

Koreksi nama pada catatan 2026-10-04 14:39. Di [`BleEvent.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt), hasil pindai adalah `BleScanEvent.Advertisement` dan kegagalan pemindai adalah `BleScanEvent.Failed`. Blok pabrik adalah `BleScanEvent.Advertisement.ManufacturerBlock`. Peristiwa GATT adalah anggota `BleConnectEvent`: `Notification`, `NotifyReady`, `LinkLost`, `NotifyMissing`, dan `Failed`. Tidak ada tipe tingkat atas `BleAdvertisement` atau `BleScanFailed`.

## 2026-10-04 14:39 WIB — Peristiwa radio ada di data/model

Koreksi letak pada catatan 2026-10-04 14:30. `BleAdvertisement`, `BleScanEvent`, `BleConnectEvent`, dan tipe turunannya ada di [`BleEvent.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/BleEvent.kt). [`BleDataSource`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleDataSource.kt) hanya antarmuka. `startScan` mengembalikan `Flow<BleScanEvent>`. `connect` mengembalikan `Flow<BleConnectEvent>`.

## 2026-10-04 14:30 WIB — Radio Bluetooth memakai Flow

[`BleDataSource.startScan`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleDataSource.kt) dan `connect` mengembalikan `Flow`. Null bila radio mati atau izin tidak ada. Satu hasil pindai adalah `BleAdvertisement`: semua blok pabrik plus rekam mentah. [`ScaleRadioRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleRadioRepositoryImpl.kt) memilih blok timbangan pertama, atau rekam mentah bila tidak ada yang cocok, lalu mengirim `ScaleRadioEvent`. Membatalkan flow menghentikan pindai atau GATT itu. `stopScan` tetap sinkron sebelum `connect`, supaya pemindaian dan `connectGatt` tidak jalan bersama. Pintu domain `ScaleRadioRepository` tidak berubah.

## 2026-10-04 11:05 WIB — Radio Bluetooth bernama BleDataSource

Koreksi nama pada catatan 2026-10-04 11:01. Kontrak radio adalah [`BleDataSource`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleDataSource.kt). Implementasinya [`BleDataSourceImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleDataSourceImpl.kt). [`DataSourceModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/DataSourceModule.kt) mengikat keduanya. [`ScaleRadioRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleRadioRepositoryImpl.kt) menyuntik `BleDataSource`.

## 2026-10-04 11:01 WIB — Radio Bluetooth satu antarmuka satu implementasi

Koreksi catatan 2026-10-04 10:56. `ScanSink` dan `ConnectSink` tidak ada. Hasil pindai dan peristiwa GATT adalah parameter fungsi pada [`BleSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleSession.kt). Satu implementasi: [`BleSessionImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleSessionImpl.kt). [`ScaleRadioRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleRadioRepositoryImpl.kt) mengirim lambda ke `startScan` dan `connect`.

## 2026-10-04 10:56 WIB — Satu antarmuka radio satu berkas

Koreksi letak pada catatan 2026-10-04 10:46. Paketnya `com.mascill.healthtrack.data.datasource`, bukan `data.datasource.ble`. [`BleSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleSession.kt), [`ScanSink`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/ScanSink.kt), dan [`ConnectSink`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/ConnectSink.kt) masing-masing satu berkas. [`BleSessionImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/BleSessionImpl.kt) tetap kelas platformnya.

## 2026-10-04 10:46 WIB — Radio Bluetooth dipisah kontrak dan implementasi

[`BleSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/ble/BleSession.kt) adalah antarmuka pindai dan GATT. [`BleSessionImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/ble/BleSessionImpl.kt) memegang `BluetoothLeScanner` dan `BluetoothGatt`. [`DataSourceModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/DataSourceModule.kt) mengikat implementasi itu ke antarmuka. [`ScaleRadioRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleRadioRepositoryImpl.kt) menyuntik `BleSession`.

## 2026-10-04 10:36 WIB — Use case sesi dipanggil dari domain

[`MeasureScaleUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/MeasureScaleUseCase.kt) dijalankan oleh ViewModel sesi. Implementasinya [`MeasureScale`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/MeasureScale.kt) memanggil `AcceptTransmissionUseCase`, `AcceptGattUseCase`, `ApplyBroadcastWeightUseCase`, dan `MeasurementStateUseCase`. [`ScaleFrames`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/ScaleFrames.kt) di paket yang sama menerapkan satu siaran atau frame GATT dan tidak mengimpor `android.*`.

[`ScaleRadioRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleRadioRepository.kt) adalah pintu radio. [`ScaleRadioRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleRadioRepositoryImpl.kt) memegang `BleSession`, memotong muatan iklan, dan mengembalikan [`ScaleRadioEvent`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleRadioEvent.kt). Kelas data itu tidak memanggil use case. Batas 15 detik, dua putaran, dan batas sesi 120 detik ada di `MeasureScale`.

## 2026-10-04 09:58 WIB — Hex byte ada di ProtocolUtils

[`ByteArray.toHex`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/ProtocolUtils.kt) ada di `data/util`, di bagian pembantu byte. Hasilnya huruf kecil tanpa pemisah. [`SessionListener`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/ble/SessionListener.kt) memakai fungsi itu untuk hex siaran dan hex GATT.

## 2026-10-04 09:58 WIB — Tanda frame berulang ada di data/model

[`BroadcastSign`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/SessionSign.kt) dan `GattSign` ada di `data/model/SessionSign.kt`. Keduanya `internal`. [`SessionListener`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/ble/SessionListener.kt) memakainya untuk mengabaikan siaran atau GATT yang sama dengan frame sebelumnya.

## 2026-10-04 09:50 WIB — Sesi Bluetooth ada di data/datasource/ble

Koreksi catatan 2026-10-04 09:15 pada letak paket. [`SessionListener`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/ble/SessionListener.kt) dan [`BleSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/ble/BleSession.kt) ada di `data/datasource/ble`, sejajar dengan `datasource/local`. [`ScaleSessionRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleSessionRepositoryImpl.kt) di `data/repository` tetap memegang `BleSession`. `SessionListener` tetap tidak mengimpor `android.*`.

## 2026-10-04 09:36 WIB — Rekomendasi berikut: uji tutup aplikasi pintu keluar fase 5

Langkah berikut: satu pengukuran, tutup aplikasi, buka lagi, buka baris yang sama dari riwayat. Tulang 2,77 dan metabolisme 1502,0 harus sama dengan saat sesi selesai bila yang tersimpan adalah vektor 68,7 kg. Syaratnya kode fase 5, yang sudah ada. Hex pada jalur riwayat tampil `tidak ada` karena bukan kolom `measurement`. Pintu keluar timbangan fase 4 tetap terbuka. Jangan mulai fase 6. Jangan mem-port `cs_bias_vA019`.

## 2026-10-04 09:36 WIB — Riwayat membuka hasil lewat ResultRoute

Baris di [`HistoryScreen`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/presentation/history/HistoryScreen.kt) mendorong [`ResultRoute`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/presentation/navigation/Routes.kt) hanya dengan `measurementId`. [`ResultViewModel`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/presentation/result/ResultViewModel.kt) membaca baris itu dari `MeasurementRepository.list` dan membulatkan lewat `DisplayMeasurementUseCase`. Angka tidak dihitung di Compose. Membuka rute ini tidak memulai `BleSession`.

Tinggi untuk BMI, bila argumen rute 0, adalah `BodyRepository.latest`. Tabel `measurement` tidak menyimpan tinggi. Tulang dan metabolisme datang dari JSON `report`, jadi tidak ikut berubah bila profil tubuh diganti sesudah sesi. Hex siaran dan hex GATT tetap hanya di argumen `ResultRoute` sesi yang baru selesai, bukan kolom tabel.

## 2026-10-04 09:15 WIB — Rekomendasi berikut: uji timbangan pintu keluar fase 4

Langkah berikut: ukur di timbangan yang sama dengan uji 27 Sep 2026. Profil banding itu tinggi 166 cm, umur 29, kelamin 1. Pada siaran tidak terenkripsi, berat dan daftar indeks di layar hasil harus cocok dengan aplikasi OKOK. Hex siaran dan hex GATT terakhir harus tampil di layar itu. Bila iklan tidak connectable, berat siaran terkunci tetap menghasilkan laporan. Syaratnya kode fase 4, yang sudah ada. Jangan mulai fase 5. Jangan mem-port `cs_bias_vA019`.

## 2026-10-04 09:15 WIB — Sesi Bluetooth ada di data/ble

[`SessionListener`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/ble/SessionListener.kt) tidak mengimpor `android.*`. Muatan iklan dan notify masuk lewat `ScaleTransmissionRepository` dan `ScaleGattRepository`, lalu ke `AcceptTransmissionUseCase`, `AcceptGattUseCase`, dan `ApplyBroadcastWeightUseCase`. [`BleSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/ble/BleSession.kt) memegang `BluetoothLeScanner` dan `BluetoothGatt`. `connectGatt` memakai `autoConnect` false. Pemindaian berhenti sebelum `connectGatt`, lalu hidup lagi setelah notify RX `0000fff1-0000-1000-8000-00805f9b34fb` aktif. Sesi tidak menulis TX `0000fff2-0000-1000-8000-00805f9b34fb`.

[`ScaleSessionRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleSessionRepository.kt) adalah antarmuka domain. [`ScaleSessionRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleSessionRepositoryImpl.kt) memegang `BleSession`. ViewModel sesi menyuntik antarmuka itu. Tiga percobaan sambungan, batas 15 detik, paling banyak dua putaran pindai. Sesi berakhir pada 120 detik atau saat hasil tersimpan. Alamat yang disimpan adalah MAC radio.

[`MeasurementSession.storedId`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) diisi dari nilai kembali `MeasurementRepository.save`. [`GattParser.reset`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/gatt/GattParser.kt) dipanggil di awal sesi. Izin runtime diminta di layar sesi: API 28–30 memakai `BLUETOOTH`, `BLUETOOTH_ADMIN`, dan `ACCESS_FINE_LOCATION`; API 31+ memakai `BLUETOOTH_SCAN` dengan `neverForLocation` dan `BLUETOOTH_CONNECT`. Layar tetap menyala selama mengukur. Foreground service tidak dipakai.

Layar hasil memakai `DisplayMeasurementUseCase`. Hex siaran dan hex GATT dibawa `ResultRoute`, bukan kolom tabel `measurement`. Riwayat belum membuka hasil lama.

## 2026-10-04 04:07 WIB — Rekomendasi berikut: fase 4 sesi Bluetooth

Langkah berikut: fase 4 di [fase-04-sesi-bluetooth.md](android-dev/fase-04-sesi-bluetooth.md). Tambah `BleSession` dan `SessionListener` di `data/ble`, serta `ScaleSessionRepository` di `domain/repository`. Layar sesi memakai use case dari [`UseCaseModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/di/UseCaseModule.kt) dan baru mengukur bila [`BodyRepository.latest`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/BodyRepository.kt) ada. Syaratnya pintu keluar fase 3, yang sudah terpenuhi. Jangan mem-port `cs_bias_vA019`. Jangan membuka hasil lama dari riwayat; itu fase 5.

## 2026-10-04 04:07 WIB — Profil dan hasil tersimpan di Room

Database `healthtrack.db` dibuat di [`DatabaseModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/DatabaseModule.kt). Tabelnya `body` dan `measurement`. Kolom `impedance_ohm` dan `report` adalah teks JSON. Nama field laporan sama dengan [`V235Report`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/V235Report.kt): `bfp`, `slm`, `slp`, `bwp`, `bmc`, `vfl`, `pp`, `smm`, `swt`, `mc`, `wc`, `fc`, `bmr`, `ma`, `sbc`. `created_at` adalah waktu UTC dalam ISO-8601.

[`BodyRepository.save`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/BodyRepository.kt) menyisipkan baris baru. `latest` membaca `id` terbesar. [`MeasurementRepository.save`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/MeasurementRepository.kt) tetap sinkron. `list` mengembalikan `id` menurun. [`BodyData`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/BodyData.kt) menolak jenis kelamin selain 0 dan 1 sebelum insert.

DataStore `healthtrack_prefs` tidak punya kunci wajib. Profil dan hasil tidak ditulis ke prefs.

Tab Navigation 3: `ProfileRoute`, `SessionRoute`, `HistoryRoute`. `ResultRoute` membawa `measurementId`; isi layar hasil masih placeholder. Composable tema tetap `HealthTrackTheme`, paketnya `presentation/theme`.

`SessionViewModel.onStartClick` tidak masuk keadaan mengukur bila `BodyRepository.latest` kosong. Bluetooth belum disambungkan.

## 2026-10-04 02:13 WIB — Use case disediakan UseCaseModule

Koreksi catatan 2026-10-03 22:08 pada cara inject use case. Tujuh use case di `domain/usecase` tidak memakai `@Inject`. [`UseCaseModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/di/UseCaseModule.kt) membuatnya dengan `@Provides`. `@Inject` pada kelas yang sama bentrok dengan provider itu.

`@BindsOptionalOf` untuk `MeasurementRepository` tetap di `data/di/RepositoryModule`. `provideCloseMeasurementUseCase` membuka optional itu. Kosong berarti `save` dilewati.

```46:53:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/di/UseCaseModule.kt
    @Provides
    fun provideCloseMeasurementUseCase(
        calculateReport: CalculateReportUseCase,
        repository: Optional<MeasurementRepository>,
    ): CloseMeasurementUseCase = CloseMeasurementUseCase(
        calculateReport = calculateReport,
        repository = repository.orElse(null),
    )
```

## 2026-10-04 02:03 WIB — Optional MeasurementRepository ada di data/di

Koreksi catatan 2026-10-03 22:08. `@BindsOptionalOf` untuk [`MeasurementRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/MeasurementRepository.kt) ada di [`RepositoryModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/RepositoryModule.kt). Paket `domain/di` tidak ada. Use case tetap memakai `@Inject`. `dagger.hilt` hanya di `data/di`.

```35:37:HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/RepositoryModule.kt
    @BindsOptionalOf
    abstract fun measurementRepository(): MeasurementRepository
}
```

## 2026-10-03 22:08 WIB — Use case domain di-inject dari domain/di

Tujuh use case di `domain/usecase` memakai konstruktor `@Inject`. [`DomainModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/di/DomainModule.kt) hanya menandai [`MeasurementRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/MeasurementRepository.kt) sebagai `@BindsOptionalOf`. Implementasi Room nanti diikat `@Binds` di `data/di/RepositoryModule` dan mengisi optional itu. Jangan menyediakan instance kedua.

[`CloseMeasurementUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/CloseMeasurementUseCase.kt) melewatkan `save` bila optional kosong. `MeasurementSession` dibuat per pengukuran lewat `BodyData`, bukan dari graf. Tipe di `domain/model` tidak di-inject. Binding `ScaleTransmissionRepository` dan `ScaleGattRepository` tetap di `data/di`. [`CsBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/util/CsBiasV235.kt) tetap `object` di `util` dan dipanggil langsung oleh `CalculateReportUseCase`.

```21:23:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/di/DomainModule.kt
    @BindsOptionalOf
    abstract fun measurementRepository(): MeasurementRepository
}
```

## 2026-10-03 22:03 WIB — Urutan tambah otot rangka v235

Di [`CsBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/util/CsBiasV235.kt), otot rangka ditambah dari kiri: otot, lalu `muscleZ`, lalu konstanta. Bentuk `muscle += muscleZ + kSmmConst` menjumlahkan `muscleZ` dan konstanta lebih dulu, dan menggeser hasil satu ulp pada vektor `(0, 99, 220, 25000, 15000)`.

```356:356:HealthTrack/app/src/main/java/com/mascill/healthtrack/util/CsBiasV235.kt
        muscle = muscle + muscleZ + kSmmConst
```

## 2026-10-03 21:57 WIB — Satu use case satu invoke

Satu kelas use case memuat satu fungsi publik, `invoke`. Fungsi lain di kelas itu privat. Use case boleh memanggil use case lain.

Keadaan ukur ada di [`MeasurementSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt). [`AcceptTransmissionUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/AcceptTransmissionUseCase.kt), `AcceptGattUseCase`, dan `ApplyBroadcastWeightUseCase` memanggil [`CloseMeasurementUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/CloseMeasurementUseCase.kt). Kelas itu memanggil `CalculateReportUseCase`. `MeasurementStateUseCase` hanya membaca keadaan.

```13:20:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/AcceptTransmissionUseCase.kt
    operator fun invoke(session: MeasurementSession, frame: ScaleTransmission): ScaleTransmission {
        session.transmission = frame
        val ohms = frame.impedanceOhm
        if (session.result == null && frame.locked && ohms != null) {
            session.impedanceOhm = ohms.toDouble()
            session.mac = frame.mac
            session.productId = frame.productId
            closeMeasurement(session)
```

## 2026-10-03 21:51 WIB — Rumus v235 ada di util

Koreksi catatan 2026-10-03 19:57. Paket `domain` tidak berisi rumus. [`CsBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/util/CsBiasV235.kt) ada di `com.mascill.healthtrack.util`, bersama `f32` dan `fma`. Tipe laporan tetap di `domain/model`. [`CalculateReportUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/CalculateReportUseCase.kt) memilih rumus itu. `CsBiasVA019` menyusul di `util`. Jangan membuat `domain/formula`.

```284:290:HealthTrack/app/src/main/java/com/mascill/healthtrack/util/CsBiasV235.kt
object CsBiasV235 {
    /**
     * Same inputs as the native call.
     * [weight100] is kilograms times 100. [impedance10] is ohms times 10.
     * Height, weight, and impedance are cut to 16 bits. Age and sex are cut to 8 bits.
     * Out of range, [BiasV235Result.data] is null and [BiasV235Result.code] is negative:
     * -2 weight, -3 height, -4 age, -5 sex, -6 impedance.
```

## 2026-10-03 19:57 WIB — Rumus v235 ada di domain/formula

Koreksi catatan 2026-10-03 19:55 pada letak rumus. [`CsBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/formula/CsBiasV235.kt) ada di `domain/formula`. Paket `model` tetap tipe. [`CalculateReportUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/CalculateReportUseCase.kt) di `domain/usecase` memilih rumus itu. `CsBiasVA019` menyusul di paket `formula` yang sama. `f32` dan `fma` tetap di `util`.

```286:294:HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/formula/CsBiasV235.kt
object CsBiasV235 {
    /**
     * Same inputs as the native call.
     * [weight100] is kilograms times 100. [impedance10] is ohms times 10.
     * Height, weight, and impedance are cut to 16 bits. Age and sex are cut to 8 bits.
     * Out of range, [BiasV235Result.data] is null and [BiasV235Result.code] is negative:
     * -2 weight, -3 height, -4 age, -5 sex, -6 impedance.
     */
    fun csBiasV235(
```

## 2026-10-03 19:55 WIB — Paket model hanya tipe

Koreksi catatan 2026-10-03 19:34 pada letak rumus dan pembulatan. Paket `domain/model` hanya tipe. [`CsBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/CsBiasV235.kt) dan [`DisplayMeasurementUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/DisplayMeasurementUseCase.kt) ada di `domain/usecase`.

Tipe yang tetap di `domain/model`: `BiasV235Data`, `BiasV235Result`, `V235Report`, `V235ReportResult`, dan `MeasurementDisplay`. `CsBiasVA019` menyusul di `domain/usecase`, satu berkas dengan `CsBiasV235`. Tipe laporannya tetap di `domain/model`. `f32` dan `fma` tetap di `util`, sesuai catatan 2026-10-03 19:51.

## 2026-10-03 19:51 WIB — f32 dan fma ada di util

Koreksi catatan 2026-10-03 19:34 dan 2026-10-03 18:48 pada letak pembantu float. [`f32`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/util/BinaryFloat.kt) dan `fma` ada di `com.mascill.healthtrack.util`. [`CsBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/CsBiasV235.kt) memakai keduanya dari sana. [`ProtocolUtils.f32`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/ProtocolUtils.kt) tetap milik parser di `data/util` dan tidak dipakai rumus laporan.

## 2026-10-03 19:34 WIB — Sesi dan pilih rumus ada di domain/usecase

Koreksi catatan 2026-10-03 18:39 dan 2026-10-03 18:48 pada letak mesin sesi. [`CalculateReportUseCase`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/CalculateReportUseCase.kt) dan [`MeasurementSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/usecase/MeasurementSession.kt) ada di `domain/usecase`. Sesi memakai `MeasurementRepository` untuk menyimpan hasil yang kodenya 0.

[`CsBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/CsBiasV235.kt), `BodyData`, `MeasurementResult`, `V235Report`, dan `MeasurementDisplay` tetap di `domain/model`. `BinaryFloat` tetap di sana. `MeasurementRepositoryImpl` belum ada. Implementasi itu nanti hanya `save` dan `list`. Rumus dan mesin sesi tidak pindah ke `data/repository`.

ViewModel profil dan riwayat tetap menerima antarmuka repository. Jangan menambah UseCase untuk simpan profil atau daftar riwayat. Folder `domain/formula` dan `domain/session` tetap tidak dibuat.

## 2026-10-03 18:48 WIB — Rekomendasi berikut: profil dan Room

Langkah berikut: fase 3 di [fase-03-profil-room.md](android-dev/fase-03-profil-room.md). Tambah Room, DataStore, Navigation 3, dan plugin serialization. Entitas `body` dan `measurement`, implementasi `BodyRepository` serta `MeasurementRepository.save` yang sudah ada, layar profil, sesi yang tidak mulai tanpa profil, dan riwayat kosong. Syaratnya pintu keluar fase 2, yang sudah terpenuhi. Jangan memindai Bluetooth, jangan menyambung GATT, dan jangan mem-port `cs_bias_vA019`.

## 2026-10-03 18:48 WIB — Rumus v235 dan mesin sesi ada di domain

[`CsBiasV235.csBiasV235`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/CsBiasV235.kt) dan `parseDefaultZ` ada di `domain/model`. Nilai library sebelum penyempitan bertipe `Double`. Operasi yang dipaksa binary32 memakai [`f32`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/BinaryFloat.kt), dan perkalian-tambah memakai `fma` di berkas yang sama. `parseDefaultZ` menyempitkan field ke `V235Report`. Viseral laporan adalah `vfl`.

[`MeasurementSession`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/MeasurementSession.kt) menerima `ScaleTransmission` dan `GattResult` yang sudah diurai. Sesi tidak memegang parser dan tidak membaca byte. Impedansi diambil dari siaran terkunci. Berat diambil dari `ScaleGatt` dengan `lockFlag == 1` dan `history == false`. `applyBroadcastWeight` menutup sesi dari siaran bila berat GATT belum ada. Hasil pertama dengan kode 0 disimpan lewat [`MeasurementRepository.save`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/MeasurementRepository.kt). Method itu mengembalikan id baris dan tidak `suspend`. Implementasi Room belum ada.

`calculateReport` untuk satu ohm memakai nama `v235`. Sepuluh ohm melempar `IllegalStateException` sampai `vA019`. Jumlah lain melempar `IllegalArgumentException`. Pembulatan layar ada di `V235Report.toDisplay`. Layar nanti memakai nilai itu dan tidak menghitung ulang.

## 2026-10-03 18:39 WIB — Rekomendasi berikut: rumus v235 di domain/model

Langkah berikut: port `cs_bias_v235` dan `MeasurementSession` ke paket `domain/model` yang sudah ada, dan antarmuka `MeasurementRepository` ke `domain/repository`. Syaratnya pintu keluar fase 1, yang sudah terpenuhi. Jangan membuat folder `domain/formula`, `domain/session`, atau `domain/usecase`. Jangan mulai Room, DataStore, Compose, Bluetooth, atau `vA019`. Daftar kerjanya ada di [fase-02-rumus-v235-mesin-sesi.md](android-dev/fase-02-rumus-v235-mesin-sesi.md).

## 2026-10-03 18:39 WIB — Domain HealthTrack hanya model dan repository

Koreksi catatan 2026-10-03 18:33 pada letak fase 2–6. Paket `domain` yang boleh dipakai hanya `model` dan `repository`, yang sudah ada di `HealthTrack/app/src/main/java/com/mascill/healthtrack/domain`.

Rumus `CsBiasV235` dan `CsBiasVA019`, `BodyData`, `MeasurementResult`, serta `MeasurementSession` masuk `domain/model`. Antarmuka `BodyRepository`, `MeasurementRepository`, dan `ScaleSessionRepository` masuk `domain/repository`. ViewModel menyuntik antarmuka itu. UseCase tidak dibuat. Folder `domain/formula`, `domain/session`, dan `domain/usecase` tidak dibuat.

## 2026-10-03 18:33 WIB — Rencana eksekusi ada di docs/android-dev

Letak paket yang dipakai saat menulis HealthTrack ada di [android-dev/00-rencana-besar.md](android-dev/00-rencana-besar.md). Bagian paket di [rencana aplikasi Android](rencana-aplikasi-android.md) yang menaruh parser di `domain/protocol` dan menyebut templat kosong tidak dipakai.

Fase 1 sudah di kode: pintu domain `ScaleTransmissionRepository` dan `ScaleGattRepository`, modul Hilt di `data/di`. Fase 2–6 menambah `domain/formula`, `domain/session`, `domain/usecase`, entitas Room `body` dan `measurement`, DataStore `healthtrack_prefs`, serta layar di `presentation/[feature]` dengan Navigation 3. Tabel Room tidak dinamai `tubuh` atau `ukur`. Enam fase ini tidak memasang supabase-kt, OkHttp, atau Retrofit. Antarmuka simpan hasil bernama `MeasurementRepository`, bukan `ResultStore`.

## 2026-10-03 16:01 WIB — RepositoryModule ada di data/di

Koreksi catatan 2026-10-01 01:59. [`RepositoryModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/RepositoryModule.kt) ada di paket `data.di`, bersama `DataModule` dan `ScaleFrameHeaders`. Modul itu mengikat `ScaleTransmissionRepository` dan `ScaleGattRepository` ke implementasi data, `@Singleton` pada `SingletonComponent`. Paket `com.mascill.healthtrack.di` tidak ada.

## 2026-10-01 01:59 WIB — scaleHeaders disediakan DataModule

Koreksi catatan 2026-10-01 01:47 dan 2026-10-01 01:49. Daftar header iklan disediakan [`DataModule.scaleHeaders`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/DataModule.kt): `TxConst.HEADER_CA` dan `TxConst.HEADER_C0`, ditandai `@ScaleFrameHeaders`. [`RepositoryModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/di/RepositoryModule.kt) hanya mengikat `ScaleTransmissionRepository` dan `ScaleGattRepository`.

## 2026-10-01 01:53 WIB — Parser sesi GATT ada di DataModule

[`DataModule.gattParser`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/DataModule.kt) menyediakan satu [`GattParser`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/gatt/GattParser.kt) untuk seluruh aplikasi. [`ScaleGattRepositoryImpl.parse`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt) memakai instance itu, jadi perintah terpecah 18, 19, dan 20 bisa selesai pada panggilan berikutnya. `parseGatt` tetap membuat `GattParser` baru untuk tiap frame. Kelas `GattParser` publik karena konstruktor repository dan penyedia Hilt menyebut tipenya.

## 2026-10-01 01:49 WIB — ScaleFrameHeaders ada di data/di

Koreksi catatan 2026-10-01 01:47. Anotasi [`ScaleFrameHeaders`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/di/ScaleFrameHeaders.kt) ada di paket `data.di`. [`ScaleTransmissionRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleTransmissionRepositoryImpl.kt) dan [`RepositoryModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/di/RepositoryModule.kt) mengimpor anotasi itu. Daftar header tetap disediakan `RepositoryModule.scaleHeaders`.

## 2026-10-01 01:47 WIB — Header iklan diisi Hilt

Koreksi catatan 2026-10-01 01:39 pada `scaleHeaders`. Daftar itu disediakan [`RepositoryModule.scaleHeaders`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/di/RepositoryModule.kt): `TxConst.HEADER_CA` dan `TxConst.HEADER_C0`. [`ScaleTransmissionRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleTransmissionRepositoryImpl.kt) menerimanya lewat konstruktor. Anotasi `ScaleFrameHeaders` di berkas yang sama menandai parameter itu. `Constants` tetap hanya menyimpan `LB_PER_KG`.

## 2026-10-01 01:39 WIB — Composition dan header iklan milik pemakainya

Koreksi catatan 2026-10-01 00:57. `Composition` ada lagi, sebagai kelas `private` di dalam [`GattMapper`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/GattMapper.kt). Kelas itu menampung angka komposisi yang sudah dijepit, hanya saat `RawGattMeasurement` menjadi `ScaleGatt`. `data/model` tidak memuat tipe itu. Model mentah komposisi tetap `RawBody`.

`scaleHeaders` adalah properti `private` pada [`ScaleTransmissionRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleTransmissionRepositoryImpl.kt). Isinya `TxConst.HEADER_CA` dan `TxConst.HEADER_C0`. [`Constants`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/Constants.kt) hanya menyimpan `LB_PER_KG`.

## 2026-10-01 01:09 WIB — Konversi berat ada di WeightMapper

Koreksi catatan 2026-09-29 17:58. Konversi berat tidak lagi di `data/util/Weight.kt`.

[`WeightMapper`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/WeightMapper.kt) memuat `unit`, `digitPlaces`, `unitNameFromCode`, `scaleText`, `weightKilograms`, dan `mapWeight`. `weightKilograms` memilih `NativeProtocol.nativeWeightKilograms` bila `libscale_protocol.so` termuat, dan rumus Kotlin bila tidak. `mapWeight` mengembalikan kilogram sebagai `Float` untuk transmission.

`ProtocolUtils` tetap di `data/util`: `u8`, `bytesToInt`, `bits`, `f32`, `roundHalfUp`, dan `javaFloatText`. `Constants.LB_PER_KG` tetap di sana dan dipakai `WeightMapper` untuk pon dan stone.

## 2026-10-01 00:57 WIB — Model domain dibangun di mapper

Koreksi catatan 2026-09-29 18:09, 2026-09-29 18:12, dan 2026-10-01 00:25. Pembaca frame tidak lagi membangun model domain.

[`parseCa`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/transmission/CaTransmission.kt), `parseC0`, dan `parseFf` mengembalikan [`RawTransmission`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/RawProtocolData.kt). `RawWeight` membedakan berat dari dua byte, bilangan dibagi sepuluh, berat kosong, dan teks timbangan kosong. `RawImpedance` membedakan impedansi yang tidak ada, nol, dan dibagi sepuluh. Layout `0xCA`, `0xC0`, dan `0xFF` tidak memakai satu rumus.

[`RawGattMeasurement`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/RawProtocolData.kt) membawa `RawBody` hanya bila frame punya blok komposisi. Perintah 0 dan 1 tidak punya blok itu. Versi 16 membacanya saat kunci aktif. Perintah 18 dan 19 selalu membacanya, lalu mapper menghitung ulang otot.

[`TransmissionMapper`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/TransmissionMapper.kt) dan [`GattMapper`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/GattMapper.kt) adalah satu-satunya pembangun `ScaleTransmission`, `ScaleGatt`, dan `GattConfirmation`. Penjepit komposisi ada di `GattMapper`. Pemetaan `DoubleArray` native ada di mapper yang sama. Pembaca native hanya memanggil JNI dan menolak kode kesalahan. `fromWeight`, `div10` di pembaca transmission, `cloudProperty` di `FfTransmission`, `GattComposition`, dan `data/model/Composition` tidak ada lagi.

[`ScaleTransmissionRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleTransmissionRepositoryImpl.kt) tetap memegang pembacaan iklan dan penolakan kode kesalahan native.

## 2026-10-01 00:31 WIB — Pembantu GATT satu berkas bersifat private

[`gattFromNative`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/gatt/GattNative.kt) dan `rolesFromNative` di berkas yang sama bersifat `private`. Hanya pembaca native di berkas itu yang memanggilnya. `nativeParseAssembled`, `nativeParseV16`, `nativeParseRoles`, dan `nativeParseV17Weight` tetap `internal` karena [`GattFrames`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/gatt/GattFrames.kt) memanggilnya. Fungsi komposisi, `need`, `javaByte`, `sliceInt`, `splitPack`, dan `concatPackets` tetap `internal` karena pemanggilnya ada di berkas lain pada paket yang sama.

## 2026-10-01 00:25 WIB — Pembantu transmission satu pemanggil bersifat private

Fungsi yang hanya dipanggil satu fungsi tidak `internal`. `cloudProperty` ada di [`FfTransmission.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/transmission/FfTransmission.kt) sebagai `private`, karena hanya `parseFf` yang memakai. Pembaca iklan Kotlin `scalePayloadKotlin` dan `transmissionFromNative` adalah method `private` pada [`ScaleTransmissionRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleTransmissionRepositoryImpl.kt). `need`, `lockBit`, `div10`, `frameInt`, dan `fromWeight` tetap `internal` karena lebih dari satu pembaca memakainya. `parseCa`, `parseC0`, dan `parseFf` tetap `internal` karena dispatcher-nya ada di berkas lain.

## 2026-10-01 00:13 WIB — Mask byte ada di ProtocolUtils

Mask dan geser byte di [`ProtocolUtils.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/ProtocolUtils.kt) bernama `LOW_BYTE`, `BYTE_SHIFT`, `BIT_COUNT`, `HIGH_BIT`, `LOW_BIT`, `BIT_MASK`, dan `INT_ABSENT`. `BYTE_SHIFT` dan `BIT_COUNT` sama-sama `8` dengan arti berbeda: geser satu byte, dan lebar bit dalam satu byte. Nama itu tinggal di berkas util byte. `TxConst.LOW_BYTE` dan `GattConst.LOW_BYTE` tetap milik layout frame.

## 2026-10-01 00:08 WIB — Angka nol transmission punya nama sendiri

Di [`TxConst`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/TxConst.kt), beberapa nilai `0` tidak digabung. `FLAG_OFF` adalah flag native yang mati. `NO_PROPERTY`, `NO_PRODUCT`, dan `NO_SEQ` adalah field yang layout itu tidak punya. `NO_WEIGHT` dan `NO_IMPEDANCE` adalah berat dan impedansi kosong. `AD_START` dan `AD_END` adalah awal pindai iklan dan panjang blok yang mengakhiri pindai. `BIT_CLEAR` dan `BIT_SET` adalah karakter bit pada string properti.

## 2026-10-01 00:04 WIB — Angka nol GATT punya tiga nama

Di [`GattConst`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/GattConst.kt), `FLAG_OFF`, `INT_ABSENT`, dan `EMPTY_LEN` sama-sama `0` dengan arti berbeda. `FLAG_OFF` adalah flag native yang mati. `INT_ABSENT` adalah irisan bilangan yang kosong atau tidak muat di 32 bit. `EMPTY_LEN` adalah panjang muatan kosong. Mereka tidak digabung karena artinya beda, sama seperti `ERR_OK` dan `CMD_UNLOCKED` yang juga `0`.

## 2026-09-30 23:59 WIB — Komposisi GATT yang ditolak bernama CLEARED

Nilai yang ditampilkan saat field komposisi kosong atau di luar rentang adalah [`GattConst.CLEARED`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/GattConst.kt), yaitu `0.0`. `GattConst.RAW_ABSENT` tetap `65535` pada nilai mentah, sebelum dibagi `GattConst.TENTHS`.

## 2026-09-30 23:50 WIB — Indeks DoubleArray native satu objek per berkas

[`TxIdx`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/TxIdx.kt), [`GIdx`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/GIdx.kt), dan [`RIdx`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/RIdx.kt) masing-masing satu berkas di `data/util`. Nama berkas sama dengan nama objek. Urutan angka tetap sama dengan urutan yang ditulis jembatan JNI.

## 2026-09-30 23:44 WIB — TxConst dan GattConst ada di data/util

[`TxConst`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/TxConst.kt) dan [`GattConst`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/GattConst.kt) ada di paket `data/util`. Keduanya tetap objek terpisah. Nama field bentrok, antara lain `HEADER`, `LOW_BYTE`, `TENTHS`, `VERSION_16`, dan `CMD_LOCKED`, jadi tidak digabung ke `Constants`. Pembaca transmission, pembaca GATT, `TransmissionMapper`, dan `GattMapper` mengimpor objek itu.

## 2026-09-30 23:44 WIB — Indeks DoubleArray native bernama NativeDoubleArrayIndex

`TxIdx`, `GIdx`, dan `RIdx` ada di [`NativeDoubleArrayIndex.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/NativeDoubleArrayIndex.kt). Mereka adalah posisi field di `DoubleArray` hasil `nativeParseTransmission`, parser GATT native, dan `nativeParseGattRoles`. Urutan angka tetap sama dengan urutan yang ditulis jembatan JNI.

## 2026-09-29 18:40 WIB — Layout GATT ada di GattConst

Angka perintah, offset, panjang, dan batas komposisi pembaca GATT ada di [`GattConst`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/gatt/GattConst.kt). Offset tidak digabung dengan [`TxConst`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/transmission/TxConst.kt). Versi 16, berat versi 17, badan perintah 18 dan 19, serta daftar peran perintah 20 menaruh field di indeks yang berbeda.

Perintah `0` dan `1` adalah berat langsung. `18` pengukuran sekarang, `19` riwayat, `20` daftar peran. Batas komposisi, termasuk `65535`, `5000`, dan tutup otot `50`, ada di objek yang sama. `GattMapper` memakai konstanta itu. Parser di `scale_protocol.c` masih menulis angka yang sama sebagai literal.

## 2026-09-29 18:36 WIB — Layout transmission ada di TxConst

Angka header, versi, offset, panjang, dan kode kesalahan pembaca transmission ada di [`TxConst`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/transmission/TxConst.kt). Offset tidak dijadikan satu daftar `BYTE_n` karena indeks yang sama adalah field berbeda pada `0xCA`, `0xC0`, dan `0xFF`. Panjang minimum dihitung dari offset field ditambah panjang field itu.

Kode kesalahan Kotlin sama dengan makro C:

```8:12:HealthTrack/app/src/main/cpp/scale_protocol.h
#define SP_OK           0
#define SP_ERR_EMPTY    1
#define SP_ERR_UNKNOWN  2
#define SP_ERR_SHORT    3
#define SP_ERR_ENCRYPTED 4
```

Parser di `scale_protocol.c` masih menulis angka itu sebagai literal. `Constants.LB_PER_KG` tetap faktor pon, bukan tempat layout frame.

## 2026-09-29 18:31 WIB — Nama kode frame siaran adalah Transmission

Koreksi catatan 2026-09-29 18:25. Tipe Kotlin tidak memakai kata Indonesia `Siaran`. Nama Inggrisnya `Transmission`.

`Broadcast` tetap dihindari karena bentrok dengan `android.content.BroadcastReceiver`. `Advertisement` tetap nama langkah lain: mengambil muatan dari rekaman pindai (`scalePayload`, `payloadFromManufacturer`). Frame `0xCA`, `0xC0`, dan `0xFF` dibaca `parseTransmission` pada [`ScaleTransmissionRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleTransmissionRepository.kt) dan mengembalikan [`ScaleTransmission`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleTransmission.kt).

Pembaca ada di paket `data/repository/transmission/`. Model mentah `RawTransmission`. Indeks `DoubleArray` native bernama `TxIdx`. Fungsi JNI-nya `nativeParseTransmission`. Struct C `sp_broadcast_t` dan `sp_parse_broadcast` tidak berubah.

```104:105:HealthTrack/app/src/main/cpp/scale_protocol_jni.c
Java_com_mascill_healthtrack_data_datasource_NativeProtocol_nativeParseTransmission(
        JNIEnv *env, jclass cls, jbyteArray frame) {
```

```35:35:HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/NativeProtocol.kt
    @JvmStatic external fun nativeParseTransmission(frame: ByteArray): DoubleArray
```

## 2026-09-29 18:25 WIB — Frame siaran tidak memakai nama Broadcast

Nama Kotlin untuk frame `0xCA`, `0xC0`, dan `0xFF` adalah siaran. Nama `Broadcast` bentrok dengan `android.content.BroadcastReceiver`. Iklan tetap terpisah: `scalePayload` dan `payloadFromManufacturer` pada [`ScaleSiaranRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleSiaranRepository.kt).

- Model domain [`ScaleSiaran`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleSiaran.kt). Pembacaan domain: `parseSiaran`.
- Kesalahan frame terenkripsi: `EncryptedSiaranError`.
- Pembaca ada di [`ScaleSiaranRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleSiaranRepositoryImpl.kt) dan paket `data/repository/siaran/`.
- Model mentah `RawSiaran`. Mapper [`SiaranMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/SiaranMapper.kt) tetap tidak dipanggil repository.
- Indeks `DoubleArray` native bernama `SrIdx`, menggantikan `BrIdx`.

Fungsi JNI yang dipanggil Kotlin adalah `nativeParseSiaran`. Simbol C `sp_broadcast_t` dan `sp_parse_broadcast` tetap. Build Android berikutnya harus memakai `.so` yang memuat simbol JNI baru:

```104:105:HealthTrack/app/src/main/cpp/scale_protocol_jni.c
Java_com_mascill_healthtrack_data_datasource_NativeProtocol_nativeParseSiaran(
        JNIEnv *env, jclass cls, jbyteArray frame) {
```

```35:35:HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/NativeProtocol.kt
    @JvmStatic external fun nativeParseSiaran(frame: ByteArray): DoubleArray
```

## 2026-09-29 18:20 WIB — Pembaca frame dipecah di dalam data/repository

[`ScaleBroadcastRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleBroadcastRepositoryImpl.kt) dan [`ScaleGattRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt) hanya memilih `NativeProtocol.isLoaded`. Pembaca Kotlin dan pemetaan `DoubleArray` ada di paket di bawahnya.

- `data/repository/broadcast/`: muatan iklan, `0xCA`, `0xC0`, `0xFF`, dan hasil native siaran.
- `data/repository/gatt/`: [`GattParser`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/gatt/GattParser.kt), frame versi 16 dan 17, komposisi, dan hasil native GATT.

`parse` tetap memegang satu `GattParser`. `parseGatt` membuat `GattParser` baru tiap panggilan. Antarmuka domain dan binding Hilt tidak berubah. `RawBroadcast`, `BroadcastMapper`, dan `GattMapper` tetap tidak dipanggil.

## 2026-09-29 18:12 WIB — Pembaca frame tidak pindah ke mapper, datasource, atau util

Pembaca header di kedua implementasi repository tidak masuk paket yang sudah ada.

- `data/datasource` hanya [`NativeProtocol`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/NativeProtocol.kt): muat `libscale_protocol.so` dan `external fun`. Nama kelas itu mengunci simbol JNI.
- `data/mapper` mengubah `RawBroadcast` dan model GATT mentah menjadi model domain. Repository tidak membangun model mentah itu.
- `data/util` sudah dipakai repository: `u8`, `bytesToInt`, `mapWeight`, `scaleText`, `BrIdx`, `GIdx`, `RIdx`.

`parseCa`, `parseC0`, `parseFf`, `parseV16`, dan `GattParser` membaca offset frame, menolak format, dan untuk GATT menyimpan buffer. Itu tetap di `data/repository`. `GattParser` tidak pindah karena buffer milik instance [`ScaleGattRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt).

## 2026-09-29 18:09 WIB — Parser frame ada di berkas repository, mapper tidak terpanggil

Kelas [`ScaleBroadcastRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleBroadcastRepositoryImpl.kt) dan [`ScaleGattRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt) pendek. Panjang berkasnya adalah fungsi privat di berkas yang sama: pembaca header, jalur Kotlin, dan pemetaan `DoubleArray` native ke model domain.

[`RawBroadcast`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/model/RawProtocolData.kt), [`BroadcastMapper`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/BroadcastMapper.kt), dan [`GattMapper`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/GattMapper.kt) tidak dipanggil repository. Jalur native sudah mengembalikan angka jadi. Melewatkannya lewat mapper menghitung ulang berat di Kotlin. Penyempitan komposisi di `GattMapper` menyalin rumus yang sama dengan fungsi privat di implementasi GATT.

Memecah berkas tetap di `data/repository`, antarmuka domain tidak bertambah. Pengelompokan mengikuti header di `docs/protokol-frame-okok.md`: `0xCA`, `0xC0`, `0xFF`, lalu GATT versi 16 dan 17. `GattParser` tetap milik instance repository.

## 2026-09-29 18:02 WIB — Hilt tidak dipecah per layer

Binding yang ada hanya [`RepositoryModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/di/RepositoryModule.kt): `ScaleBroadcastRepository` dan `ScaleGattRepository` ke implementasi data, `@Singleton` pada `SingletonComponent`. Domain tidak punya modul Hilt. Isinya antarmuka, model, dan kesalahan format. Modul di `domain/` menarik Hilt ke paket yang tidak mengimpor framework Android.

Data tidak punya modul terpisah. [`NativeProtocol`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/NativeProtocol.kt) adalah `object` JNI yang dimuat sekali. Mapper adalah extension tanpa konstruktor. Util adalah fungsi dan konstanta. `GattParser` privat di dalam [`ScaleGattRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt); `@Singleton` pada repository itu yang menjaga buffer `parse`. Memindahkan `@Module` ke `data/di` tetap mengikat komponen aplikasi yang sama.

Konstruktor kedua implementasi repository kosong. Tidak ada dependensi lain yang perlu `@Provides` atau `@Binds` sebelum Room, DataStore, dan ViewModel di fase 3.

## 2026-09-29 17:58 WIB — Konversi berat ada di data/util

Koreksi terhadap catatan 2026-09-29 17:12 dan 2026-09-29 16:56. Konversi berat tidak lagi di `data/mapper/WeightMapper.kt`.

- [`Weight.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/Weight.kt): `unit`, `digitPlaces`, `unitNameFromCode`, `scaleText`, `weightKilograms`, `mapWeight`. Satuan `lb` dan `st` memakai `Constants.LB_PER_KG`.
- [`ProtocolUtils.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/ProtocolUtils.kt): `bits`, bersama `u8` dan `bytesToInt`.

Paket `data/mapper` hanya memetakan model data ke domain: [`BroadcastMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/BroadcastMapper.kt) dan [`GattMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/GattMapper.kt). Penyempitan komposisi tubuh (`setAxunge`, `setWater`, `setMuscle`, dan sejenisnya) tetap privat di `GattMapper`.

## 2026-09-29 17:54 WIB — Jembatan JNI ada di data/datasource

Koreksi terhadap catatan 2026-09-29 17:45. [`NativeProtocol`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/datasource/NativeProtocol.kt) ada di `com.mascill.healthtrack.data.datasource`, bukan `data/protocol`. Paket `data/protocol` di sumber utama kosong. Uji parser tetap di paket `com.mascill.healthtrack.data.protocol`.

Nama fungsi di [`scale_protocol_jni.c`](../HealthTrack/app/src/main/cpp/scale_protocol_jni.c) mengikuti paket Kotlin itu. Awalan simbolnya `Java_com_mascill_healthtrack_data_datasource_NativeProtocol_`.

```6:6:HealthTrack/app/src/main/cpp/scale_protocol_jni.c
#define JNI_PKG Java_com_mascill_healthtrack_data_datasource_NativeProtocol_
```

## 2026-09-29 17:45 WIB — Parser frame ada di repository implementation

Koreksi terhadap catatan yang menaruh parser di `data/protocol`. Pembacaan iklan, berat, dan siaran ada di [`ScaleBroadcastRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleBroadcastRepositoryImpl.kt). Pembacaan GATT ada di [`ScaleGattRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt). `data/protocol` hanya menyisakan [`NativeProtocol`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/NativeProtocol.kt), jembatan JNI.

## 2026-09-29 17:43 WIB — GATT punya satu antarmuka repository

Koreksi terhadap catatan 2026-09-29 17:38. [`ScaleGattRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleGattRepository.kt) tidak lagi punya `GattFrameReader` atau `createGattReader`. Satu antarmuka itu memuat `parseGatt` dan `parse`. `parseGatt` mulai buffer baru tiap frame. `parse` menyimpan buffer pada instance [`ScaleGattRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt).

## 2026-09-29 17:38 WIB — Repository protocol terpisah: siaran dan GATT

Koreksi terhadap catatan 2026-09-29 17:16 dan 2026-09-29 17:21. Tidak ada lagi `ScaleProtocolRepository`. Pintu domain ada dua:

- [`ScaleBroadcastRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleBroadcastRepository.kt): `scalePayload`, `payloadFromManufacturer`, `parseBroadcast`. Implementasi [`ScaleBroadcastRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleBroadcastRepositoryImpl.kt).
- [`ScaleGattRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleGattRepository.kt): `parseGatt` dan `createGattReader`. Implementasi [`ScaleGattRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleGattRepositoryImpl.kt). `GattFrameReader` ada di berkas antarmuka GATT yang sama.

Keduanya diikat di [`RepositoryModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/di/RepositoryModule.kt) sebagai `@Singleton`.

## 2026-09-29 17:21 WIB — Hilt mengikat repository protocol

Koreksi terhadap catatan 2026-09-29 17:16 yang menyatakan Hilt belum dipakai. Aplikasi memakai [`App`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/App.kt) dengan `@HiltAndroidApp`. [`MainActivity`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/MainActivity.kt) memakai `@AndroidEntryPoint`.

[`RepositoryModule`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/di/RepositoryModule.kt) mengikat `ScaleProtocolRepository` ke `ScaleProtocolRepositoryImpl` sebagai `@Singleton`. Antarmuka domain tidak mengimpor Hilt. Versi: Hilt `2.60.1`, KSP `2.2.10-2.0.2`, sama dengan Kotlin `2.2.10`.

AGP 9 menolak `kotlin.sourceSets`. KSP `2.2.10-2.0.2` masih memakai DSL itu, jadi `HealthTrack/gradle.properties` memuat `android.disallowKotlinSourceSets=false`. supabase-kt, OkHttp, Retrofit, Room, dan DataStore belum dipasang.

## 2026-09-29 17:16 WIB — Pintu protocol adalah repository

Koreksi terhadap pohon paket di catatan lama yang menaruh parser di `domain/protocol`. Pemanggil di domain memakai [`ScaleProtocolRepository`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleProtocolRepository.kt). Implementasinya [`ScaleProtocolRepositoryImpl`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/repository/ScaleProtocolRepositoryImpl.kt) di data, dan dialah yang memanggil parser serta `GattParser`.

`parseGatt` pada repository selalu mulai buffer baru. Rakitan paket GATT yang terpecah memakai `createGattReader()`, yang mengembalikan [`GattFrameReader`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/repository/ScaleProtocolRepository.kt). Hilt belum dipakai. Repository profil, hasil ukur, dan Bluetooth belum dibuat; itu menyusul pada fase Room dan sesi Bluetooth.

## 2026-09-29 17:15 WIB — Indeks hasil JNI ada di data/util

Koreksi terhadap catatan 2026-09-29 16:40. `BrIdx`, `GIdx`, dan `RIdx` tidak lagi di `NativeProtocol.kt`. Ketiganya ada di [`NativeIndex.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/NativeIndex.kt). Mereka adalah posisi field di `DoubleArray` yang dikembalikan `nativeParseBroadcast`, parser GATT native, dan `nativeParseGattRoles`. Urutan angka harus tetap sama dengan urutan yang ditulis jembatan JNI. Mereka tidak digabung ke `Constants` karena nama field-nya bentrok (`ERROR`, `VERSION`, `PROPERTY`, `WEIGHT_KG`).

## 2026-09-29 17:12 WIB — Faktor pon ke kilogram ada di data/util

`Constants.LB_PER_KG` di [`Constants.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/util/Constants.kt) adalah faktor pon ke kilogram untuk mapper berat. Nilainya `0.4535924.toFloat().toDouble()`, jadi presisinya float32, bukan `Double` literal. [`WeightMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/WeightMapper.kt) memakai konstanta itu untuk satuan `lb` dan `st`.

## 2026-09-29 17:06 WIB — Mapper data ke domain memakai extension

Koreksi terhadap catatan 2026-09-29 16:56. `BroadcastMapper` dan `GattMapper` bukan `object`. Pemetaan ada sebagai extension pada model data:

- [`BroadcastMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/BroadcastMapper.kt): `RawBroadcast?.toScaleBroadcast()` dan `RawBroadcast?.toCloudScaleBroadcast()`.
- [`GattMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/GattMapper.kt): `RawGattMeasurement?.toScaleGatt()` dan `RawGattConfirmation?.toGattConfirmation()`.

Receiver nullable. Nilai kosong memakai `0`, `false`, string kosong, atau `orEmpty()`.

## 2026-09-29 16:56 WIB — Struktur paket data layer dengan mapper

Koreksi terhadap catatan 2026-09-29 16:40. Data layer sekarang dibagi dua paket dengan tanggung jawab terpisah:

**Data Mapper** (`com.mascill.healthtrack.data.mapper`):
- [`WeightMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/WeightMapper.kt): konversi berat (`weightKilograms`, `mapWeight`, `unit`, `digitPlaces`, `bits`, `scaleText`, `unitNameFromCode`).
- [`BroadcastMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/BroadcastMapper.kt): `BroadcastMapper` object dengan `mapToDomain()` dan `mapCloudToDomain()`.
- [`GattMapper.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/mapper/GattMapper.kt): `GattMapper` object dengan `mapMeasurementToDomain()`, `mapConfirmationToDomain()`, dan fungsi narrowing body composition.

**Data Protocol** (`com.mascill.healthtrack.data.protocol`):
- [`RawProtocolData.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/RawProtocolData.kt): data class intermediate (`RawBroadcast`, `RawGattMeasurement`, `RawGattConfirmation`, `RawGattResult`).
- [`ProtocolUtils.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/ProtocolUtils.kt): byte utilities (`u8`, `bytesToInt`, `f32`, `roundHalfUp`, `javaFloatText`).
- [`WeightParser.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/WeightParser.kt): `parseWeight` (delegasi ke mapper).
- [`BroadcastParser.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/BroadcastParser.kt): `parseBroadcast`.
- [`GattFrameParser.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/GattFrameParser.kt): `GattParser`, `parseGatt`.
- [`AdvertisementParser.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/AdvertisementParser.kt): `scalePayload`, `payloadFromManufacturer`.
- [`NativeProtocol.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/NativeProtocol.kt): JNI bridge.

Pemisahan ini mengikuti Clean Architecture: protocol menangani parsing bytes, mapper menangani transformasi ke domain model.

## 2026-09-29 16:40 WIB — Struktur paket parser protocol berubah

Koreksi terhadap catatan 2026-09-29 16:13 dan 2026-09-29 15:55. Parser protocol tidak lagi di `com.mascill.healthtrack.domain.protocol`. Sekarang dibagi dua paket:

**Domain model** (`com.mascill.healthtrack.domain.model`):
- [`ScaleBroadcast.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleBroadcast.kt): data class `ScaleBroadcast`.
- [`ScaleGatt.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleGatt.kt): `GattResult`, `GattConfirmation`, `ScaleGatt`.
- [`ScaleProtocolError.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/model/ScaleProtocolError.kt): `FrameFormatError`, `EncryptedBroadcastError`, `UnsupportedGatt`, `IncompleteGatt`.

**Data layer** (`com.mascill.healthtrack.data.protocol`):
- [`NativeProtocol.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/NativeProtocol.kt): JNI bridge + `BrIdx`, `GIdx`, `RIdx`.
- [`ProtocolUtils.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/ProtocolUtils.kt): `u8`, `bits`, `f32`, `roundHalfUp`, `scaleText`, `unitNameFromCode`, `bytesToInt`.
- [`WeightParser.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/WeightParser.kt): `weightKilograms`, `parseWeight`, `unit`, `digitPlaces`.
- [`BroadcastParser.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/BroadcastParser.kt): `parseBroadcast`.
- [`GattFrameParser.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/GattFrameParser.kt): `GattParser`, `parseGatt`.
- [`AdvertisementParser.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/data/protocol/AdvertisementParser.kt): `scalePayload`, `payloadFromManufacturer`.

Nama fungsi JNI di [`scale_protocol_jni.c`](../HealthTrack/app/src/main/cpp/scale_protocol_jni.c) berubah dari `domain_protocol` ke `data_protocol`.

## 2026-09-29 16:13 WIB — Parser protocol memakai C/C++ JNI

Operasi hex, bit manipulation, dan rumus aritmatika parser protocol sekarang diimplementasikan di C lewat JNI (`libscale_protocol.so`). Berkas:

- [`scale_protocol.h`](../HealthTrack/app/src/main/cpp/scale_protocol.h) dan [`scale_protocol.c`](../HealthTrack/app/src/main/cpp/scale_protocol.c): implementasi C murni. Semua `sp_*` functions: `sp_bytes_to_int`, `sp_weight_kilograms`, `sp_set_axunge`/`water`/`muscle`/`bmr`/`bone`, `sp_set_visceral`, `sp_recalculate_muscle`, `sp_parse_broadcast`, `sp_parse_gatt_v16`/`v17_weight`/`assembled`/`roles`, `sp_find_scale_payload`.
- [`scale_protocol_jni.c`](../HealthTrack/app/src/main/cpp/scale_protocol_jni.c): jembatan JNI yang mengonversi `jbyteArray` → `uint8_t*`, memanggil fungsi C, lalu mengemas hasil ke `DoubleArray`/`ByteArray`.
- [`NativeProtocol.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/protocol/NativeProtocol.kt): `System.loadLibrary("scale_protocol")`, flag `isLoaded`, deklarasi `external fun`, dan konstanta indeks (`BrIdx`, `GIdx`, `RIdx`).

Arsitektur dua jalur: di Android, `NativeProtocol.isLoaded` bernilai `true` dan fungsi publik memanggil native C. Di JUnit host (macOS/Linux), `.so` ARM tidak dimuat, `isLoaded` bernilai `false`, dan fallback Kotlin yang jalan. Kedua jalur menghasilkan output identik.

Formatting string (`scaleText`, `javaFloatText`) tetap di Kotlin karena bergantung `java.lang.Float.toString()`. `GattParser` (state management buffer paket) tetap di Kotlin; yang dipanggil native hanya parsing stateless per frame.

NDK yang dipakai: `28.0.12433566` (beta1). Versi `28.0.13004108` terpasang tapi tanpa `source.properties`.

## 2026-09-29 16:13 WIB — Rekomendasi berikut: rumus v235 dan mesin sesi

Langkah berikut: port `cs_bias_v235` dan `parse_default_z` ke `com.mascill.healthtrack.domain.formula.CsBiasV235`, lalu mesin `MeasurementSession` untuk satu nilai ohm. Rumus itu juga kandidat untuk diimplementasikan di C dalam `libscale_protocol.so`, terutama koefisien dan aritmatika `bia_calc`. Syaratnya pintu keluar fase 1, yang sudah terpenuhi. Jangan mulai Room, DataStore, Compose, Bluetooth, atau `vA019`. Daftar kerjanya ada di [fase-02-rumus-v235-mesin-sesi.md](android-dev/fase-02-rumus-v235-mesin-sesi.md).

## 2026-09-29 15:55 WIB — Parser HealthTrack tanpa nama OKOK

Koreksi terhadap catatan 2026-09-29 15:31. Parser di `com.mascill.healthtrack.domain.protocol` tidak memakai nama OKOK. [`ScaleAdvertisement.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/protocol/ScaleAdvertisement.kt) memuat `scalePayload` dan `payloadFromManufacturer`. [`ScaleBroadcast.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/protocol/ScaleBroadcast.kt) memuat `ScaleBroadcast`, `parseBroadcast`, `parseWeight`, dan `weightKilograms`. [`ScaleGatt.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/protocol/ScaleGatt.kt) memuat `ScaleGatt`, `GattConfirmation`, `GattResult`, `UnsupportedGatt`, `IncompleteGatt`, `GattParser`, dan `parseGatt`. Kode Python di `rumus/` dan `aplikasi/` tetap memakai nama berkas yang sudah ada.

## 2026-09-29 15:31 WIB — Rekomendasi berikut: rumus v235 dan mesin sesi

Langkah berikut: port `cs_bias_v235` dan `parse_default_z` ke `com.mascill.healthtrack.domain.formula.CsBiasV235`, lalu mesin `MeasurementSession` untuk satu nilai ohm, masih di modul Gradle `app`. Nama kelas, fungsi, dan variabel Kotlin memakai bahasa Inggris. Syaratnya pintu keluar fase 1, yang sudah terpenuhi lewat `./gradlew :app:testDebugUnitTest`. Jangan mulai Room, DataStore, Compose, Bluetooth, atau `vA019`. Daftar kerjanya ada di [fase-02-rumus-v235-mesin-sesi.md](android-dev/fase-02-rumus-v235-mesin-sesi.md).

## 2026-09-29 15:31 WIB — Nama Kotlin HealthTrack berbahasa Inggris

Parser OKOK ada di paket `com.mascill.healthtrack.domain.protocol`. [`OkokAdvertisement.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/protocol/OkokAdvertisement.kt) memuat `okokPayload` dan `payloadFromManufacturer`. [`OkokBroadcast.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/protocol/OkokBroadcast.kt) memuat `OkokBroadcast`, `parseBroadcast`, `parseWeight`, dan `weightKilograms`. [`OkokGatt.kt`](../HealthTrack/app/src/main/java/com/mascill/healthtrack/domain/protocol/OkokGatt.kt) memuat `OkokGatt`, `GattConfirmation`, `GattResult`, `UnsupportedGatt`, `IncompleteGatt`, `GattParser`, dan `parseGatt`. Paket itu tidak mengimpor `android.*`.

Koreksi terhadap catatan 2026-09-29 10:34 dan 2026-09-28 10:15. Paket rumus yang akan ditulis adalah `domain.formula`. Paket sesi adalah `domain.session`, dengan `BodyData`, `MeasurementSession`, `MeasurementResult`, `ResultStore.saveResult`, `calculateReport`, dan `applyBroadcastWeight`. Bluetooth yang akan ditulis adalah `SessionListener` dan `BleSession`. Tabel Room adalah `body` dan `measurement`. Kode Python di `rumus/` dan `aplikasi/` tetap memakai nama yang sudah ada.

## 2026-09-29 10:34 WIB — Rekomendasi berikut: rumus v235 dan mesin sesi

Langkah berikut: port `cs_bias_v235` dan `parse_default_z` ke `com.mascill.healthtrack.domain.rumus.CsBiasV235`, lalu mesin `SesiUkur` untuk satu nilai ohm, masih di modul Gradle `app`. Syaratnya pintu keluar fase 1, yang sudah terpenuhi lewat `./gradlew :app:testDebugUnitTest`. Jangan mulai Room, DataStore, Compose, Bluetooth, atau `vA019`. Daftar kerjanya ada di [fase-02-rumus-v235-mesin-sesi.md](android-dev/fase-02-rumus-v235-mesin-sesi.md).

## 2026-09-29 10:34 WIB — Parser OKOK di paket domain

Parser iklan, siaran, dan GATT ada di modul `app`, paket `com.mascill.healthtrack.domain.protokol`: `IklanOkok.kt`, `SiaranOkok.kt`, `GattOkok.kt`. Paket itu tidak mengimpor `android.*`. `settings.gradle.kts` tetap hanya `include(":app")`.

`SiaranOkok.weightKg` dan `impedanceOhm` bertipe `Float`. Itu hasil operasi yang di `rumus/siaran_okok.py` lewat `_f32`, termasuk pembulatan akhir yang lalu disimpan sebagai `Float`. Berat dan angka komposisi di `GattOkok` serta `GattKonfirmasi` bertipe `Double`, sama dengan pembagian Python pada `_stored_weight` dan penyempitan komposisi. `EncryptedBroadcastError` adalah subclass `FrameFormatError`. Siaran `0xC0` ditolak bila bit 7 pada byte offset 4 menyala.

`compileSdk` modul `app` adalah rilis `37.0` (`android-37.0`). `androidx.core:core-ktx:1.19.0` menolak kompilasi terhadap `android-36.1`. `minSdk` tetap 28 dan `targetSdk` tetap 36.

## 2026-09-28 17:48 WIB — Rekomendasi berikut: parser di dalam modul app

Langkah berikut: tulis parser iklan, siaran, dan GATT di paket `com.mascill.healthtrack.domain.protokol` pada modul Gradle `app` yang sudah ada. Uji JUnit host lewat `./gradlew :app:testDebugUnitTest`, dari vektor Python. Jangan membuat modul Gradle kedua. Jangan mulai profil, Bluetooth, rumus, atau modul produk lain sebelum pintu keluar fase 1 terpenuhi. Daftar kerjanya ada di [fase-01-modul-inti-parser.md](android-dev/fase-01-modul-inti-parser.md).

## 2026-09-28 17:47 WIB — HealthTrack satu modul app

Koreksi terhadap catatan 2026-09-28 09:12. Parser, rumus, dan mesin sesi tidak punya modul Gradle sendiri. Semuanya di dalam `app`, paket `domain`, dan tidak mengimpor `android.*`. Uji tanpa emulator tetap di `app/src/test`. Rencana yang berlaku ada di [rencana aplikasi Android](rencana-aplikasi-android.md) dan [android-dev/00-rencana-besar.md](android-dev/00-rencana-besar.md).

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
