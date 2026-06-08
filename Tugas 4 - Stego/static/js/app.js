document.addEventListener("DOMContentLoaded", function () {
    // ── TAB SWITCHING ──
    document.querySelectorAll(".tab-btn").forEach(function (btn) {
        btn.addEventListener("click", function () {
            document.querySelectorAll(".tab-btn").forEach(function (b) { b.classList.remove("active"); });
            document.querySelectorAll(".tab-content").forEach(function (c) { c.classList.remove("active"); });
            btn.classList.add("active");
            document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
        });
    });

    // ── ENCODE TAB ──
    var encodeFile = document.getElementById("encode-file");
    var encodeDropzone = document.getElementById("encode-dropzone");
    var encodeFilename = document.getElementById("encode-filename");
    var encodeMessage = document.getElementById("encode-message");
    var encodeBtn = document.getElementById("encode-btn");
    var encodeLoader = document.getElementById("encode-loader");
    var encodeError = document.getElementById("encode-error");
    var charCount = document.getElementById("char-count");
    var resultSection = document.getElementById("result-section");
    var encodeFileSelected = false;

    function updateEncodeButton() {
        encodeBtn.disabled = !(encodeFileSelected && encodeMessage.value.trim().length > 0);
    }

    function handleEncodeFile(files) {
        if (files.length > 0) {
            encodeFilename.textContent = files[0].name + " (" + formatBytes(files[0].size) + ")";
            encodeFileSelected = true;
        }
        updateEncodeButton();
    }

    encodeFile.addEventListener("change", function () {
        handleEncodeFile(this.files);
    });

    encodeDropzone.addEventListener("dragover", function (e) {
        e.preventDefault();
        this.classList.add("drag-over");
    });

    encodeDropzone.addEventListener("dragleave", function () {
        this.classList.remove("drag-over");
    });

    encodeDropzone.addEventListener("drop", function (e) {
        e.preventDefault();
        this.classList.remove("drag-over");
        if (e.dataTransfer.files.length > 0) {
            encodeFile.files = e.dataTransfer.files;
            handleEncodeFile(e.dataTransfer.files);
        }
    });

    encodeDropzone.addEventListener("click", function (e) {
        if (e.target !== encodeFile) {
            encodeFile.click();
        }
    });

    encodeMessage.addEventListener("input", function () {
        charCount.textContent = this.value.length;
        updateEncodeButton();
    });

    encodeBtn.addEventListener("click", function () {
        encodeError.classList.remove("active");
        resultSection.style.display = "none";
        encodeBtn.style.display = "none";
        encodeLoader.classList.add("active");

        var formData = new FormData();
        formData.append("image", encodeFile.files[0]);
        formData.append("message", encodeMessage.value);

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/encode");

        xhr.onload = function () {
            encodeLoader.classList.remove("active");
            encodeBtn.style.display = "block";

            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                if (data.success) {
                    showEncodeResult(data);
                } else {
                    showEncodeError(data.error);
                }
            } else {
                try {
                    var err = JSON.parse(xhr.responseText);
                    showEncodeError(err.error || "Terjadi kesalahan server.");
                } catch (e) {
                    showEncodeError("Terjadi kesalahan server (" + xhr.status + ").");
                }
            }
        };

        xhr.onerror = function () {
            encodeLoader.classList.remove("active");
            encodeBtn.style.display = "block";
            showEncodeError("Gagal terhubung ke server.");
        };

        xhr.send(formData);
    });

    function showEncodeResult(data) {
        document.getElementById("orig-img").src = "data:image/png;base64," + data.original_b64;
        document.getElementById("stego-img").src = "data:image/png;base64," + data.stego_b64;
        document.getElementById("diff-img").src = "data:image/png;base64," + data.diff_b64;

        document.getElementById("stat-psnr").textContent = data.stats.psnr_db === "-" ? "\u221E" : data.stats.psnr_db + " dB";
        document.getElementById("stat-mse").textContent = data.stats.mse;
        document.getElementById("stat-changed").textContent = data.stats.changed_pixels + " / " + data.stats.total_pixels;
        document.getElementById("stat-capacity").textContent = data.stats.capacity_used_pct + "%";
        document.getElementById("stat-time").textContent = data.stats.encode_time_ms + " ms";
        document.getElementById("stat-chars").textContent = data.stats.message_chars + " karakter";

        var dl = document.getElementById("download-btn");
        dl.href = "/api/download/" + data.stego_id;
        dl.download = "stego_image.png";

        var range = document.getElementById("compare-range");
        range.value = 50;
        updateClip(50);

        resultSection.style.display = "block";
        resultSection.scrollIntoView({ behavior: "smooth" });
    }

    function showEncodeError(msg) {
        encodeError.textContent = msg;
        encodeError.classList.add("active");
        encodeError.scrollIntoView({ behavior: "smooth" });
    }

    // ── COMPARISON SLIDER ──
    var compareRange = document.getElementById("compare-range");
    function updateClip(val) {
        document.getElementById("stego-img").style.clipPath = "inset(0 0 0 " + val + "%)";
        document.querySelector(".compare-slider").style.left = val + "%";
    }

    compareRange.addEventListener("input", function () {
        updateClip(this.value);
    });

    // ── DECODE TAB ──
    var decodeFile = document.getElementById("decode-file");
    var decodeDropzone = document.getElementById("decode-dropzone");
    var decodeFilename = document.getElementById("decode-filename");
    var decodeBtn = document.getElementById("decode-btn");
    var decodeLoader = document.getElementById("decode-loader");
    var decodeError = document.getElementById("decode-error");
    var decodeResult = document.getElementById("decode-result");
    var decodeFileSelected = false;

    function updateDecodeButton() {
        decodeBtn.disabled = !decodeFileSelected;
    }

    function handleDecodeFile(files) {
        if (files.length > 0) {
            decodeFilename.textContent = files[0].name + " (" + formatBytes(files[0].size) + ")";
            decodeFileSelected = true;
        }
        updateDecodeButton();
    }

    decodeFile.addEventListener("change", function () {
        handleDecodeFile(this.files);
    });

    decodeDropzone.addEventListener("dragover", function (e) {
        e.preventDefault();
        this.classList.add("drag-over");
    });

    decodeDropzone.addEventListener("dragleave", function () {
        this.classList.remove("drag-over");
    });

    decodeDropzone.addEventListener("drop", function (e) {
        e.preventDefault();
        this.classList.remove("drag-over");
        if (e.dataTransfer.files.length > 0) {
            decodeFile.files = e.dataTransfer.files;
            handleDecodeFile(e.dataTransfer.files);
        }
    });

    decodeDropzone.addEventListener("click", function (e) {
        if (e.target !== decodeFile) {
            decodeFile.click();
        }
    });

    decodeBtn.addEventListener("click", function () {
        decodeError.classList.remove("active");
        decodeResult.style.display = "none";
        decodeBtn.style.display = "none";
        decodeLoader.classList.add("active");

        var formData = new FormData();
        formData.append("image", decodeFile.files[0]);

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/decode");

        xhr.onload = function () {
            decodeLoader.classList.remove("active");
            decodeBtn.style.display = "block";

            if (xhr.status === 200) {
                var data = JSON.parse(xhr.responseText);
                if (data.success) {
                    showDecodeResult(data);
                } else {
                    showDecodeError(data.error);
                }
            } else {
                try {
                    var err = JSON.parse(xhr.responseText);
                    showDecodeError(err.error || "Terjadi kesalahan server.");
                } catch (e) {
                    showDecodeError("Terjadi kesalahan server (" + xhr.status + ").");
                }
            }
        };

        xhr.onerror = function () {
            decodeLoader.classList.remove("active");
            decodeBtn.style.display = "block";
            showDecodeError("Gagal terhubung ke server.");
        };

        xhr.send(formData);
    });

    function showDecodeResult(data) {
        document.getElementById("decoded-message").textContent = data.message;
        document.getElementById("decode-chars").textContent = data.char_count + " karakter";
        document.getElementById("decode-time").textContent = data.decode_time_ms + " ms";
        decodeResult.style.display = "block";
        decodeResult.scrollIntoView({ behavior: "smooth" });
    }

    function showDecodeError(msg) {
        decodeError.textContent = msg;
        decodeError.classList.add("active");
        decodeError.scrollIntoView({ behavior: "smooth" });
    }

    // ── UTILS ──
    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / 1048576).toFixed(1) + " MB";
    }
});
