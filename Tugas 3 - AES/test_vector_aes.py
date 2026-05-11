"""
Validasi AES manual terhadap library AES (hanya sebagai pembanding akhir).
"""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.aes_core import aes_decrypt_block, aes_encrypt_block
from src.aes_utils import bytes_to_hex, key_to_block, pkcs7_unpad, text_to_block


def validate_against_library() -> None:
    plaintext = "MOH KHAIRUL UMAM"
    key_text = "KAMPUSUMM"

    plain_block = text_to_block(plaintext)
    key_block = key_to_block(key_text)

    manual_cipher, _ = aes_encrypt_block(plain_block, key_block, collect_trace=False)
    manual_plain, _ = aes_decrypt_block(manual_cipher, key_block, collect_trace=False)
    manual_plain = pkcs7_unpad(manual_plain)

    try:
        from Crypto.Cipher import AES  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "Modul pycryptodome belum terpasang. Install dengan: pip install pycryptodome"
        ) from exc

    aes_lib = AES.new(key_block, AES.MODE_ECB)
    lib_cipher = aes_lib.encrypt(plain_block)
    lib_plain = aes_lib.decrypt(lib_cipher)
    lib_plain = pkcs7_unpad(lib_plain)

    print("=== VALIDASI AES MANUAL VS LIBRARY ===")
    print(f"Plaintext block:     {bytes_to_hex(plain_block)}")
    print(f"Key block:           {bytes_to_hex(key_block)}")
    print(f"Cipher manual:       {bytes_to_hex(manual_cipher)}")
    print(f"Cipher library:      {bytes_to_hex(lib_cipher)}")
    print(f"Plain manual decode: {manual_plain.decode('utf-8', errors='replace')}")
    print(f"Plain library decode:{lib_plain.decode('utf-8', errors='replace')}")

    assert manual_cipher == lib_cipher, "Ciphertext manual tidak sama dengan library AES."
    assert manual_plain == lib_plain, "Plaintext dekripsi manual tidak sama dengan library AES."
    print("Status: VALID (hasil manual sesuai library).")


if __name__ == "__main__":
    validate_against_library()
