# Frame timbangan OKOK

Peta ini dibaca dari parser Java di `ScaleHealtSource/jadx-protocol`. Angka multi-byte dibaca big-endian: byte pertama adalah byte tinggi. Itu terjadi di [`BytesUtil.bytesToInt`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java), yang mengurai hex string seluruh array.

```75:80:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
public static int bytesToInt(byte[] bArr) {
    try {
        return Integer.parseInt(bytesToHexString(bArr), 16);
    } catch (NumberFormatException unused) {
        return 0;
    }
}
```

Dua kelas yang memotong frame:

- Iklan BLE: [`chipseaBroadcastFrame`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java)
- Data GATT setelah tersambung: [`chipseaStraightFrame`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java)

Keduanya memakai header `0xCA` (`-54`), `0xC0` (`-64`), atau `0xFF` (`-1`). Parser GATT hanya menerima `0xCA`.

Pemilihan parser siaran ada di konstruktor [`chipseaBroadcastFrame(byte[], String)`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java):

```240:258:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
byte b = bArr[0];
if (b == -54) {
    if (bArr[1] == 32) {
        okokBroadcastParser(bArr, str);
        return;
    } else {
        okokParser(bArr, str);
        return;
    }
}
if (b == -1) {
    okokCloudParser(bArr, str);
} else {
    if (b == -64) {
        okokBroadcasetV2Parser(bArr, str);
        return;
    }
    throw new FrameFormatIllegalException("帧格式错误 -- 帧头错误");
}
```

GATT menolak header selain `0xCA` di [`chipseaStraightFrame.process`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java):

```66:70:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
if (bArr[0] != -54) {
    throw new FrameFormatIllegalException("帧格式错误 -- 不是正确的帧头");
}
byte b = bArr[1];
byte b2 = bArr[2];
```

## Byte properti timbangan

[`BytesUtil.byteToBit`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) menyusun bit dari bit 7 ke bit 0. Indeks 0 pada string itu adalah bit 7.

```134:136:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
public static String byteToBit(byte b) {
    return "" + ((int) ((byte) ((b >> 7) & 1))) + ((int) ((byte) ((b >> 6) & 1))) + ((int) ((byte) ((b >> 5) & 1))) + ((int) ((byte) ((b >> 4) & 1))) + ((int) ((byte) ((b >> 3) & 1))) + ((int) ((byte) ((b >> 2) & 1))) + ((int) ((byte) ((b >> 1) & 1))) + ((int) ((byte) (b & 1)));
}
```

Arti yang dipakai parser OKOK:

| Bit | Fungsi | Kode |
|---|---|---|
| bit 0 | Kunci pengukuran. Nilai 1 berarti hasil sudah stabil. | [`getCmdId`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) memakai `substring(7, 8)` |
| bit 5 | Jenis perangkat pada siaran `0xC0`. `0` = timbangan berat (`deviceType` 0), selain itu = timbangan lemak (`deviceType` 2). | [`getDeviceTpe4BV2`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) memakai `substring(2, 3)` |
| bit 4–3 | Satuan: `00` kg, `01` jin, `10` lb, `11` stone. | [`getUnit`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) memakai `substring(3, 5)` |
| bit 2–1 | Digit standar OKOK: `01` bilangan utuh, `10` dibagi 100, selain itu dibagi 10. | [`getDigit`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) memakai `substring(5, 7)` |
| bit 2–1 | Digit cloud biasa (arti berbeda): `01` utuh, `10` dibagi 10, selain itu dibagi 100. | [`getCloudDigit`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) |
| bit 6–5 | Digit cloud V4: `01` utuh, `10` dibagi 10, selain itu dibagi 100. | [`getCloudV4Digit`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) memakai `substring(1, 3)` |

```189:191:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
public static byte getCmdId(byte b) {
    return Byte.parseByte(byteToBit(b).substring(7, 8));
}
```

Berat dua byte masuk [`WeightUnitUtil`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/WeightUnitUtil.java). Hasil `kgWeight` sudah dikonversi ke kilogram. Stone tidak memakai bilangan utuh itu: tampilannya `byteTinggi:byteRendah/10`.

Pada frame GATT, nilai kilogram dikali 10 lalu [`CsFatScale.setWeight`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java) membagi 10 lagi, jadi yang tersimpan tetap kilogram. Pada frame siaran, `chipseaBroadcastFrame.weight` langsung menyimpan kilogram.

```148:150:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java
public void setWeight(double d) {
    this.weight = d / 10.0d;
}
```

## Siaran `0xCA`

Byte kedua memilih parser. Cabangnya ada di konstruktor di atas: versi `32` (`0x20`) memanggil `okokBroadcastParser`, versi lain memanggil `okokParser`.

### Versi bukan `0x20`

