"""
Implementasi inti algoritma DES (Data Encryption Standard) — manual.

DES standar:
  - Blok data 64-bit
  - Kunci input 64-bit (56-bit efektif setelah PC-1)
  - 16 ronde jaringan Feistel

Fungsi utama diekspos dengan nama yang sesuai materi kuliah kriptografi.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from . import des_verbose as verbose_out

# ---------------------------------------------------------------------------
# Tabel permutasi dan S-Box standar FIPS-46 (DES)
# ---------------------------------------------------------------------------

IP = [
    58, 50, 42, 34, 26, 18, 10, 2,
    60, 52, 44, 36, 28, 20, 12, 4,
    62, 54, 46, 38, 30, 22, 14, 6,
    64, 56, 48, 40, 32, 24, 16, 8,
    57, 49, 41, 33, 25, 17, 9, 1,
    59, 51, 43, 35, 27, 19, 11, 3,
    61, 53, 45, 37, 29, 21, 13, 5,
    63, 55, 47, 39, 31, 23, 15, 7,
]

FP = [
    40, 8, 48, 16, 56, 24, 64, 32,
    39, 7, 47, 15, 55, 23, 63, 31,
    38, 6, 46, 14, 54, 22, 62, 30,
    37, 5, 45, 13, 53, 21, 61, 29,
    36, 4, 44, 12, 52, 20, 60, 28,
    35, 3, 43, 11, 51, 19, 59, 27,
    34, 2, 42, 10, 50, 18, 58, 26,
    33, 1, 41, 9, 49, 17, 57, 25,
]

E = [
    32, 1, 2, 3, 4, 5,
    4, 5, 6, 7, 8, 9,
    8, 9, 10, 11, 12, 13,
    12, 13, 14, 15, 16, 17,
    16, 17, 18, 19, 20, 21,
    20, 21, 22, 23, 24, 25,
    24, 25, 26, 27, 28, 29,
    28, 29, 30, 31, 32, 1,
]

P = [
    16, 7, 20, 21,
    29, 12, 28, 17,
    1, 15, 23, 26,
    5, 18, 31, 10,
    2, 8, 24, 14,
    32, 27, 3, 9,
    19, 13, 30, 6,
    22, 11, 4, 25,
]

PC1 = [
    57, 49, 41, 33, 25, 17, 9,
    1, 58, 50, 42, 34, 26, 18,
    10, 2, 59, 51, 43, 35, 27,
    19, 11, 3, 60, 52, 44, 36,
    63, 55, 47, 39, 31, 23, 15,
    7, 62, 54, 46, 38, 30, 22,
    14, 6, 61, 53, 45, 37, 29,
    21, 13, 5, 28, 20, 12, 4,
]

PC2 = [
    14, 17, 11, 24, 1, 5,
    3, 28, 15, 6, 21, 10,
    23, 19, 12, 4, 26, 8,
    16, 7, 27, 20, 13, 2,
    41, 52, 31, 37, 47, 55,
    30, 40, 51, 45, 33, 48,
    44, 49, 39, 56, 34, 53,
    46, 42, 50, 36, 29, 32,
]

SHIFT_SCHEDULE = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]

S_BOX = [
    [
        [14, 4, 13, 1, 2, 15, 11, 8, 3, 10, 6, 12, 5, 9, 0, 7],
        [0, 15, 7, 4, 14, 2, 13, 1, 10, 6, 12, 11, 9, 5, 3, 8],
        [4, 1, 14, 8, 13, 6, 2, 11, 15, 12, 9, 7, 3, 10, 5, 0],
        [15, 12, 8, 2, 4, 9, 1, 7, 5, 11, 3, 14, 10, 0, 6, 13],
    ],
    [
        [15, 1, 8, 14, 6, 11, 3, 4, 9, 7, 2, 13, 12, 0, 5, 10],
        [3, 13, 4, 7, 15, 2, 8, 14, 12, 0, 1, 10, 6, 9, 11, 5],
        [0, 14, 7, 11, 10, 4, 13, 1, 5, 8, 12, 6, 9, 3, 2, 15],
        [13, 8, 10, 1, 3, 15, 4, 2, 11, 6, 7, 12, 0, 5, 14, 9],
    ],
    [
        [10, 0, 9, 14, 6, 3, 15, 5, 1, 13, 12, 7, 11, 4, 2, 8],
        [13, 7, 0, 9, 3, 4, 6, 10, 2, 8, 5, 14, 12, 11, 15, 1],
        [13, 6, 4, 9, 8, 15, 3, 0, 11, 1, 2, 12, 5, 10, 14, 7],
        [1, 10, 13, 0, 6, 9, 8, 7, 4, 15, 14, 3, 11, 5, 2, 12],
    ],
    [
        [7, 13, 14, 3, 0, 6, 9, 10, 1, 2, 8, 5, 11, 12, 4, 15],
        [13, 8, 11, 5, 6, 15, 0, 3, 4, 7, 2, 12, 1, 10, 14, 9],
        [10, 6, 9, 0, 12, 11, 7, 13, 15, 1, 3, 14, 5, 2, 8, 4],
        [3, 15, 0, 6, 10, 1, 13, 8, 9, 4, 5, 11, 12, 7, 2, 14],
    ],
    [
        [2, 12, 4, 1, 7, 10, 11, 6, 8, 5, 3, 15, 13, 0, 14, 9],
        [14, 11, 2, 12, 4, 7, 13, 1, 5, 0, 15, 10, 3, 9, 8, 6],
        [4, 2, 1, 11, 10, 13, 7, 8, 15, 9, 12, 5, 6, 3, 0, 14],
        [11, 8, 12, 7, 1, 14, 2, 13, 6, 15, 0, 9, 10, 4, 5, 3],
    ],
    [
        [12, 1, 10, 15, 9, 2, 6, 8, 0, 13, 3, 4, 14, 7, 5, 11],
        [10, 15, 4, 2, 7, 12, 9, 5, 6, 1, 13, 14, 0, 11, 3, 8],
        [9, 14, 15, 5, 2, 8, 12, 3, 7, 0, 4, 10, 1, 13, 11, 6],
        [4, 3, 2, 12, 9, 5, 15, 10, 11, 14, 1, 7, 6, 0, 8, 13],
    ],
    [
        [4, 11, 2, 14, 15, 0, 8, 13, 3, 12, 9, 7, 5, 10, 6, 1],
        [13, 0, 11, 7, 4, 9, 1, 10, 14, 3, 5, 12, 2, 15, 8, 6],
        [1, 4, 11, 13, 12, 3, 7, 14, 10, 15, 6, 8, 0, 5, 9, 2],
        [6, 11, 13, 8, 1, 4, 10, 7, 9, 5, 0, 15, 14, 2, 3, 12],
    ],
    [
        [13, 2, 8, 4, 6, 15, 11, 1, 10, 9, 3, 14, 5, 0, 12, 7],
        [1, 15, 13, 8, 10, 3, 7, 4, 12, 5, 6, 11, 0, 14, 9, 2],
        [7, 11, 4, 1, 9, 12, 14, 2, 0, 6, 10, 13, 15, 3, 5, 8],
        [2, 1, 14, 7, 4, 10, 8, 13, 15, 12, 9, 0, 3, 5, 6, 11],
    ],
]

HEX_64_RE = re.compile(r"^[0-9a-fA-F]{16}$")


# ---------------------------------------------------------------------------
# Utilitas bit / hex
# ---------------------------------------------------------------------------

def permute(bits: str, table: List[int]) -> str:
    """Permutasi generik: ambil bit pada posisi tabel (1-indeks)."""
    return "".join(bits[pos - 1] for pos in table)


def initial_permutation(bits64: str) -> str:
    """Initial Permutation (IP) — mengacak 64-bit masukan sebelum ronde Feistel."""
    return permute(bits64, IP)


def final_permutation(bits64: str) -> str:
    """Final Permutation (FP) — invers IP setelah 16 ronde."""
    return permute(bits64, FP)


def expansion_permutation(bits32: str) -> str:
    """Expansion Permutation (E) — memperluas 32-bit menjadi 48-bit."""
    return permute(bits32, E)


def pbox_permutation(bits32: str) -> str:
    """P-Box Permutation (P) — menyebarkan bit hasil S-Box."""
    return permute(bits32, P)


def xor_bits(a: str, b: str) -> str:
    """XOR bitwise dua string biner dengan panjang sama."""
    return "".join("1" if x != y else "0" for x, y in zip(a, b))


def left_shift(bits: str, shift: int) -> str:
    """Left circular shift pada string biner."""
    return bits[shift:] + bits[:shift]


def hex_to_bits(hex_str: str) -> str:
    """Konversi string heksadesimal ke biner (tanpa prefix 0b)."""
    return bin(int(hex_str, 16))[2:].zfill(len(hex_str) * 4)


def bits_to_hex(bits: str) -> str:
    """Konversi biner ke heksadesimal huruf besar."""
    return format(int(bits, 2), f"0{len(bits) // 4}X")


def validate_hex_64(value: str, label: str) -> str:
    if not HEX_64_RE.fullmatch(value):
        raise ValueError(f"{label} harus 16 karakter heksadesimal (64-bit).")
    return value.upper()


# ---------------------------------------------------------------------------
# S-Box, fungsi f, key schedule
# ---------------------------------------------------------------------------

def sbox_substitute(bits48: str) -> str:
    """
  S-Box Substitution — 48-bit dibagi 8 x 6-bit.
  Bit luar (b1, b6) = baris; bit tengah (b2..b5) = kolom.
  Keluaran: 8 x 4-bit = 32-bit.
    """
    chunks = [bits48[i : i + 6] for i in range(0, 48, 6)]
    out = []
    for i, chunk in enumerate(chunks):
        row = int(chunk[0] + chunk[5], 2)
        col = int(chunk[1:5], 2)
        out.append(format(S_BOX[i][row][col], "04b"))
    return "".join(out)


def f_function(right32: str, subkey48: str) -> Tuple[str, str, str, str, str]:
    """
    Fungsi f pada ronde Feistel: E -> XOR K -> S-Box -> P.
    Mengembalikan (expanded, xored, sbox_out, pbox_out) untuk pelacakan verbose.
    """
    expanded = expansion_permutation(right32)
    xored = xor_bits(expanded, subkey48)
    substituted = sbox_substitute(xored)
    permuted = pbox_permutation(substituted)
    return expanded, xored, substituted, permuted


def key_schedule(key_hex_64: str, verbose: bool = False) -> List[str]:
    """
    Key Schedule — menghasilkan 16 subkey 48-bit dari kunci 64-bit.
    Tahapan: PC-1 -> bagi C0|D0 -> left shift per ronde -> PC-2.
    """
    key_hex_64 = validate_hex_64(key_hex_64, "Key")
    key56 = permute(hex_to_bits(key_hex_64), PC1)
    c, d = key56[:28], key56[28:]
    subkeys: List[str] = []

    if verbose:
        verbose_out.separator("KEY SCHEDULE")
        verbose_out.print_bits_block("Kunci 64-bit (masukan)", hex_to_bits(key_hex_64), indent=2)
        verbose_out.print_bits_block("Setelah PC-1 (56-bit efektif)", key56, indent=2)
        verbose_out.print_bits_block("C0", c, indent=2)
        verbose_out.print_bits_block("D0", d, indent=2)

    for rnd, shift in enumerate(SHIFT_SCHEDULE, start=1):
        c = left_shift(c, shift)
        d = left_shift(d, shift)
        subkey = permute(c + d, PC2)
        subkeys.append(subkey)
        if verbose:
            print(f"\n  Ronde {rnd:02d}: shift={shift}")
            verbose_out.print_bits_block(f"C{rnd}", c, indent=4)
            verbose_out.print_bits_block(f"D{rnd}", d, indent=4)
            verbose_out.print_bits_block(f"K{rnd} (subkey)", subkey, indent=4)

    return subkeys


# Alias nama fungsi sesuai spesifikasi tugas
generate_subkeys = key_schedule


def _des_block_bits(
    data64_bits: str,
    subkeys: List[str],
    verbose: bool = False,
    decrypt_mode: bool = False,
) -> str:
    """Proses satu blok 64-bit (enkripsi atau dekripsi)."""
    if verbose:
        mode_label = "DEKRIPSI" if decrypt_mode else "ENKRIPSI"
        verbose_out.separator(f"PROSES DES — {mode_label} (SATU BLOK 64-bit)")

    permuted = initial_permutation(data64_bits)
    left, right = permuted[:32], permuted[32:]

    if verbose:
        verbose_out.print_bits_block("Blok masukan (64-bit)", data64_bits, indent=2)
        verbose_out.separator("INITIAL PERMUTATION (IP)")
        verbose_out.print_bits_block("Hasil IP", permuted, indent=2)
        verbose_out.print_bits_block("L0", left, indent=2)
        verbose_out.print_bits_block("R0", right, indent=2)

    for index, subkey in enumerate(subkeys, start=1):
        expanded, xored, sbox32, f_out = f_function(right, subkey)
        new_right = xor_bits(left, f_out)
        new_left = right

        if verbose:
            verbose_out.print_feistel_step(
                index,
                right,
                subkey,
                expanded,
                xored,
                sbox32,
                f_out,
                left,
                new_left,
                new_right,
            )

        left, right = new_left, new_right

    pre_output = right + left
    final_bits = final_permutation(pre_output)

    if verbose:
        verbose_out.separator("FINAL SWAP & FINAL PERMUTATION")
        verbose_out.print_bits_block("R16 || L16 (sebelum FP)", pre_output, indent=2)
        verbose_out.print_bits_block("Ciphertext / plaintext blok (setelah FP)", final_bits, indent=2)

    return final_bits


def des_encrypt_block(block64: str, key64: str, verbose: bool = False) -> str:
    """DES Encrypt — satu blok 16 karakter hex."""
    block64 = validate_hex_64(block64, "Plaintext block")
    subkeys = key_schedule(key64, verbose=verbose)
    return bits_to_hex(_des_block_bits(hex_to_bits(block64), subkeys, verbose, False))


def des_decrypt_block(block64: str, key64: str, verbose: bool = False) -> str:
    """DES Decrypt — subkey dipakai terbalik (K16..K1)."""
    block64 = validate_hex_64(block64, "Ciphertext block")
    subkeys_forward = key_schedule(key64, verbose=False)
    subkeys = list(reversed(subkeys_forward))
    if verbose:
        verbose_out.separator("DEKRIPSI — Urutan Subkey Terbalik (K16 .. K1)")
        for i, sk in enumerate(subkeys, start=1):
            orig = 17 - i
            print(f"  Langkah {i:02d} memakai K{orig:02d}: HEX={bits_to_hex(sk)}")
    return bits_to_hex(_des_block_bits(hex_to_bits(block64), subkeys, verbose, True))
