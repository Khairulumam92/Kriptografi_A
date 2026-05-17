# Implementasi DES (Data Encryption Standard)

Project tugas kriptografi: implementasi **DES standar 64-bit** secara **manual** (tanpa `Crypto.Cipher.DES` pada proses utama), dengan output proses per ronde untuk laporan dan presentasi.

## Struktur Project

| Berkas | Fungsi |
|--------|--------|
| `src/des_core.py` | IP, FP, E, S-Box, P, key schedule, 16 ronde Feistel, enkripsi/dekripsi |
| `src/des_utils.py` | Konversi hex/text, PKCS#7 padding, kunci ASCII → 64-bit |
| `src/des_verbose.py` | Formatter output biner/hex per ronde |
| `src/des_demo.py` | **Demo utama tugas** (plaintext/key ASCII + trace lengkap) |
| `src/des_cli.py` | CLI enkripsi/dekripsi |
| `docs/laporan-des.md` | Laporan akademik lengkap |
| `test_vector_des.py` | Unit test + contoh `KHAIRULUMAM` / `KAMPUSUMM` |

## Demo Tugas (Contoh Soal)

```powershell
cd "Tugas 2 - DES"
python src/des_demo.py
```

Data bawaan:

- **PLAINTEXT:** `KHAIRULUMAM` (11 byte → PKCS#7 → 16 byte = 2 blok DES)
- **KEY:** `KAMPUSUMM` (9 byte ASCII → 8 byte pertama: `KAMPUSUM`)

**Ciphertext referensi (ECB per blok, tanpa mode chaining):** `D5B57564844B76465927F24F34ACC6E6`

Opsi:

```powershell
python src/des_demo.py --all-blocks-verbose
```

Menampilkan trace ronde untuk **semua** blok (output sangat panjang).

## CLI

Enkripsi teks + kunci ASCII:

```powershell
python src/des_cli.py encrypt --input-format text --key-format text --data "KHAIRULUMAM" --key "KAMPUSUMM" --verbose
```

Dekripsi:

```powershell
python src/des_cli.py decrypt --input-format text --key-format text --data D5B57564844B76465927F24F34ACC6E6 --key "KAMPUSUMM" --verbose
```

Vector standar FIPS (hex):

```powershell
python src/des_cli.py encrypt --input-format hex --data 0123456789ABCDEF --key 133457799BBCDFF1
```

## Pengujian

```powershell
python -m unittest test_vector_des.py -v
```

## Validasi Library (Opsional)

```powershell
pip install -r requirements.txt
```

Demo membandingkan ciphertext dengan **PyCryptodome** hanya sebagai pembanding, bukan proses enkripsi utama.

## Catatan Akademik

- DES: blok 64-bit, kunci efektif 56-bit, 16 ronde Feistel.
- Program ini **bukan** untuk produksi; DES sudah tidak aman untuk data modern (lihat `docs/laporan-des.md`).
