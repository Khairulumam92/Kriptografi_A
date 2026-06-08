import io
import time
import math
import base64
from PIL import Image


def lsb_encode(image_bytes: bytes, message: str) -> dict:
    t_start = time.perf_counter()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pixels = img.load()
    w, h = img.size
    max_capacity = (w * h * 3) - 32

    msg_bytes = message.encode("utf-8")
    msg_len = len(msg_bytes)

    if msg_len * 8 > max_capacity:
        raise ValueError(
            f"Pesan terlalu panjang. Kapasitas maksimal: {max_capacity // 8} karakter. "
            f"Pesan Anda: {msg_len} karakter."
        )

    length_prefix = msg_len.to_bytes(4, "big")
    payload = length_prefix + msg_bytes
    bits = "".join(f"{b:08b}" for b in payload)

    idx = 0
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            if idx < len(bits):
                r = (r & 0xFE) | int(bits[idx])
                idx += 1
            if idx < len(bits):
                g = (g & 0xFE) | int(bits[idx])
                idx += 1
            if idx < len(bits):
                b = (b & 0xFE) | int(bits[idx])
                idx += 1
            pixels[x, y] = (r, g, b)
            if idx >= len(bits):
                break
        if idx >= len(bits):
            break

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    t_end = time.perf_counter()

    return {
        "stego_bytes": buf.getvalue(),
        "capacity_total_bits": max_capacity,
        "capacity_used_bits": len(bits),
        "capacity_used_pct": round(len(bits) / max_capacity * 100, 4),
        "encode_time_ms": round((t_end - t_start) * 1000, 2),
    }


def lsb_decode(image_bytes: bytes) -> dict:
    t_start = time.perf_counter()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pixels = img.load()
    w, h = img.size

    bits = []
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            bits.append(str(r & 1))
            bits.append(str(g & 1))
            bits.append(str(b & 1))

    bit_str = "".join(bits)
    length_bits = bit_str[:32]
    msg_len = int(length_bits, 2)

    if msg_len < 0 or msg_len > (w * h * 3) // 8:
        raise ValueError("Gambar tidak mengandung pesan tersembunyi atau format tidak dikenali.")

    msg_bits = bit_str[32 : 32 + msg_len * 8]
    msg_bytes = bytes(int(msg_bits[i : i + 8], 2) for i in range(0, len(msg_bits), 8))
    message = msg_bytes.decode("utf-8")
    t_end = time.perf_counter()

    return {
        "message": message,
        "char_count": len(message),
        "decode_time_ms": round((t_end - t_start) * 1000, 2),
    }


def compare_images(original_bytes: bytes, stego_bytes: bytes) -> bytes:
    orig = Image.open(io.BytesIO(original_bytes)).convert("RGB")
    stego = Image.open(io.BytesIO(stego_bytes)).convert("RGB")

    if orig.size != stego.size:
        stego = stego.resize(orig.size)

    orig_px = orig.load()
    stego_px = stego.load()
    diff = Image.new("RGB", orig.size)
    diff_px = diff.load()
    w, h = orig.size

    changed = 0
    total = w * h * 3

    for y in range(h):
        for x in range(w):
            ro, go, bo = orig_px[x, y]
            rs, gs, bs = stego_px[x, y]
            dr = abs(ro - rs)
            dg = abs(go - gs)
            db = abs(bo - bs)
            if dr > 0 or dg > 0 or db > 0:
                changed += 1
            diff_px[x, y] = (dr * 255, dg * 255, db * 255)

    buf = io.BytesIO()
    diff.save(buf, format="PNG")

    return buf.getvalue(), changed, total


def calculate_mse(original_bytes: bytes, stego_bytes: bytes) -> float:
    orig = Image.open(io.BytesIO(original_bytes)).convert("RGB")
    stego = Image.open(io.BytesIO(stego_bytes)).convert("RGB")

    if orig.size != stego.size:
        stego = stego.resize(orig.size)

    orig_px = orig.load()
    stego_px = stego.load()
    w, h = orig.size

    total = 0
    count = w * h * 3
    for y in range(h):
        for x in range(w):
            ro, go, bo = orig_px[x, y]
            rs, gs, bs = stego_px[x, y]
            total += (ro - rs) ** 2 + (go - gs) ** 2 + (bo - bs) ** 2

    mse = total / count
    return mse


def calculate_psnr(mse: float) -> float:
    if mse == 0:
        return float("inf")
    return round(10 * math.log10((255 ** 2) / mse), 2)


def image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")