[`okokParser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java).

| Offset | Versi 16 | Versi 17 |
|---|---|---|
| 0 | `0xCA` | `0xCA` |
| 1 | versi | versi |
| 2 | panjang | panjang |
| 3 | `deviceType` | byte properti |
| 4 | byte properti | `deviceType` |

```54:89:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
    private void okokParser(byte[] bArr, String str) {
        this.mac = str;
        byte b = bArr[1];
        this.version = b;
        this.dataLength = bArr[2];
        if (b == 16) {
            this.deviceType = bArr[3];
            byte b2 = bArr[4];
            this.cmdId = b2;
            this.scaleProperty = b2;
        } else if (b == 17) {
            this.scaleProperty = bArr[3];
            this.deviceType = bArr[4];
        }
        if (this.deviceType != 0) {
            BytesUtil.subBytes(bArr, 5, 2);
            this.cmdId = BytesUtil.getCmdId(this.scaleProperty);
            WeightParserReturn weightParserReturnParser = WeightUnitUtil.Parser(bArr[5], bArr[6], this.scaleProperty, false);
            this.weight = weightParserReturnParser.kgWeight;
            this.scaleWeight = weightParserReturnParser.scaleWeight;
            this.productId = BytesUtil.bytesToInt(BytesUtil.subBytes(bArr, 7, 4));
            return;
        }
        if (b == 16) {
            this.weight = BytesUtil.bytesToInt(BytesUtil.subBytes(bArr, 8, 2)) / 10.0f;
            return;
        }
        if (b != 17) {
            return;
        }
        this.cmdId = BytesUtil.getCmdId(this.scaleProperty);
        WeightParserReturn weightParserReturnParser2 = WeightUnitUtil.Parser(bArr[5], bArr[6], this.scaleProperty, false);
        this.weight = weightParserReturnParser2.kgWeight;
        this.scaleWeight = weightParserReturnParser2.scaleWeight;
        this.productId = BytesUtil.bytesToInt(BytesUtil.subBytes(bArr, 7, 4));
    }
```

Jika `deviceType` bukan 0, berat ada di offset 5–6 dan product id 4 byte ada di offset 7–10. Parser ini berhenti di situ. Lemak dan impedansi tidak ada di jalur ini.

Jika `deviceType` 0 dan versi 16, berat adalah uint16 di offset 8–9 lalu dibagi 10. Satuan tidak dibaca.

Jika `deviceType` 0 dan versi 17, layout-nya sama dengan `deviceType` bukan 0: berat di 5–6, product id di 7–10.

### Versi `0x20`

[`okokBroadcastParser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java).

| Offset | Isi |
|---|---|
| 3–6 | product id, 4 byte |
| 7 | `0` berarti `deviceType` 0, selain itu 2 |
| 8 | byte properti |
| 9 | nomor urut, hanya jika bit kunci = 1 |
| 10–11 | berat |
| 12–13 | impedansi `r1`, uint16 dibagi 10 |

```95:116:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        this.productId = BytesUtil.bytesToInt(BytesUtil.subBytes(bArr, 3, 4));
        if (bArr[7] == 0) {
            this.deviceType = (byte) 0;
        } else {
            this.deviceType = (byte) 2;
        }
        byte b = bArr[8];
        this.scaleProperty = b;
        byte cmdId = BytesUtil.getCmdId(b);
        this.cmdId = cmdId;
        if (cmdId > 0) {
            this.measureSeqNo = bArr[9] & DataType.EXTEND;
            WeightParserReturn weightParserReturnParser = WeightUnitUtil.Parser(bArr[10], bArr[11], this.scaleProperty, false);
            this.weight = weightParserReturnParser.kgWeight;
            this.scaleWeight = weightParserReturnParser.scaleWeight;
            this.r1 = BytesUtil.bytesToInt(BytesUtil.subBytes(bArr, 12, 2)) / 10.0f;
            return;
        }
        this.measureSeqNo = 0;
        this.weight = 0.0d;
        this.scaleWeight = "";
        this.r1 = 0.0f;
```

Jika bit kunci = 0, berat, nomor urut, dan impedansi diisi kosong.

## Siaran `0xC0`

