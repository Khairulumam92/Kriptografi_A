# Laporan Implementasi AES-128 Manual

## 1. Pendahuluan

Kriptografi modern memegang peran penting dalam menjaga kerahasiaan data digital. Pada tugas ini, algoritma yang diimplementasikan adalah **Advanced Encryption Standard (AES)** dengan ukuran kunci **128-bit**. Implementasi dilakukan secara manual pada level transformasi internal AES, bukan sekadar memanggil pustaka siap pakai.

Tujuan utama tugas:

1. Mengimplementasikan proses enkripsi AES-128 dari plaintext ke ciphertext.
2. Mengimplementasikan proses dekripsi AES-128 dari ciphertext kembali ke plaintext.
3. Menampilkan **state matrix 4x4** pada setiap langkah round agar proses internal AES dapat dipelajari secara rinci.
4. Memvalidasi hasil akhir dengan library eksternal sebagai pembanding.

Data uji utama:

- Plaintext: `MOH KHAIRUL UMAM`
- Key: `KAMPUSUMM`

Ketika panjang key kurang dari 16 byte, sistem menerapkan padding sehingga key menjadi 16 byte sebelum key expansion.

---

## 2. Dasar Teori

### 2.1 Pengertian AES

AES (Advanced Encryption Standard) adalah standar enkripsi simetris yang ditetapkan oleh NIST melalui FIPS-197. AES bekerja pada blok data 128-bit dengan pilihan panjang kunci 128, 192, atau 256 bit. Pada tugas ini digunakan **AES-128**, sehingga jumlah round adalah **10 round**.

### 2.2 Konsep Kriptografi Simetris

Pada kriptografi simetris, proses enkripsi dan dekripsi menggunakan **kunci yang sama**. Pengirim dan penerima harus menjaga kunci tersebut tetap rahasia. Keunggulan model ini adalah performa tinggi untuk enkripsi data dalam jumlah besar, sedangkan tantangannya ada pada distribusi kunci yang aman.

### 2.3 Struktur State Matrix pada AES

AES memproses data sebagai matriks 4x4 byte yang disebut **state**. Blok 16 byte dimasukkan secara kolom (column-major). Seluruh transformasi per round (`SubBytes`, `ShiftRows`, `MixColumns`, `AddRoundKey`) bekerja terhadap state ini.

Contoh format state yang digunakan pada output:

```text
19 a0 9a e9
3d f4 c6 f8
e3 e2 8d 48
be 2b 2a 08
```

### 2.4 Konsep XOR pada AES

Operasi XOR (`^`) menjadi komponen inti pada AES, terutama pada:

- `AddRoundKey`: state di-XOR dengan round key.
- `KeyExpansion`: pembentukan round key baru dari word sebelumnya.

Sifat penting XOR:

- `A ^ A = 0`
- `A ^ 0 = A`
- bersifat reversible (membantu proses dekripsi).

### 2.5 Penjelasan Tiap Transformasi Round

1. **SubBytes**  
   Setiap byte state diganti menggunakan tabel substitusi non-linear (S-Box). Tujuannya menambah confusion.

2. **ShiftRows**  
   Baris state digeser ke kiri secara siklik:
   - baris 0: tetap
   - baris 1: geser 1
   - baris 2: geser 2
   - baris 3: geser 3  
   Tujuannya menyebarkan pengaruh byte antar kolom.

3. **MixColumns**  
   Tiap kolom dianggap polinomial dan ditransformasikan pada GF(2^8), sehingga menghasilkan diffusion yang kuat.

4. **AddRoundKey**  
   State di-XOR dengan round key hasil key expansion.

### 2.6 Key Expansion (Jadwal Kunci)

AES-128 mengubah 1 kunci awal 16 byte menjadi 11 round key (masing-masing 16 byte). Prosesnya melibatkan:

- `RotWord`
- `SubWord`
- konstanta `RCON`
- operasi XOR antar word

