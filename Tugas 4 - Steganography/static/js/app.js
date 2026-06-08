(function () {
    "use strict";

    // ── DOM REFERENCES ──
    var tabButtons = document.querySelectorAll(".tab-btn");
    var tabIndicator = document.querySelector(".tab-indicator");
    var tabContents = document.querySelectorAll(".tab-content");

    var encodeFile = document.getElementById("encode-file");
    var encodeDropzone = document.getElementById("encode-dropzone");
    var encodeFilename = document.getElementById("encode-filename");
    var encodeMessage = document.getElementById("encode-message");
    var encodeBtn = document.getElementById("encode-btn");
    var encodeLoader = document.getElementById("encode-loader");
    var encodeError = document.getElementById("encode-error");
    var charCount = document.getElementById("char-count");
    var maxChars = document.getElementById("max-chars");
    var resultSection = document.getElementById("result-section");
    var statsGrid = document.getElementById("stats-grid");

    var decodeFile = document.getElementById("decode-file");
    var decodeDropzone = document.getElementById("decode-dropzone");
    var decodeFilename = document.getElementById("decode-filename");
    var decodeBtn = document.getElementById("decode-btn");
    var decodeLoader = document.getElementById("decode-loader");
    var decodeError = document.getElementById("decode-error");
    var decodeResult = document.getElementById("decode-result");

    var compareRange = document.getElementById("compare-range");
    var compareHandle = document.getElementById("compare-handle");
    var steganographyImg = document.getElementById("steganography-img");

    var encodeFileSelected = false;
    var decodeFileSelected = false;

    // ── TAB SWITCHING ──
    function moveIndicator(btn) {
        if (!tabIndicator) return;
        tabIndicator.classList.toggle("right", btn.dataset.tab === "decode");
    }

    tabButtons.forEach(function (btn) {
        btn.addEventListener("click", function () {
            tabButtons.forEach(function (b) { b.classList.remove("active"); });
            tabContents.forEach(function (c) { c.classList.remove("active"); });
            btn.classList.add("active");
            document.getElementById("tab-" + btn.dataset.tab).classList.add("active");
            moveIndicator(btn);
        });
    });

    moveIndicator(document.querySelector(".tab-btn.active"));

    // ── UTILITY ──
    function formatBytes(bytes) {
        if (bytes < 1024) return bytes + " B";
        if (bytes < 1048576) return (bytes / 1024).toFixed(1) + " KB";
        return (bytes / 1048576).toFixed(1) + " MB";
    }

    function showError(el, msg) {
        el.textContent = msg;
        el.classList.add("active");
        el.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }

    function hideError(el) {
        el.classList.remove("active");
    }

    function setLoading(btn, loader, isLoading) {
        btn.style.display = isLoading ? "none" : "";
        loader.classList.toggle("active", isLoading);
    }

    // ── DROP ZONE LOGIC ──
    function setupDropZone(dz, fileInput, filenameEl, onFileSelected) {
        dz.addEventListener("dragover", function (e) {
            e.preventDefault();
            dz.classList.add("drag-over");
        });

        dz.addEventListener("dragleave", function () {
            dz.classList.remove("drag-over");
        });

        dz.addEventListener("drop", function (e) {
            e.preventDefault();
            dz.classList.remove("drag-over");
            if (e.dataTransfer.files.length > 0) {
                fileInput.files = e.dataTransfer.files;
                var f = e.dataTransfer.files[0];
                filenameEl.textContent = f.name + " (" + formatBytes(f.size) + ")";
                onFileSelected(true);
            }
        });

        dz.addEventListener("click", function (e) {
            if (e.target !== fileInput) {
                fileInput.click();
            }
        });

        fileInput.addEventListener("change", function () {
            if (this.files.length > 0) {
                filenameEl.textContent = this.files[0].name + " (" + formatBytes(this.files[0].size) + ")";
                onFileSelected(true);
            }
        });
    }

    function updateEncodeBtn() {
        encodeBtn.disabled = !(encodeFileSelected && encodeMessage.value.trim().length > 0);
    }

    function updateDecodeBtn() {
        decodeBtn.disabled = !decodeFileSelected;
    }

    setupDropZone(encodeDropzone, encodeFile, encodeFilename, function (selected) {
        encodeFileSelected = selected;
        updateEncodeBtn();
    });

    setupDropZone(decodeDropzone, decodeFile, decodeFilename, function (selected) {
        decodeFileSelected = selected;
        updateDecodeBtn();
    });

    // ── MESSAGE INPUT ──
    encodeMessage.addEventListener("input", function () {
        charCount.textContent = this.value.length;
        updateEncodeBtn();
    });

    // ── COMPARISON SLIDER ──
    function updateClip(val) {
        var pct = val + "%";
        steganographyImg.style.clipPath = "inset(0 0 0 " + pct + ")";
        compareHandle.style.left = pct;
    }

    compareRange.addEventListener("input", function () {
        updateClip(this.value);
    });

    // ── ENCODE ──
    encodeBtn.addEventListener("click", function () {
        hideError(encodeError);
        resultSection.style.display = "none";
        setLoading(encodeBtn, encodeLoader, true);

        var formData = new FormData();
        formData.append("image", encodeFile.files[0]);
        formData.append("message", encodeMessage.value);

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/encode");
        xhr.timeout = 60000;

        xhr.onload = function () {
            setLoading(encodeBtn, encodeLoader, false);
            try {
                var data = JSON.parse(xhr.responseText);
                if (xhr.status === 200 && data.success) {
                    showEncodeResult(data);
                } else {
                    showError(encodeError, data.error || "Gagal memproses gambar.");
                }
            } catch (e) {
                showError(encodeError, "Respons server tidak valid.");
            }
        };

        xhr.onerror = function () {
            setLoading(encodeBtn, encodeLoader, false);
            showError(encodeError, "Gagal terhubung ke server. Pastikan server berjalan.");
        };

        xhr.ontimeout = function () {
            setLoading(encodeBtn, encodeLoader, false);
            showError(encodeError, "Waktu permintaan habis. Coba dengan gambar yang lebih kecil.");
        };

        xhr.send(formData);
    });

    function showEncodeResult(data) {
        document.getElementById("orig-img").src = "data:image/png;base64," + data.original_b64;
        document.getElementById("steganography-img").src = "data:image/png;base64," + data.steganography_b64;
        document.getElementById("diff-img").src = "data:image/png;base64," + data.diff_b64;

        document.getElementById("stat-psnr").textContent =
            data.stats.psnr_db === "-" ? "\u221E dB" : data.stats.psnr_db + " dB";
        document.getElementById("stat-mse").textContent = data.stats.mse;
        document.getElementById("stat-changed").textContent =
            data.stats.changed_pixels + " / " + data.stats.total_pixels;
        document.getElementById("stat-capacity").textContent = data.stats.capacity_used_pct + "%";
        document.getElementById("stat-time").textContent = data.stats.encode_time_ms + " ms";
        document.getElementById("stat-chars").textContent = data.stats.message_chars + " char";

        if (maxChars.textContent === "-") {
            maxChars.textContent = Math.floor((data.stats.total_pixels - 4)).toLocaleString();
        }

        var dl = document.getElementById("download-btn");
        dl.href = "/api/download/" + data.steganography_id;

        compareRange.value = 50;
        updateClip(50);

        resultSection.style.display = "block";
        statsGrid.style.display = "grid";

        setTimeout(function () {
            resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 100);
    }

    // ── DECODE ──
    decodeBtn.addEventListener("click", function () {
        hideError(decodeError);
        decodeResult.style.display = "none";
        setLoading(decodeBtn, decodeLoader, true);

        var formData = new FormData();
        formData.append("image", decodeFile.files[0]);

        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/api/decode");
        xhr.timeout = 30000;

        xhr.onload = function () {
            setLoading(decodeBtn, decodeLoader, false);
            try {
                var data = JSON.parse(xhr.responseText);
                if (xhr.status === 200 && data.success) {
                    showDecodeResult(data);
                } else {
                    showError(decodeError, data.error || "Gagal mengekstrak pesan.");
                }
            } catch (e) {
                showError(decodeError, "Respons server tidak valid.");
            }
        };

        xhr.onerror = function () {
            setLoading(decodeBtn, decodeLoader, false);
            showError(decodeError, "Gagal terhubung ke server.");
        };

        xhr.ontimeout = function () {
            setLoading(decodeBtn, decodeLoader, false);
            showError(decodeError, "Waktu permintaan habis.");
        };

        xhr.send(formData);
    });

    function showDecodeResult(data) {
        var msgBox = document.getElementById("decoded-message");
        msgBox.textContent = data.message;

        document.getElementById("decode-chars").textContent = data.char_count + " karakter";
        document.getElementById("decode-time").textContent = data.decode_time_ms + " ms";

        decodeResult.style.display = "block";
        setTimeout(function () {
            decodeResult.scrollIntoView({ behavior: "smooth", block: "start" });
        }, 100);
    }

    // ── INIT ──
    updateEncodeBtn();
    updateDecodeBtn();
    updateClip(50);
})();
