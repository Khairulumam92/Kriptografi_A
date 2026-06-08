import os
import uuid

from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename

from app.stego import (
    lsb_encode,
    lsb_decode,
    compare_images,
    calculate_mse,
    calculate_psnr,
    image_to_base64,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/encode", methods=["POST"])
def api_encode():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "File gambar tidak ditemukan."}), 400

    file = request.files["image"]
    message = request.form.get("message", "").strip()

    if not file or file.filename == "":
        return jsonify({"success": False, "error": "File tidak valid."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Format gambar tidak didukung. Gunakan PNG, JPG, BMP, atau GIF."}), 400

    if not message:
        return jsonify({"success": False, "error": "Pesan tidak boleh kosong."}), 400

    try:
        original_bytes = file.read()
        result = lsb_encode(original_bytes, message)

        stego_id = uuid.uuid4().hex[:12]
        stego_path = os.path.join(RESULTS_DIR, f"{stego_id}.png")
        with open(stego_path, "wb") as f:
            f.write(result["stego_bytes"])

        diff_bytes, changed_channels, total_pixels = compare_images(
            original_bytes, result["stego_bytes"]
        )
        mse = calculate_mse(original_bytes, result["stego_bytes"])
        psnr = calculate_psnr(mse)

        return jsonify(
            {
                "success": True,
                "original_b64": image_to_base64(original_bytes),
                "stego_b64": image_to_base64(result["stego_bytes"]),
                "diff_b64": image_to_base64(diff_bytes),
                "stego_id": stego_id,
                "stats": {
                    "psnr_db": psnr if psnr != float("inf") else "-",
                    "mse": round(mse, 6),
                    "changed_pixels": changed_channels,
                    "total_pixels": total_pixels,
                    "capacity_used_pct": result["capacity_used_pct"],
                    "encode_time_ms": result["encode_time_ms"],
                    "message_chars": len(message),
                },
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Gagal memproses: {str(e)}"}), 500


@app.route("/api/decode", methods=["POST"])
def api_decode():
    if "image" not in request.files:
        return jsonify({"success": False, "error": "File gambar tidak ditemukan."}), 400

    file = request.files["image"]

    if not file or file.filename == "":
        return jsonify({"success": False, "error": "File tidak valid."}), 400

    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "Format gambar tidak didukung. Gunakan PNG, JPG, BMP, atau GIF."}), 400

    try:
        image_bytes = file.read()
        result = lsb_decode(image_bytes)

        return jsonify(
            {
                "success": True,
                "message": result["message"],
                "char_count": result["char_count"],
                "decode_time_ms": result["decode_time_ms"],
            }
        )
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400
    except UnicodeDecodeError:
        return jsonify(
            {
                "success": False,
                "error": "Gagal mendekode pesan. Pastikan gambar mengandung pesan LSB yang valid.",
            }
        ), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Gagal memproses: {str(e)}"}), 500


@app.route("/api/download/<stego_id>")
def api_download(stego_id):
    safe_id = secure_filename(stego_id)
    filepath = os.path.join(RESULTS_DIR, f"{safe_id}.png")
    if not os.path.exists(filepath):
        return jsonify({"success": False, "error": "File tidak ditemukan."}), 404
    return send_file(filepath, as_attachment=True, download_name="stego_image.png", mimetype="image/png")