Total word untuk AES-128 adalah 44 word (4 word per round key x 11 round key).

### 2.7 Proses Enkripsi AES-128

Alur enkripsi:

1. Initial `AddRoundKey`
2. Round 1 sampai 9:
   - `SubBytes`
   - `ShiftRows`
   - `MixColumns`
   - `AddRoundKey`
3. Round 10:
   - `SubBytes`
   - `ShiftRows`
   - `AddRoundKey` (tanpa `MixColumns`)

### 2.8 Proses Dekripsi AES-128

Dekripsi memakai transformasi invers:

- `InvShiftRows`
- `InvSubBytes`
- `AddRoundKey`
- `InvMixColumns` (untuk round menengah)

Urutannya merupakan kebalikan logis dari enkripsi.

### 2.9 Mengapa Round Terakhir AES Tidak Menggunakan MixColumns

Round terakhir memang secara desain AES tidak menyertakan `MixColumns` agar struktur dekripsi tetap efisien dan simetris secara matematis. Keamanan AES tetap terjaga karena diffusion dari round sebelumnya sudah cukup kuat.

### 2.10 Mengapa AES Dianggap Aman

AES dinilai aman karena:

1. Tidak ada serangan praktis yang memecahkan AES penuh (AES-128) dengan kompleksitas realistis.
2. Memiliki kombinasi confusion dan diffusion yang kuat.
3. Struktur S-Box tahan terhadap serangan linear dan diferensial pada level praktis.
4. Telah diuji luas oleh komunitas akademik dan industri selama bertahun-tahun.

### 2.11 Kelemahan Implementasi AES yang Salah

Walaupun algoritmanya kuat, implementasi yang salah bisa berbahaya, misalnya:

1. Salah orientasi state matrix (row-major vs column-major).
2. Key expansion tidak sesuai standar.
3. Salah urutan operasi dekripsi.
4. Penggunaan mode operasi yang tidak aman pada data multi-blok.
5. Tidak ada autentikasi integritas (hanya enkripsi tanpa MAC/AEAD).
6. Kerentanan side-channel pada implementasi nyata (timing/power/cache leak).

---

## 3. Implementasi Program

Struktur folder:

- `src/aes_core.py`
- `src/aes_utils.py`
- `src/aes_cli.py`
- `test_vector_aes.py`
- `README.md`

Karakteristik implementasi:

1. Implementasi AES dilakukan manual.
2. Tidak memakai library AES pada proses inti.
3. Output menampilkan state matrix detail di setiap langkah round.
4. Validasi terhadap library dilakukan terpisah di file pengujian.

---

## 4. Penjelasan Source Code per Fungsi

### 4.1 Fungsi Inti pada `aes_core.py`

1. `sub_bytes(state)`  
   Melakukan substitusi byte menggunakan `S_BOX`.

2. `shift_rows(state)`  
   Menggeser tiap baris state ke kiri secara siklik.

3. `mix_columns(state)`  
   Mencampur tiap kolom state pada GF(2^8) menggunakan matriks standar AES.

4. `add_round_key(state, round_key)`  
   Melakukan XOR antara state dan round key.

5. `key_expansion(key)`  
   Menghasilkan 11 round key dari 1 kunci 128-bit.

6. `inv_sub_bytes(state)`  
   Substitusi invers menggunakan `INV_S_BOX`.

7. `inv_shift_rows(state)`  
   Menggeser baris ke kanan (kebalikan `ShiftRows`).

8. `inv_mix_columns(state)`  
   Operasi invers dari `MixColumns`.

9. `aes_encrypt_block(block, key, collect_trace=True)`  
   Menjalankan enkripsi AES-128 satu blok dan mengumpulkan jejak state setiap langkah.

10. `aes_decrypt_block(block, key, collect_trace=True)`  
    Menjalankan dekripsi AES-128 satu blok dan mengumpulkan jejak state setiap langkah.

### 4.2 Fungsi Pendukung pada `aes_utils.py`

