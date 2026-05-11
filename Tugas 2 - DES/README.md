# Implementasi DES (Data Encryption Standard)

Project ini berisi implementasi algoritma DES secara manual (tanpa library DES siap pakai), berbasis terminal/console, untuk kebutuhan tugas kriptografi.

## Struktur Project

- `src/des_core.py` - komponen inti DES (IP, FP, E, S-Box, P, key schedule, 16 ronde Feistel)
- `src/des_utils.py` - utilitas konversi data, pemecahan blok 64-bit, dan padding/unpadding
- `src/des_cli.py` - antarmuka terminal untuk enkripsi/dekripsi
- `docs/laporan-des.md` - laporan algoritma DES langkah demi langkah

## Cara Menjalankan

Pastikan Python 3 tersedia.

### 1) Enkripsi satu blok (input HEX)

```bash
python src/des_cli.py encrypt --input-format hex --data 0123456789ABCDEF --key 133457799BBCDFF1
```

### 2) Dekripsi satu blok (input HEX)

```bash
python src/des_cli.py decrypt --input-format hex --data 85E813540F0AB405 --key 133457799BBCDFF1
```

### 3) Enkripsi plaintext TEXT (multi-blok + padding)

```bash
python src/des_cli.py encrypt --input-format text --data "Belajar DES di kelas kriptografi" --key 133457799BBCDFF1
```

### 4) Dekripsi ciphertext ke TEXT

Gunakan ciphertext hasil enkripsi mode text:

```bash
python src/des_cli.py decrypt --input-format text --data <CIPHERTEXT_HEX> --key 133457799BBCDFF1
```

### 5) Menampilkan proses internal ronde

Tambahkan `--verbose` (ditampilkan untuk blok pertama):

```bash
python src/des_cli.py encrypt --input-format hex --data 0123456789ABCDEF --key 133457799BBCDFF1 --verbose
```

## Catatan

- Key DES diinput sebagai 16 karakter hex (64-bit).
- Untuk mode `hex`, data harus kelipatan 16 karakter hex (tiap 16 hex = 1 blok DES).
- Untuk mode `text`, sistem memakai PKCS#7 padding pada ukuran blok 8 byte.
