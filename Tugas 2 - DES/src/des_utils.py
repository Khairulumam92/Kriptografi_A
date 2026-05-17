"""
Utility helpers for block processing and text/hex conversion.
"""

from __future__ import annotations

import re
from typing import List

HEX_RE = re.compile(r"^[0-9a-fA-F]+$")


def text_to_hex(text: str) -> str:
    return text.encode("utf-8").hex().upper()


def hex_to_text(hex_data: str) -> str:
    return bytes.fromhex(hex_data).decode("utf-8")


def chunk_hex_16(hex_data: str) -> List[str]:
    if len(hex_data) % 16 != 0:
        raise ValueError("Panjang data hex harus kelipatan 16 karakter.")
    return [hex_data[i:i + 16] for i in range(0, len(hex_data), 16)]


def pkcs7_pad(data: bytes, block_size: int = 8) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    if pad_len == 0:
        pad_len = block_size
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes, block_size: int = 8) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("Data padding tidak valid.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Nilai padding tidak valid.")
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        raise ValueError("Pola padding tidak valid.")
    return data[:-pad_len]


def text_to_padded_hex_blocks(text: str) -> List[str]:
    padded = pkcs7_pad(text.encode("utf-8"), 8)
    return [block.hex().upper() for block in [padded[i:i + 8] for i in range(0, len(padded), 8)]]


def hex_blocks_to_unpadded_text(blocks: List[str]) -> str:
    data = b"".join(bytes.fromhex(block) for block in blocks)
    return pkcs7_unpad(data, 8).decode("utf-8")


def validate_hex_data(value: str, label: str = "Data") -> str:
    cleaned = value.strip().replace(" ", "")
    if len(cleaned) == 0 or len(cleaned) % 2 != 0 or not HEX_RE.fullmatch(cleaned):
        raise ValueError(f"{label} harus heksadesimal valid dengan panjang genap.")
    return cleaned.upper()


def text_key_to_bytes(key_text: str) -> bytes:
    """
    Ubah kunci ASCII menjadi 8 byte (64-bit) untuk DES.

    - Jika panjang <= 8 byte: padding NUL (0x00) di kanan.
    - Jika panjang > 8 byte: ambil 8 byte pertama (sesuai contoh KAMPUSUMM -> KAMPUSUM).
    """
    raw = key_text.encode("utf-8")
    if len(raw) > 8:
        return raw[:8]
    return raw.ljust(8, b"\x00")


def text_key_to_hex_64(key_text: str) -> str:
    """Kunci ASCII menjadi 16 karakter hex (64-bit)."""
    return text_key_to_bytes(key_text).hex().upper()


def bytes_to_binary_groups(data: bytes, group: int = 8) -> str:
    """Format byte menjadi string biner per grup (mis. per byte)."""
    bits = "".join(format(b, "08b") for b in data)
    return " ".join(bits[i : i + group] for i in range(0, len(bits), group))
