"""
Utility helpers for AES demo output and data preparation.
"""

from __future__ import annotations

from typing import List

from .aes_core import State


def pad_to_16_pkcs7_if_needed(data: bytes) -> bytes:
    """
    Pad data to 16 bytes using PKCS#7 only when length < 16.
    """
    if len(data) > 16:
        raise ValueError("Data melebihi 16 byte. Demo ini hanya untuk satu blok AES.")
    if len(data) == 16:
        return data
    pad_len = 16 - len(data)
    return data + bytes([pad_len] * pad_len)


def pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    if not data:
        raise ValueError("Data kosong tidak bisa di-unpad.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        return data
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        return data
    return data[:-pad_len]


def text_to_block(text: str) -> bytes:
    return pad_to_16_pkcs7_if_needed(text.encode("utf-8"))


def key_to_block(key_text: str) -> bytes:
    return pad_to_16_pkcs7_if_needed(key_text.encode("utf-8"))


def bytes_to_hex(data: bytes) -> str:
    return "".join(f"{byte:02x}" for byte in data)


def bytes_to_spaced_hex(data: bytes) -> str:
    return " ".join(f"{byte:02x}" for byte in data)


def format_state_matrix(state: State) -> str:
    lines: List[str] = []
    for row in range(4):
        lines.append(" ".join(f"{state[row][col]:02x}" for col in range(4)))
    return "\n".join(lines)


def safe_decode_text(data: bytes) -> str:
    return data.decode("utf-8", errors="replace")