1. `pad_to_16_pkcs7_if_needed(data)`  
   Menambahkan padding PKCS#7 jika panjang data kurang dari 16 byte.

2. `pkcs7_unpad(data)`  
   Menghapus padding setelah dekripsi.

3. `text_to_block(text)` dan `key_to_block(key_text)`  
   Mengubah input teks menjadi blok 16 byte siap proses AES.

4. `format_state_matrix(state)`  
   Memformat state ke tampilan 4x4 heksadesimal agar mudah dibaca/screenshot.

### 4.3 Program Utama pada `aes_cli.py`

Program ini:

1. Membaca plaintext dan key.
2. Menampilkan representasi ASCII dan hex sebelum enkripsi.
3. Menampilkan jejak enkripsi round 0 hingga round 10.
4. Menampilkan ciphertext akhir.
5. Menampilkan jejak dekripsi hingga plaintext kembali.
6. Menampilkan status validasi round-trip.

---

## 5. Hasil Enkripsi

Data input:

- Plaintext (ASCII): `MOH KHAIRUL UMAM`
- Key (ASCII): `KAMPUSUMM`

Representasi heksadesimal (hasil program):

- Plaintext (HEX): `4d 4f 48 20 4b 48 41 49 52 55 4c 20 55 4d 41 4d`
- Key (HEX): `4b 41 4d 50 55 53 55 4d 4d 07 07 07 07 07 07 07`

Ciphertext akhir AES-128:

- `dfe3fd51fc2760bb1c513d097f2ee341`

---

## 6. Hasil Dekripsi

Hasil dekripsi dari ciphertext menghasilkan kembali:

- `MOH KHAIRUL UMAM`

Status:

- **VALID** (plaintext hasil dekripsi sama dengan plaintext awal).

---

## 7. Screenshot / Output Tiap Round

Program telah mencetak seluruh state matrix untuk:

1. Initial State
2. AddRoundKey awal
3. Round 1 sampai Round 10 (setiap tahap transformasi)
4. Ciphertext State
5. Proses dekripsi dari awal hingga state plaintext kembali

Contoh bagian output (potongan):

```text
Round 1 - SubBytes:
6f 72 c0 00
ab af 00 d6
6b fa b3 5a
51 f2 cc d6

Round 1 - ShiftRows:
6f 72 c0 00
af 00 d6 ab
b3 5a 6b fa
d6 51 f2 cc
```

Untuk keperluan laporan tugas:

1. Jalankan `python src/aes_cli.py`.
2. Ambil screenshot konsol per bagian round sesuai kebutuhan dosen/asisten.
3. Tempel screenshot ke dokumen akhir (PDF/Word) bila diminta format cetak.

---

## 8. Analisis Hasil

1. Implementasi manual berhasil menghasilkan ciphertext valid dan proses dekripsi yang konsisten.
2. Validasi dengan library AES menunjukkan ciphertext manual sama persis.
3. Jejak per-round membantu memahami bagaimana perubahan satu byte memengaruhi keseluruhan state pada round berikutnya.
4. Penggunaan format matrix 4x4 heksadesimal memudahkan pembuktian langkah algoritma saat presentasi.
5. Implementasi ini cocok sebagai media belajar, namun untuk produksi diperlukan mode operasi aman (misalnya GCM) dan perhatian terhadap side-channel.

---

## 9. Kesimpulan

Implementasi AES-128 manual pada proyek ini telah memenuhi kebutuhan tugas:

1. Mengimplementasikan fungsi inti AES dan fungsi invers secara eksplisit.
2. Menampilkan transformasi state matrix di setiap tahap round enkripsi dan dekripsi.
3. Menghasilkan ciphertext valid dan mengembalikan plaintext asli dengan benar.
4. Menyediakan dokumentasi akademik formal yang dapat digunakan langsung untuk laporan tugas.

Dengan demikian, tujuan pembelajaran konseptual (teori AES) dan tujuan teknis (implementasi program) tercapai secara menyeluruh.
