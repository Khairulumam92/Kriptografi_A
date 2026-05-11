"""
Program demo AES-128 manual untuk tugas kriptografi.

Default input tugas:
- Plaintext : "MOH KHAIRUL UMAM"
- Key       : "KAMPUSUMM"
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.aes_core import aes_decrypt_block, aes_encrypt_block
    from src.aes_utils import (
        bytes_to_hex,
        bytes_to_spaced_hex,
        format_state_matrix,
        key_to_block,
        pkcs7_unpad,
        safe_decode_text,
        text_to_block,
    )
else:
    from .aes_core import aes_decrypt_block, aes_encrypt_block
    from .aes_utils import (
        bytes_to_hex,
        bytes_to_spaced_hex,
        format_state_matrix,
        key_to_block,
        pkcs7_unpad,
        safe_decode_text,
        text_to_block,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo AES-128 manual (single block, educational).")
    parser.add_argument("--plaintext", default="MOH KHAIRUL UMAM", help="Plaintext input (maksimal 16 karakter UTF-8).")
    parser.add_argument("--key", default="KAMPUSUMM", help="Key input (maksimal 16 karakter UTF-8).")
    return parser.parse_args()


def print_title(title: str) -> None:
    print("\n" + "=" * 78)
    print(title)
    print("=" * 78)


def print_trace(trace_title: str, trace_data: list[tuple[str, list[list[int]]]]) -> None:
    print_title(trace_title)
    for label, state in trace_data:
        print(f"\n{label}:")
        print(format_state_matrix(state))


def main() -> None:
    args = parse_args()

    plaintext_input = args.plaintext
    key_input = args.key

    plaintext_block = text_to_block(plaintext_input)
    key_block = key_to_block(key_input)

    print_title("INPUT DATA")
    print(f"Plaintext (ASCII): {plaintext_input}")
    print(f"Key (ASCII):       {key_input}")
    print(f"Plaintext (HEX):   {bytes_to_spaced_hex(plaintext_block)}")
    print(f"Key (HEX):         {bytes_to_spaced_hex(key_block)}")
    print("\nCatatan padding:")
    print("- Jika panjang < 16 byte, sistem menambahkan PKCS#7 hingga 16 byte.")
    print("- Jika panjang = 16 byte, data dipakai langsung sebagai satu blok AES.")

    ciphertext, encrypt_trace = aes_encrypt_block(plaintext_block, key_block, collect_trace=True)
    print_trace("PROSES ENKRIPSI AES-128 (10 ROUND)", encrypt_trace)

    print_title("HASIL ENKRIPSI")
    print(f"Ciphertext (HEX, tanpa spasi): {bytes_to_hex(ciphertext)}")
    print(f"Ciphertext (HEX, ber-spasi):   {bytes_to_spaced_hex(ciphertext)}")

    recovered_plain_block, decrypt_trace = aes_decrypt_block(ciphertext, key_block, collect_trace=True)
    print_trace("PROSES DEKRIPSI AES-128", decrypt_trace)

    unpadded_plaintext = pkcs7_unpad(recovered_plain_block)
    decoded_plaintext = safe_decode_text(unpadded_plaintext)

    print_title("HASIL DEKRIPSI")
    print(f"Recovered Plaintext (HEX):   {bytes_to_spaced_hex(recovered_plain_block)}")
    print(f"Recovered Plaintext (TEXT):  {decoded_plaintext}")
    print(f"Status Round-Trip:           {'VALID' if decoded_plaintext == plaintext_input else 'TIDAK VALID'}")


if __name__ == "__main__":
    main()