[`okokBroadcasetV2Parser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java). Versi dipaksa 1 dan panjang dipaksa 9. Frame lebih pendek dari 9 byte diabaikan.

| Offset | Isi |
|---|---|
| 1 | nomor urut |
| 2–3 | berat |
| 4–5 | impedansi. Bit 7 byte 4 adalah tanda terenkripsi |
| 6–7 | product id, 2 byte |
| 8 | byte properti |
| 9–14 | hanya jika terenkripsi dan panjang minimal 15 |

```124:130:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        this.version = (byte) 1;
        this.dataLength = (byte) 9;
        if (bArr.length < 9) {
            return;
        }
        boolean z = (bArr[4] & (-128)) == -128;
        LogUtil.i(TAG, "okokBroadcasetV2Parser encrypted : " + z);
```

Impedansi setelah dekripsi di-mask `0x7FFF` lalu dibagi 10.

```172:183:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        byte[] bArrSubBytes2 = BytesUtil.subBytes(bArr, 4, 2);
        LogUtil.i(TAG, "bTmp : " + BytesUtil.bytesToHexString(bArrSubBytes2));
        if (z) {
            int iOkokBroadcasetV2ParserDecrypt3 = okokBroadcasetV2ParserDecrypt(BytesUtil.bytesToInt(bArrSubBytes2), bytesFromHexStr) & 32767;
            if (bytesFromHexStr == null) {
                iOkokBroadcasetV2ParserDecrypt3 = 0;
            }
            bArrSubBytes2[0] = (byte) ((iOkokBroadcasetV2ParserDecrypt3 >> 8) & 255);
            bArrSubBytes2[c] = (byte) (iOkokBroadcasetV2ParserDecrypt3 & 255);
            LogUtil.i(TAG, "decryptedR : " + iOkokBroadcasetV2ParserDecrypt3);
        }
        this.r1 = BytesUtil.bytesToInt(bArrSubBytes2) / 10.0f;
```

Jika bit enkripsi menyala, berat dan impedansi didekripsi dengan kunci 4 byte. Kunci itu hex string dari [`OkokScaleEncryptedKeyUtils.getOkokScaleEncryptedKeySync`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java), dipanggil lewat refleksi di [`ScaleEncryptedKeyUtils.getScaleEncryptedKey`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/ScaleEncryptedKeyUtils.java). Definisi kelas ada di [`classes4.dex`](../ScaleHealtSource/base/classes4.dex). [`classes3.dex`](../ScaleHealtSource/base/classes3.dex) hanya memuat pemanggilnya. Kalau kunci tidak ada, berat dan impedansi dipaksa 0.

Method itu tidak menghitung kunci. Ia membaca SharedPreferences bernama `chipsea`, entri `okok_scale_encrypted_key_` ditambah MAC.

```41:45:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
    public static String getOkokScaleEncryptedKeySync(String str) {
        Context contexts = MyAplication.getContexts();
        if (contexts != null && !TextUtils.isEmpty(str)) {
            try {
                return PrefsUtil.getInstance(contexts.getApplicationContext()).getOkokScaleEncryptedKey(str);
```

```62:62:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/PrefsUtil.java
    public static final String SP_NAME = "chipsea";
```

```1680:1684:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/PrefsUtil.java
    public String getOkokScaleEncryptedKey(String str) {
        if (TextUtils.isEmpty(str)) {
            return null;
        }
        return getValue("okok_scale_encrypted_key_" + str, (String) null);
```

Kunci diisi saat ikat perangkat, hanya jika `ScaleInfo.isEncrypted()`, dari [`BoundDeviceActivity.toBindCloud`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java). Bind tetap dilanjutkan walaupun pengambilan kunci gagal.

```551:560:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java
        ScaleInfo scaleInfo = this.mScaleInfo;
        if (scaleInfo != null && scaleInfo.isEncrypted()) {
            ThreadUtil.executeThread(new Runnable() { // from class: com.chipsea.btcontrol.activity.setting.BoundDeviceActivity$$ExternalSyntheticLambda5
                @Override // java.lang.Runnable
                public final void run() {
                    this.f$0.lambda$toBindCloud$6(runnable);
                }
            });
        } else {
            runnable.run();
```

```592:593:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btcontrol/activity/setting/BoundDeviceActivity.java
    public /* synthetic */ void lambda$toBindCloud$6(final Runnable runnable) {
        com.chipsea.btlib.util.LogUtil.i(TAG, "encryptedKeyGetSuccess : " + OkokScaleEncryptedKeyUtils.getOkokScaleEncryptedKeyFromServerSync(this.mScaleInfo.getMac()));
```

Permintaan itu GET ke `HttpsEngine.WEB_IP` ditambah [`Api.SCALE_ENCRYPTED_KEY_GET`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/Api.java) ditambah MAC tanpa titik dua dan huruf kecil. Pada build rilis, host-nya `https://intl.chips-cloud.com/v3`. Yang disimpan adalah `toString()` dari [`JsonCommonInfo.getData`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/mode/json/JsonCommonInfo.java), di bawah MAC asli yang dikembalikan `getMac()` pada cuplikan di atas (titik dua tidak dihapus). `ApiCallFailInfo` tidak disimpan. `data` null atau string kosong dianggap sukses, tetapi tidak menulis prefs.

```13:32:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
    public static boolean getOkokScaleEncryptedKeyFromServerSync(String str) {
        if (TextUtils.isEmpty(str)) {
            return false;
        }
        Context contexts = MyAplication.getContexts();
        Object scaleEncryptedKey = new ApiImpl(contexts.getApplicationContext()).getScaleEncryptedKey(str.replace(":", "").toLowerCase(Locale.ENGLISH));
        LogUtil.i(TAG, "getScaleEncryptedKey : " + scaleEncryptedKey);
        if (scaleEncryptedKey instanceof ApiImpl.ApiCallFailInfo) {
            return false;
        }
        if (scaleEncryptedKey == null) {
            return true;
        }
        String string = scaleEncryptedKey.toString();
        if (TextUtils.isEmpty(string)) {
            return true;
        }
        try {
            LogUtil.i(TAG, "getScaleEncryptedKey keyFromServer : " + string);
            PrefsUtil.getInstance(contexts.getApplicationContext()).setOkokScaleEncryptedKey(str, string);
```

```155:155:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/Api.java
    public static final String SCALE_ENCRYPTED_KEY_GET = "/device/scale/sn?mac=";
```

```1177:1178:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/ApiImpl.java
    public Object getScaleEncryptedKey(String str) {
        return get(Api.SCALE_ENCRYPTED_KEY_GET + str, null, Api.METHOD_GET);
```

```1207:1211:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/business/ApiImpl.java
    private Object get(String str, Type type, String str2) throws Throwable {
        LogUtil.i("get", "action : " + str);
        JsonCommonInfo handle = this.httpsEngine.getHandle(str, str2);
        if (handle != null && handle.getCode() == 200) {
            return handle.getData();
```

```25:26:ScaleHealtSource/jadx-protocol/sources/com/chipsea/mode/json/JsonCommonInfo.java
    public Object getData() {
        return this.data;
```

```55:62:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/engine/HttpsEngine.java
    static {
        if (MyAplication.isDebug()) {
            WEB_IP = "http://172.31.10.160/v3";
            IS_HTTPS = false;
        } else {
            IS_HTTPS = true;
            WEB_IP = "https://intl.chips-cloud.com/v3";
        }
```

```1265:1266:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/engine/HttpsEngine.java
                LogUtil.i(str, "recive: " + stringBuffer.toString());
                JsonCommonInfo jsonCommonInfo = (JsonCommonInfo) new Gson().fromJson(stringBuffer.toString(), JsonCommonInfo.class);
```

MAC yang dipakai parser untuk membaca kunci, pada frame terenkripsi, huruf besar dan bertitik dua. Itu hasil [`BytesUtil.bytesToMac`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java). String prefs harus sama persis dengan `chipseaBroadcastFrame.mac`.

```270:271:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
        String string = sb.toString();
        return !TextUtils.isEmpty(string) ? string.toUpperCase(Locale.ENGLISH) : string;
```

```10:16:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/ScaleEncryptedKeyUtils.java
    public static String getScaleEncryptedKey(String str) {
        try {
            Object objInvoke = Class.forName("com.chipsea.code.util.OkokScaleEncryptedKeyUtils").getDeclaredMethod("getOkokScaleEncryptedKeySync", String.class).invoke(null, str);
            if (objInvoke instanceof String) {
                return (String) objInvoke;
            }
            return null;
```

Pemanggilan dari parser, plus cabang kunci kosong:

```149:164:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
        byte[] bytesFromHexStr = null;
        if (z) {
            String scaleEncryptedKey = ScaleEncryptedKeyUtils.getScaleEncryptedKey(this.mac);
            bytesFromHexStr = TextUtils.isEmpty(scaleEncryptedKey) ? null : BytesUtil.getBytesFromHexStr(scaleEncryptedKey);
            LogUtil.i(TAG, "okokBroadcasetV2Parser encryptedKey : " + BytesUtil.bytesToHexString(bytesFromHexStr));
        }
        this.measureSeqNo = bArr[c] & DataType.EXTEND;
        byte[] bArr2 = new byte[2];
        bArr2[0] = bArr[2];
        bArr2[c] = bArr[c2];
        LogUtil.i(TAG, "weightBytes : " + BytesUtil.bytesToHexString(bArr2));
        if (z) {
            int iOkokBroadcasetV2ParserDecrypt2 = okokBroadcasetV2ParserDecrypt(BytesUtil.bytesToInt(bArr2), bytesFromHexStr);
            if (bytesFromHexStr == null) {
                iOkokBroadcasetV2ParserDecrypt2 = 0;
            }
```

MAC pada frame terenkripsi memakai bahan lain: 2 byte pertama dari offset 9 didekripsi dengan 4 byte sesudahnya, lalu 2 byte hasil itu digabung dengan 4 byte tersebut menjadi MAC.

```135:141:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
            byte[] bArrSubBytes = BytesUtil.subBytes(bArr, 9, 6);
            int iBytesToInt = BytesUtil.bytesToInt(new byte[]{bArrSubBytes[0], bArrSubBytes[1]});
            c2 = 3;
            int iOkokBroadcasetV2ParserDecrypt = okokBroadcasetV2ParserDecrypt(iBytesToInt, new byte[]{bArrSubBytes[2], bArrSubBytes[3], bArrSubBytes[4], bArrSubBytes[5]});
            LogUtil.i(TAG, "mac54 : " + iOkokBroadcasetV2ParserDecrypt + " encryptedMac : " + iBytesToInt);
            c = (char) 1;
            this.mac = BytesUtil.bytesToMac(new byte[]{(byte) ((iOkokBroadcasetV2ParserDecrypt >> 8) & 255), (byte) (iOkokBroadcasetV2ParserDecrypt & 255), bArrSubBytes[2], bArrSubBytes[3], bArrSubBytes[4], bArrSubBytes[5]});
```

Dekripsi menjaga bit 15, lalu pada 15 bit sisanya: XOR byte kunci 0, putar kiri 14 bit, XOR byte 1, putar kiri 12 bit, XOR byte 2, putar kiri 13 bit, XOR byte 3. Putaran dibatasi 15 bit.

```192:203:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
    public static int okokBroadcasetV2ParserDecrypt(int i, byte[] bArr) {
        if (bArr == null || bArr.length < 4) {
            return 0;
        }
        int i2 = (i >> 15) & 1;
        int i3 = bArr[3] & DataType.EXTEND;
        int i4 = bArr[2] & DataType.EXTEND;
        int i5 = bArr[1] & DataType.EXTEND;
        int i6 = ((i & 32767) ^ (bArr[0] & DataType.EXTEND)) & 32767;
        int i7 = (((((i6 << 14) & 32767) | (i6 >> 1)) & 32767) ^ i5) & 32767;
        int i8 = (((((i7 << 12) & 32767) | (i7 >> 3)) & 32767) ^ i4) & 32767;
        return ((((((i8 << 13) & 32767) | (i8 >> 2)) & 32767) ^ i3) & 32767) | (i2 << 15);
    }
```

## Siaran `0xFF`

[`okokCloudParser`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java). `deviceType` dipaksa 1.

| Offset | Isi |
|---|---|
| 2 | versi |
| 3 | byte properti |
| 4–5 | berat, urutan byte dibalik terhadap parser lain |
| 6–9 | product id |

```206:232:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java
    private void okokCloudParser(byte[] bArr, String str) {
        WeightParserReturn weightParserReturnParser;
        this.mac = str;
        this.deviceType = (byte) 1;
        this.version = bArr[2];
        this.scaleProperty = bArr[3];
        this.cmdId = (byte) 0;
        byte[] bArrSubBytes = BytesUtil.subBytes(bArr, 6, 4);
        if (bArrSubBytes[0] == -6 && bArrSubBytes[1] == -5 && bArrSubBytes[2] == -4 && bArrSubBytes[3] == -3) {
            this.productId = 997264800;
            this.scaleProperty = (byte) 4;
        } else {
            int iBytesToInt = BytesUtil.bytesToInt(bArrSubBytes);
            this.productId = iBytesToInt;
            if (iBytesToInt == 1104000001) {
                this.scaleProperty = (byte) 4;
            }
        }
        byte b = bArr[2];
        if (b == 16 || b == 17) {
            weightParserReturnParser = WeightUnitUtil.Parser(bArr[5], bArr[4], this.scaleProperty);
        } else {
            weightParserReturnParser = WeightUnitUtil.Parser(bArr[5], bArr[4], this.scaleProperty, true);
        }
        this.weight = weightParserReturnParser.kgWeight;
        this.scaleWeight = weightParserReturnParser.scaleWeight;
        this.scaleProperty = BytesUtil.changeCloudProperty2Standard(this.scaleProperty);
    }
```

Product id khusus `0xFA 0xFB 0xFC 0xFD` (byte bertanda `-6, -5, -4, -3`) diganti angka `997264800` dan properti dipaksa 4. Product id `1104000001` juga memaksa properti 4.

Versi 16 dan 17 memakai digit cloud V4. Versi lain memakai digit cloud biasa. Setelah berat terbaca, properti diubah ke bentuk standar lewat [`changeCloudProperty2Standard`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java).

## GATT, versi 16

[`chipseaStraightFrame.process`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java), satu paket. Offset 3 tidak dibaca.

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

```71:96:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
        if (b == 16) {
            byte b3 = bArr[4];
            BytesUtil.subBytes(bArr, 5, 2);
            byte[] bArrSubBytes = BytesUtil.subBytes(bArr, 7, 2);
            byte[] bArrSubBytes2 = BytesUtil.subBytes(bArr, 9, 2);
            byte[] bArrSubBytes3 = BytesUtil.subBytes(bArr, 11, 2);
            byte[] bArrSubBytes4 = BytesUtil.subBytes(bArr, 13, 2);
            byte[] bArrSubBytes5 = BytesUtil.subBytes(bArr, 15, 2);
            byte[] bArrSubBytes6 = BytesUtil.subBytes(bArr, 17, 1);
            CsFatScale csFatScale = new CsFatScale();
            this.fatScale = csFatScale;
            csFatScale.setHistoryData(false);
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
                this.fatScale.setBmr(BytesUtil.bytesToInt(bArrSubBytes4));
                this.fatScale.setVisceral_fat(BytesUtil.bytesToInt(bArrSubBytes5));
                this.fatScale.setBone(BytesUtil.bytesToInt(bArrSubBytes6));
            }
```

Komposisi tubuh hanya diisi jika bit kunci pada byte properti = 1. Kalau tidak, yang terisi hanya berat.

## GATT, versi 17

Perintah ada di offset 3, bukan di byte properti. Cabang perintah ada di `process` yang sama, mulai baris 99.

| Perintah | Arti | Kode |
|---|---|---|
| 0 atau 1 | Berat langsung. Angka ini juga menjadi tanda kunci. Properti di offset 11, berat di offset 5–6. Tidak ada komposisi. | `bArr[3] == 0 \|\| bArr[3] == 1` |
| 18 | Pengukuran sekarang, beberapa paket, ada komposisi. | `case 18` |
| 19 | Riwayat, beberapa paket, ada waktu timbang. | `case 19` |
| 20 | Daftar pengguna yang cocok. Hasilnya [`CsFatConfirm`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatConfirm.java), bukan `CsFatScale`. | `case 20` |

```99:111:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
        if (b == 17) {
            byte b4 = bArr[3];
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
                return enumProcessResult.Received_Scale_Data;
```

Paket perintah 18, 19, dan 20: panjang muatan = byte panjang minus 2, muatan mulai di offset 5. Offset 4 adalah indeks paket. Nibble tinggi = nomor paket mulai dari 1. Nibble rendah = jumlah paket. Itu di [`splitPackInfo`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java) dan [`packageProcess`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java). Geser itu memakai byte bertanda. Nibble 8 sampai 15 menjadi negatif, jadi jumlah paket 8 atau lebih tidak lolos pemeriksaan ukuran buffer. Paket nomor 1 mengosongkan buffer. Rakitan selesai ketika nomor paket sama dengan jumlah paket dan isi buffer sama dengan jumlah itu. Parser perintah 18 dan 19 ada di [`rumus/gatt_okok.py`](../rumus/gatt_okok.py). Perintah 20 belum diurai.

```22:24:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
    private byte[] splitPackInfo(byte b) {
        return new byte[]{(byte) (((byte) (b << 4)) >> 4), (byte) (b >> 4)};
    }
```

```204:228:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
    private boolean packageProcess(byte[] bArr) {
        byte b = bArr[2];
        byte b2 = bArr[3];
        int i = b - 2;
        byte[] bArrSplitPackInfo = splitPackInfo(bArr[4]);
        byte[] bArr2 = new byte[i];
        for (int i2 = 0; i2 < i; i2++) {
            bArr2[i2] = bArr[i2 + 5];
        }
        if (b2 == 18) {
            if (bArrSplitPackInfo[1] == 1) {
                HashMap<Byte, byte[]> map = this.lstBuffer;
                if (map != null) {
                    map.clear();
                } else {
                    this.lstBuffer = new HashMap<>();
                }
            }
            if (this.lstBuffer.containsKey(Byte.valueOf(bArrSplitPackInfo[1]))) {
                this.lstBuffer.remove(Byte.valueOf(bArrSplitPackInfo[1]));
            }
            this.lstBuffer.put(Byte.valueOf(bArrSplitPackInfo[1]), bArr2);
            if (bArrSplitPackInfo[0] == bArrSplitPackInfo[1]) {
                if (this.lstBuffer.size() == bArrSplitPackInfo[0]) {
                    return true;
```

Urutan rakitan perintah 18 dan 19, dibaca setelah buffer digabung:

```124:150:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                        if (b4 == 18) {
                            csFatScale3.setHistoryData(false);
                        } else {
                            this.fatScale.setWeighingDate(new Date(((long) BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConvertMap2ByteArray, 0, 4))) * 1000));
                            this.fatScale.setHistoryData(true);
                        }
                        byte b5 = bArrConvertMap2ByteArray[4];
                        this.fatScale.setRoleId(BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConvertMap2ByteArray, 6, 4)));
                        byte[] bArrSubBytes8 = BytesUtil.subBytes(bArrConvertMap2ByteArray, 10, 2);
                        this.fatScale.setScaleProperty(b5);
                        WeightParserReturn weightParserReturnParser3 = WeightUnitUtil.Parser(bArrSubBytes8[0], bArrSubBytes8[1], b5, false);
                        this.fatScale.setWeight(weightParserReturnParser3.kgWeight * 10.0d);
                        this.fatScale.setScaleWeight(weightParserReturnParser3.scaleWeight);
                        this.fatScale.setAxunge(BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConvertMap2ByteArray, 12, 2)));
                        this.fatScale.setWater(BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConvertMap2ByteArray, 14, 2)));
                        this.fatScale.setMuscle(BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConvertMap2ByteArray, 16, 2)));
                        this.fatScale.setBmr(BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConvertMap2ByteArray, 18, 2)));
                        this.fatScale.setVisceral_fat(BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConvertMap2ByteArray, 20, 2)));
                        this.fatScale.setBone(BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConvertMap2ByteArray, 22, 1)));
                        double muscle = (this.fatScale.getMuscle() / this.fatScale.getWeight()) * 100.0d;
                        if (muscle >= 50.0d) {
                            muscle = this.fatScale.getMuscle();
                            if (muscle >= 50.0d) {
                                muscle = 50.0d;
                            }
                        }
                        this.fatScale.setMuscle((int) (muscle * 10.0d));
```

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

Sesudah itu otot dihitung ulang: `(otot / berat) * 100`. Jika hasilnya di bawah 50, angka itu disimpan sebagai persen. Jika 50 atau lebih, nilai otot yang sudah tersimpan dipakai dan dibatasi 50. Nilai akhir dikali 10, dipotong ke int, lalu [`setMuscle`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java) membagi 10 lagi.

```150:150:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                        this.fatScale.setMuscle((int) (muscle * 10.0d));
```

[`bytesToInt`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) pada id peran dan waktu Unix memakai `Integer.parseInt`. Empat byte di atas 2147483647 menjadi 0. Waktu setelah 2038-01-19 03:14:07 UTC ikut aturan itu.

```75:80:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
    public static int bytesToInt(byte[] bArr) {
        try {
            return Integer.parseInt(bytesToHexString(bArr), 16);
        } catch (NumberFormatException unused) {
            return 0;
        }
```

Rakitan perintah 20: offset 0–1 berat, offset 2 byte properti, lalu id peran 4 byte berulang.

```173:184:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                        this.fatConfirm = new CsFatConfirm();
                        byte[] bArrSubBytes9 = BytesUtil.subBytes(bArrConverList2ByteArray, 0, 2);
                        byte b6 = bArrConverList2ByteArray[2];
                        WeightParserReturn weightParserReturnParser4 = WeightUnitUtil.Parser(bArrSubBytes9[0], bArrSubBytes9[1], b6, false);
                        this.fatConfirm.setScaleProperty(b6);
                        this.fatConfirm.setWeight(weightParserReturnParser4.kgWeight * 10.0d);
                        this.fatConfirm.setScaleWeight(weightParserReturnParser4.scaleWeight);
                        ArrayList<Integer> arrayList = new ArrayList<>();
                        for (int i4 = 3; i4 < bArrConverList2ByteArray.length; i4 += 4) {
                            arrayList.add(Integer.valueOf(BytesUtil.bytesToInt(BytesUtil.subBytes(bArrConverList2ByteArray, i4, 4))));
                        }
                        this.fatConfirm.setMatchedRoleList(arrayList);
```

## Skala komposisi di `CsFatScale`

Nilai mentah dibagi 10 di [`CsFatScale`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java), lalu dibatasi:

| Field | Batas yang lolos | Di luar batas | Metode |
|---|---|---|---|
| Lemak | 5 sampai 45 persen. `65535` langsung 0 | 0 | `setAxunge` |
| Air | 20 sampai 85, dan di bawah 100 | 0 | `setWater` |
| Otot | di bawah 100 | 0 | `setMuscle` |
| Lemak visceral | tidak di atas 59 dan di bawah 100 | 0. Nilai mentah tetap di `ori_visceral_fat` | `setVisceral_fat` |
| Tulang | 1 sampai 4 | di bawah 1 menjadi 0, di atas 4 menjadi 4. `65535` menjadi 0 | `setBone` |
| BMR | `65535` menjadi 0. Jika mentah `5000` atau lebih, dibagi 10. Selain itu mentah disimpan utuh | — | `setBmr` |

```152:215:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java
    public void setAxunge(double d) {
        double d2 = 0.0d;
        if (d >= 65535.0d) {
            this.axunge = 0.0d;
            return;
        }
        double d3 = d / 10.0d;
        if (d3 >= 5.0d && d3 <= 45.0d) {
            d2 = d3;
        }
        this.axunge = d2;
    }

    public void setWater(double d) {
        double d2 = d / 10.0d;
        if (d2 >= 100.0d || d2 < 20.0d || d2 > 85.0d) {
            d2 = 0.0d;
        }
        this.water = d2;
    }

    public void setMuscle(double d) {
        double d2 = d / 10.0d;
        if (d2 >= 100.0d) {
            d2 = 0.0d;
        }
        this.muscle = d2;
    }

    public void setBmr(double d) {
        if (d >= 65535.0d) {
            this.bmr = 0.0d;
            return;
        }
        if (d >= 5000.0d) {
            d /= 10.0d;
        }
        this.bmr = d;
    }

    public void setVisceral_fat(double d) {
        this.ori_visceral_fat = d;
        double d2 = d / 10.0d;
        if (d2 >= 100.0d || d2 > 59.0d) {
            d2 = 0.0d;
        }
        this.visceral_fat = d2;
    }

    public void setBone(double d) {
        double d2 = 0.0d;
        if (d >= 65535.0d) {
            this.bone = 0.0d;
            return;
        }
        double d3 = d / 10.0d;
        if (d3 >= 1.0d) {
            d2 = 4.0d;
            if (d3 <= 4.0d) {
                d2 = d3;
            }
        }
        this.bone = d2;
    }
```

Di [`CsBtUtil_v11.handleConnectedInfo`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java), data stabil dengan lemak di atas 0 menandai jenis perangkat: `ori_visceral_fat == 25600` menjadi tipe 2, selain itu tipe 1. Berat yang sampai ke listener dibuang jika `<= 0` atau `>= 6000` kilogram. Riwayat dibuang jika tanggalnya sebelum `2010-01-01` atau lebih dari 5 menit di depan jam ponsel.

```959:966:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java
                    if (fatScale.getLockFlag() == 1) {
                        if (fatScale.getAxunge() > 0.0d) {
                            if (fatScale.ori_visceral_fat == 25600.0d) {
                                setDeviceInfo(2);
                            } else {
                                setDeviceInfo(1);
                            }
                        }
```

```994:1000:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil_v11.java
                    if (fatScale.getWeight() >= 6000.0d || fatScale.getWeight() <= 0.0d) {
                        return;
                    }
                    LogUtil.i(TAG, fatScale.toString());
                    if (fatScale.isHistoryData()) {
                        try {
                            if (fatScale.getWeighingDate().getTime() < new SimpleDateFormat(TimeUtil.TIME_FORMAT1).parse("2010-01-01 00:00:00").getTime() || fatScale.getWeighingDate().getTime() > System.currentTimeMillis() + 300000) {
```

## Perintah ponsel ke timbangan

[`syncChipseaInstruction`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/syncChipseaInstruction.java) menyusun frame `0xCA`. Checksum adalah XOR dari byte 1 sampai byte sebelum checksum, lewat [`BytesUtil.getDatasXor`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java). Header `0xCA` tidak ikut XOR. Sisa byte hingga panjang 20 diisi 0 pada perintah yang memakai buffer 20 byte.

```107:114:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java
public static byte getDatasXor(byte[] bArr, int i, int i2) {
    byte b = bArr[i];
    while (true) {
        i = (byte) (i + 1);
        if (i > i2) {
            return b;
        }
        b = (byte) (b ^ bArr[i]);
```

| Perintah | Versi | Byte perintah | Isi | Metode |
|---|---|---|---|---|
| Ambil riwayat | 17 | 17 | panjang 2, byte indeks 1 | [`sycnRetrieveHistoryData_v11`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/syncChipseaInstruction.java) |
| Pilih pengguna | 17 | 21 | panjang 5, id peran 4 byte | [`syncSelectedUserId`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/syncChipseaInstruction.java) |
| Kirim semua peran | 17 | 16 | waktu Unix, lalu tiap peran 8 byte: id, umur dengan bit 7 = jenis kelamin 1, tinggi, berat | [`sycnAllRoleInfo_v11`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/syncChipseaInstruction.java) |
| Kirim satu peran, v10 | 16 | 1 | `yy MM dd HH mm ss`, id peran, jenis kelamin, umur, tinggi | [`syncRoleInfo_v10`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/syncChipseaInstruction.java) |

Ambil riwayat:

```26:36:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/syncChipseaInstruction.java
public static byte[] sycnRetrieveHistoryData_v11() {
    byte[] bArr = new byte[20];
    bArr[0] = -54;
    bArr[1] = 17;
    bArr[2] = 2;
    bArr[3] = 17;
    bArr[4] = 1;
    bArr[5] = BytesUtil.getDatasXor(bArr, 1, 4);
```

Jenis kelamin menempel di bit 7 umur:

```17:19:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/syncChipseaInstruction.java
private static byte mergeSexAndAge(byte b, byte b2) {
    return (byte) (b == 1 ? b2 | 128 : b2 & 127);
}
```

Peran jamak dipecah. Tiap paket memuat paling banyak 14 byte muatan, dengan nibble indeks yang sama seperti penerimaan (`mergePackageField`, `size / 14`).

## Checksum

[`chipseaBroadcastFrame`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaBroadcastFrame.java) dan [`chipseaStraightFrame`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java) tidak memeriksa XOR saat menerima. Konstruktor siaran hanya menolak header yang tidak dikenal. `process` GATT hanya menolak header selain `0xCA`.

Pemeriksaan XOR ada di [`com.chipsea.btlib.model.Frame`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/Frame.java). Kelas itu hanya dipakai parser lama [`CsBtUtil`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/CsBtUtil.java) (dua panggilan `new Frame(...)` di berkas itu). Syaratnya: header `0xCA`, byte panjang sama dengan panjang frame minus 4, dan checksum sama dengan `versi XOR panjang XOR xor(deviceType, perintah, muatan)`. Pada bentuk itu, offset 3 adalah device type dan offset 4 adalah perintah.

```39:51:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/Frame.java
        if (bArr[0] != -54) {
            throw new FrameFormatIllegalException("帧格式错误 -- 不是正确的帧头");
        }
        if (bArr[2] != bArr.length - 4) {
            throw new FrameFormatIllegalException("帧格式错误 -- 数据长度不匹配");
        }
        setFrameVers(bArr[1]);
        setDataAreaLen(bArr[2]);
        setCheckByte(bArr[bArr.length - 1]);
        FrameData frameData = new FrameData(bArr[3], bArr[4], BytesUtil.subBytes(bArr, 5, bArr[2] - 2));
        setDatasArea(frameData);
        if (((byte) (((byte) (bArr[2] ^ bArr[1])) ^ frameData.getDatasXor())) != getCheckByte()) {
            throw new FrameFormatIllegalException("帧格式错误 -- 实际异或值与获得异或值不一致");
```

## Yang belum tertutup peta ini

Keputusan rilis pertama mengeluarkan siaran `0xC0` yang bit enkripsinya menyala. Nilai 4 byte tetap tidak ada di APK. [`OkokScaleEncryptedKeyUtils.getOkokScaleEncryptedKeySync`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java) hanya membaca prefs. Parser siaran `0xCA`, `0xC0` tanpa bit itu, dan `0xFF` ada di [`rumus/siaran_okok.py`](../rumus/siaran_okok.py). Parser itu menolak siaran terenkripsi. Java mengisi berat 0 bila kunci kosong. Parser itu juga menolak frame yang lebih pendek dari field yang dibaca. Pada `0xC0` lebih pendek dari 9 byte, Java kembali lebih awal dan berat tetap 0.

Parser GATT versi 16 serta perintah 0 dan 1 pada versi 17 ada di [`rumus/gatt_okok.py`](../rumus/gatt_okok.py). Pada perintah 0 dan 1, tanda kunci adalah byte perintah di offset 3. Properti ada di offset 11. Tidak ada komposisi. Pada versi 16, komposisi paket hanya diisi bila bit kunci properti = 1, lalu disempitkan seperti [`CsFatScale`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java). Angka itu bukan laporan. Potongan yang tidak muat menjadi 0, sama dengan [`bytesToInt`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) bila [`subBytes`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/util/BytesUtil.java) mengembalikan null. Rakitan perintah 18 dan 19 ada di [`GattParser`](../rumus/gatt_okok.py). Perintah 20 belum diurai.

```106:110:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/protocal/chipseaStraightFrame.java
                this.fatScale.setLockFlag(b4);
                this.fatScale.setScaleProperty(bArr[11]);
                WeightParserReturn weightParserReturnParser2 = WeightUnitUtil.Parser(bArrSubBytes7[0], bArrSubBytes7[1], this.fatScale.getScaleProperty(), false);
                this.fatScale.setWeight(weightParserReturnParser2.kgWeight * 10.0d);
                this.fatScale.setScaleWeight(weightParserReturnParser2.scaleWeight);
```

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

```152:160:ScaleHealtSource/jadx-protocol/sources/com/chipsea/btlib/model/device/CsFatScale.java
    public void setAxunge(double d) {
        double d2 = 0.0d;
        if (d >= 65535.0d) {
            this.axunge = 0.0d;
            return;
        }
        double d3 = d / 10.0d;
        if (d3 >= 5.0d && d3 <= 45.0d) {
            d2 = d3;
```

```41:45:ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/util/OkokScaleEncryptedKeyUtils.java
    public static String getOkokScaleEncryptedKeySync(String str) {
        Context contexts = MyAplication.getContexts();
        if (contexts != null && !TextUtils.isEmpty(str)) {
            try {
                return PrefsUtil.getInstance(contexts.getApplicationContext()).getOkokScaleEncryptedKey(str);
```

Rumus laporan OKOK ada di [`CsAlgoBuilder`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java). Pada timbangan yang bukan 8 elektroda, hasil yang dipakai adalah native [`cs_bias_v235`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/v235/CSBiasAPI.java) bila pemanggilan berhasil. Rumus Java [`getBFR_Raw`](../ScaleHealtSource/jadx-protocol/sources/com/chipsea/code/algorithm/CsAlgoBuilder.java) adalah cadangan. Isi `libchipsea_bias_v235.so` ditulis ulang di [`rumus/cs_bias_v235.py`](../rumus/cs_bias_v235.py). Frekuensi ganda dan multi memakai [`cs_bias_vA019`](../ScaleHealtSource/jadx-protocol/sources/chipsea/bias/vA019/CSBiasAPI.java) di `libchipsea_bias_vA019.so`, ditulis ulang di [`rumus/cs_bias_vA019.py`](../rumus/cs_bias_vA019.py).

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

[`Myndk`](../ScaleHealtSource/jadx-protocol/sources/com/example/jnipack/Myndk.java) memuat `libBodyFatScaleAlg.so` untuk jalur XS, lewat [`n.e`](../ScaleHealtSource/jadx-protocol/sources/n/e.java) (`FormulasHelper`). Kelas itu tidak dipanggil `CsAlgoBuilder`.

Parser XS tetap di [`libprotocol.so`](../ScaleHealtSource/split_config.arm64_v8a/lib/arm64-v8a/libprotocol.so). Pembungkus Java-nya [`com.xshq.sdk.Protocol`](../ScaleHealtSource/jadx-protocol/sources/com/xshq/sdk/Protocol.java) memuat library itu dan menyatakan `parseScan`, `parseData`, serta `getFuncBuffer` sebagai method native. Di hasil dekompilasi ini, `parseScan` dipanggil dari [`XsBluetoothManager`](../ScaleHealtSource/jadx-protocol/sources/com/ss/bluetooth/sscore/XsBluetoothManager.java). `parseData` dan `getFuncBuffer` belum punya pemanggil Java di folder itu.
