"""
Terminal program for DES encryption/decryption.

Examples:
  python src/des_cli.py encrypt --input-format hex --data 0123456789ABCDEF --key 133457799BBCDFF1
  python src/des_cli.py decrypt --input-format hex --data 85E813540F0AB405 --key 133457799BBCDFF1
  python src/des_cli.py encrypt --input-format text --data "HELLO DES" --key 133457799BBCDFF1
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from src.des_core import des_decrypt_block, des_encrypt_block, validate_hex_64
    from src.des_utils import (
        chunk_hex_16,
        hex_blocks_to_unpadded_text,
        text_key_to_hex_64,
        text_to_padded_hex_blocks,
        validate_hex_data,
    )
else:
    from .des_core import des_decrypt_block, des_encrypt_block, validate_hex_64
    from .des_utils import (
        chunk_hex_16,
        hex_blocks_to_unpadded_text,
        text_key_to_hex_64,
        text_to_padded_hex_blocks,
        validate_hex_data,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Program DES berbasis terminal.")
    parser.add_argument("mode", choices=["encrypt", "decrypt"], help="Mode operasi.")
    parser.add_argument("--data", required=True, help="Data plaintext/ciphertext.")
    parser.add_argument("--key", required=True, help="Key (hex 16 karakter atau teks ASCII).")
    parser.add_argument(
        "--input-format",
        choices=["hex", "text"],
        default="hex",
        help="Format input data.",
    )
    parser.add_argument(
        "--key-format",
        choices=["hex", "text"],
        default="hex",
        help="Format key: hex (16 char) atau text (ASCII, 8 byte).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Tampilkan proses internal per ronde (hanya blok pertama agar ringkas).",
    )
    return parser.parse_args()


def resolve_key_hex(key: str, key_format: str) -> str:
    if key_format == "text":
        return text_key_to_hex_64(key)
    return validate_hex_64(key, "Key")


def encrypt_data(
    data: str,
    key: str,
    input_format: str,
    verbose: bool,
    key_format: str = "hex",
) -> str:
    key_hex = resolve_key_hex(key, key_format)
    if input_format == "text":
        blocks = text_to_padded_hex_blocks(data)
    else:
        raw_hex = validate_hex_data(data, "Plaintext hex")
        if len(raw_hex) % 16 != 0:
            raise ValueError("Plaintext hex harus kelipatan 16 karakter (64-bit per blok).")
        blocks = chunk_hex_16(raw_hex)

    encrypted_blocks = []
    for idx, block in enumerate(blocks):
        encrypted_blocks.append(des_encrypt_block(block, key_hex, verbose and idx == 0))
    return "".join(encrypted_blocks)


def decrypt_data(
    data: str,
    key: str,
    input_format: str,
    verbose: bool,
    key_format: str = "hex",
) -> str:
    key_hex = resolve_key_hex(key, key_format)
    cipher_hex = validate_hex_data(data, "Ciphertext hex")
    if len(cipher_hex) % 16 != 0:
        raise ValueError("Ciphertext hex harus kelipatan 16 karakter (64-bit per blok).")

    blocks = chunk_hex_16(cipher_hex)
    decrypted_blocks = []
    for idx, block in enumerate(blocks):
        decrypted_blocks.append(des_decrypt_block(block, key_hex, verbose and idx == 0))

    plain_hex = "".join(decrypted_blocks)
    if input_format == "text":
        return hex_blocks_to_unpadded_text(decrypted_blocks)
    return plain_hex


def main() -> None:
    args = parse_args()
    try:
        if args.mode == "encrypt":
            result = encrypt_data(
                args.data, args.key, args.input_format, args.verbose, args.key_format
            )
            print(f"Ciphertext (HEX): {result}")
        else:
            result = decrypt_data(
                args.data, args.key, args.input_format, args.verbose, args.key_format
            )
            if args.input_format == "text":
                print(f"Plaintext (TEXT): {result}")
            else:
                print(f"Plaintext (HEX): {result}")
    except ValueError as exc:
        raise SystemExit(f"Input error: {exc}") from exc


if __name__ == "__main__":
    main()
