"""
Demo tugas kuliah DES — plaintext dan key ASCII dengan output rinci.

Contoh bawaan:
  PLAINTEXT : KHAIRULUMAM
  KEY       : KAMPUSUMM

Jalankan dari folder project:
  python src/des_demo.py
  python src/des_demo.py --plaintext "KHAIRULUMAM" --key "KAMPUSUMM"
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.des_core import des_decrypt_block, des_encrypt_block
    from src.des_utils import (
        bytes_to_binary_groups,
        pkcs7_pad,
        pkcs7_unpad,
        text_key_to_bytes,
    )
else:
    from .des_core import des_decrypt_block, des_encrypt_block
    from .des_utils import (
        bytes_to_binary_groups,
        pkcs7_pad,
        pkcs7_unpad,
        text_key_to_bytes,
    )


def _banner(title: str) -> None:
    width = 78
    print("\n" + "=" * width)
    print(title.center(width))
    print("=" * width)


def _print_ascii_block(label: str, text: str) -> None:
    raw = text.encode("utf-8")
    print(f"\n{label}")
    print(f"  ASCII     : {text!r}")
    print(f"  Panjang   : {len(raw)} byte")
    print(f"  HEX       : {raw.hex().upper()}")
    print(f"  BIN (8b)  : {bytes_to_binary_groups(raw)}")


def validate_with_pycryptodome(padded: bytes, key8: bytes, expected_ct_hex: str) -> None:
    """Validasi opsional memakai PyCryptodome (bukan proses utama)."""
    try:
        from Crypto.Cipher import DES
    except ImportError:
        print("\n[Validasi] PyCryptodome tidak terpasang — lewati perbandingan library.")
        return

    cipher = DES.new(key8, DES.MODE_ECB)
    ref = cipher.encrypt(padded).hex().upper()
    ok = ref == expected_ct_hex
    print("\n[Validasi PyCryptodome — MODE_ECB, hanya pembanding]")
    print(f"  Ciphertext referensi : {ref}")
    print(f"  Ciphertext program   : {expected_ct_hex}")
    print(f"  Status               : {'SESUAI' if ok else 'TIDAK SESUAI'}")


def run_demo(plaintext: str, key_text: str, verbose_all_blocks: bool = False) -> None:
    _banner("TUGAS KRIPTOGRAFI — IMPLEMENTASI DES MANUAL")

    _print_ascii_block("PLAINTEXT (sebelum padding)", plaintext)
    padded = pkcs7_pad(plaintext.encode("utf-8"), 8)
    print("\nPLAINTEXT (setelah PKCS#7 padding ke kelipatan 8 byte)")
    print(f"  HEX       : {padded.hex().upper()}")
    print(f"  BIN (8b)  : {bytes_to_binary_groups(padded)}")
    print(f"  Panjang   : {len(padded)} byte ({len(padded) // 8} blok DES)")

    _print_ascii_block("KEY (ASCII)", key_text)
    key8 = text_key_to_bytes(key_text)
    key_hex = key8.hex().upper()
    print("\nKEY (64-bit untuk DES)")
    print(f"  Catatan   : DES memakai 8 byte kunci; jika key > 8 byte diambil 8 byte pertama.")
    print(f"  HEX       : {key_hex}")
    print(f"  BIN (8b)  : {bytes_to_binary_groups(key8)}")

    blocks = [padded[i : i + 8].hex().upper() for i in range(0, len(padded), 8)]
    ciphertext_parts = []

    for block_idx, block_hex in enumerate(blocks):
        _banner(f"ENKRIPSI BLOK {block_idx + 1} / {len(blocks)}")
        print(f"  Blok plaintext (HEX): {block_hex}")
        show_verbose = verbose_all_blocks or block_idx == 0
        ct = des_encrypt_block(block_hex, key_hex, verbose=show_verbose)
        ciphertext_parts.append(ct)
        print(f"\n>> Ciphertext blok {block_idx + 1}: {ct}")

    full_cipher = "".join(ciphertext_parts)
    _banner("HASIL ENKRIPSI AKHIR")
    print(f"  Ciphertext (HEX gabungan): {full_cipher}")

    if len(blocks) == 1:
        validate_with_pycryptodome(padded, key8, full_cipher)

    _banner("PROSES DEKRIPSI")
    recovered_parts = []
    for block_idx, ct in enumerate(ciphertext_parts):
        print(f"\n--- Dekripsi blok {block_idx + 1} ---")
        show_verbose = verbose_all_blocks or block_idx == 0
        pt_hex = des_decrypt_block(ct, key_hex, verbose=show_verbose)
        recovered_parts.append(pt_hex)
        print(f">> Plaintext blok (HEX): {pt_hex}")

    recovered_bytes = b"".join(bytes.fromhex(h) for h in recovered_parts)
    unpadded = pkcs7_unpad(recovered_bytes, 8)
    _banner("HASIL DEKRIPSI AKHIR")
    print(f"  Plaintext (HEX) : {recovered_bytes.hex().upper()}")
    print(f"  Plaintext (ASCII setelah unpad): {unpadded.decode('utf-8')!r}")
    print(f"  Round-trip OK   : {unpadded.decode('utf-8') == plaintext}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Demo DES untuk laporan tugas.")
    parser.add_argument("--plaintext", default="KHAIRULUMAM", help="Plaintext ASCII.")
    parser.add_argument("--key", default="KAMPUSUMM", help="Key ASCII (8 byte efektif).")
    parser.add_argument(
        "--all-blocks-verbose",
        action="store_true",
        help="Tampilkan detail ronde untuk semua blok (output sangat panjang).",
    )
    args = parser.parse_args()
    run_demo(args.plaintext, args.key, verbose_all_blocks=args.all_blocks_verbose)


if __name__ == "__main__":
    main()
