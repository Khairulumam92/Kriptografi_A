"""
Formatter output verbose untuk demonstrasi proses DES per ronde.
Digunakan saat presentasi dan dokumentasi laporan praktikum.
"""

from __future__ import annotations

from typing import List, Optional


def separator(title: str = "", width: int = 78) -> None:
    if title:
        print(f"\n{'=' * width}")
        print(title.center(width))
        print("=" * width)
    else:
        print("-" * width)


def print_bits_block(label: str, bits: str, indent: int = 0) -> None:
    """Tampilkan label, representasi biner, dan heksadesimal."""
    prefix = " " * indent
    hex_val = _bits_to_hex(bits)
    print(f"{prefix}{label}")
    print(f"{prefix}  BIN : {bits}")
    print(f"{prefix}  HEX : {hex_val}")


def print_sbox_detail(bits48: str, bits32: str, indent: int = 4) -> None:
    """Tampilkan masukan/keluaran tiap S-Box (8 buah, 6-bit -> 4-bit)."""
    prefix = " " * indent
    print(f"{prefix}Masukan 48-bit (8 x 6-bit):")
    for i in range(8):
        chunk = bits48[i * 6 : (i + 1) * 6]
        row = int(chunk[0] + chunk[5], 2)
        col = int(chunk[1:5], 2)
        out4 = bits32[i * 4 : (i + 1) * 4]
        print(
            f"{prefix}  S{i + 1}: in={chunk} (row={row}, col={col}) -> out={out4}"
        )


def print_subkeys(subkeys: List[str]) -> None:
    separator("KEY SCHEDULE — 16 SUBKEY (48-bit)")
    for i, sk in enumerate(subkeys, start=1):
        print(f"K{i:02d}  BIN: {sk}")
        print(f"     HEX: {_bits_to_hex(sk)}")


def print_round_header(round_no: int) -> None:
    separator(f"RONDE {round_no:02d}")


def print_feistel_step(
    round_no: int,
    right32: str,
    subkey48: str,
    expanded48: str,
    xored48: str,
    sbox32: str,
    pbox32: str,
    left_prev: str,
    new_left: str,
    new_right: str,
) -> None:
    print_round_header(round_no)
    print_bits_block(f"R{round_no - 1} (masukan fungsi f)", right32, indent=2)
    print_bits_block(f"Subkey K{round_no}", subkey48, indent=2)

    print("\n  [1] Expansion Permutation (E) — 32-bit -> 48-bit")
    print_bits_block("Hasil ekspansi", expanded48, indent=4)

    print("\n  [2] XOR dengan Subkey")
    print_bits_block("Expanded XOR K", xored48, indent=4)

    print("\n  [3] S-Box Substitution — 48-bit -> 32-bit")
    print_sbox_detail(xored48, sbox32, indent=4)
    print_bits_block("Keluaran S-Box", sbox32, indent=4)

    print("\n  [4] P-Box Permutation")
    print_bits_block("Keluaran f(R, K)", pbox32, indent=4)

    print(f"\n  [5] Pembaruan Feistel")
    print(f"    L{round_no} = R{round_no - 1}")
    print_bits_block(f"L{round_no}", new_left, indent=4)
    print(f"    R{round_no} = L{round_no - 1} XOR f(R{round_no - 1}, K{round_no})")
    print_bits_block(f"R{round_no}", new_right, indent=4)


def _bits_to_hex(bits: str) -> str:
    width = max(1, len(bits) // 4)
    return format(int(bits, 2), f"0{width}X")
