# Implementasi AES-128 Manual

Project ini berisi implementasi algoritma AES-128 secara manual (tanpa memakai library AES untuk proses utama), ditujukan untuk tugas kuliah kriptografi.

## Struktur Project

- `src/aes_core.py` - komponen inti AES (SubBytes, ShiftRows, MixColumns, AddRoundKey, Key Expansion, fungsi invers, encrypt/decrypt block)
- `src/aes_utils.py` - utilitas padding, konversi teks/hex, dan formatter matrix state 4x4
- `src/aes_cli.py` - program terminal untuk menjalankan enkripsi/dekripsi dan menampilkan jejak tiap round
- `test_vector_aes.py` - validasi hasil akhir implementasi manual terhadap library AES
- `docs/laporan-aes.md` - laporan akademik lengkap

## Cara Menjalankan

1. Jalankan demo default (sesuai soal tugas):

```bash
python src/aes_cli.py
```

2. Jalankan dengan input kustom:

```bash
python src/aes_cli.py --plaintext "HELLO AES" --key "KUNCIKULIAH"
```

3. Jalankan validasi test vector:

```bash
python test_vector_aes.py
```

## Catatan

- Demo ini fokus pada **single block AES (16 byte)** agar proses internal tiap round mudah dibaca dan di-screenshot.
- Jika panjang plaintext atau key kurang dari 16 byte, sistem menambahkan padding PKCS#7 hingga 16 byte.
- Library AES hanya digunakan pada file pengujian untuk validasi hasil akhir, bukan untuk proses utama.
