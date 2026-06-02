import os
import tempfile
from pathlib import Path

from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename

from src.huffman import compress_file, decompress_file, verify_files
from src.stream_compressor import compress_large_file, decompress_large_file

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input_files"
COMPRESSED_DIR = BASE_DIR / "compressed_files"
DECOMPRESSED_DIR = BASE_DIR / "decompressed_files"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "temp_uploads"

for folder in [INPUT_DIR, COMPRESSED_DIR, DECOMPRESSED_DIR, OUTPUT_DIR, TEMP_DIR]:
    folder.mkdir(exist_ok=True)

# IMPORTANT FIX:
# Flask/Werkzeug stores big browser uploads in a temp folder.
# This forces temp upload files to stay inside this project folder, not C:\Windows temp.
tempfile.tempdir = str(TEMP_DIR)
os.environ["TMP"] = str(TEMP_DIR)
os.environ["TEMP"] = str(TEMP_DIR)

app = Flask(__name__)
app.secret_key = "dynamic-file-compression-demo"

# Allow big files. Increase only if your drive has enough free space.
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 * 1024  # 2 GB

# Huffman mode is educational and loads full text in memory.
# Large files automatically use gzip streaming mode.
HUFFMAN_LIMIT_MB = 50


@app.route("/", methods=["GET", "POST"])
def index():
    result = None

    if request.method == "POST":
        uploaded_file = request.files.get("file")
        action = request.form.get("action")

        if not uploaded_file or uploaded_file.filename == "":
            flash("Please choose a file.")
            return redirect(url_for("index"))

        filename = secure_filename(uploaded_file.filename)
        input_path = INPUT_DIR / filename
        uploaded_file.save(input_path)

        file_size_mb = input_path.stat().st_size / (1024 * 1024)

        # Large file safe mode
        if file_size_mb > HUFFMAN_LIMIT_MB:
            compressed_path = COMPRESSED_DIR / f"{Path(filename).stem}.gz"
            metadata_path = OUTPUT_DIR / f"{Path(filename).stem}_large_metadata.json"
            decompressed_path = DECOMPRESSED_DIR / f"{Path(filename).stem}_decompressed{Path(filename).suffix}"

            result = compress_large_file(str(input_path), str(compressed_path), str(metadata_path))
            result["mode"] = "Large File Streaming Mode"
            result["unique_characters"] = "Skipped for large file"
            result["frequency"] = {}
            result["codes"] = {}
            result["compressed_download"] = compressed_path.name
            result["metadata_download"] = metadata_path.name

            if action == "full":
                decompress_large_file(str(compressed_path), str(decompressed_path))
                result["verified"] = input_path.stat().st_size == decompressed_path.stat().st_size
                result["decompressed_download"] = decompressed_path.name

            return render_template("index.html", result=result)

        # Small file DSA Huffman mode
        compressed_path = COMPRESSED_DIR / f"{Path(filename).stem}.huff"
        metadata_path = OUTPUT_DIR / f"{Path(filename).stem}_metadata.json"
        decompressed_path = DECOMPRESSED_DIR / f"{Path(filename).stem}_decompressed.txt"

        if action == "compress":
            result = compress_file(str(input_path), str(compressed_path), str(metadata_path))
            result["mode"] = "Huffman Coding DSA Mode"
            result["compressed_download"] = compressed_path.name
            result["metadata_download"] = metadata_path.name

        elif action == "full":
            result = compress_file(str(input_path), str(compressed_path), str(metadata_path))
            decompress_file(str(compressed_path), str(metadata_path), str(decompressed_path))
            result["mode"] = "Huffman Coding DSA Mode"
            result["verified"] = verify_files(str(input_path), str(decompressed_path))
            result["compressed_download"] = compressed_path.name
            result["metadata_download"] = metadata_path.name
            result["decompressed_download"] = decompressed_path.name

    return render_template("index.html", result=result)


@app.route("/download/<folder>/<filename>")
def download(folder, filename):
    folders = {
        "compressed": COMPRESSED_DIR,
        "decompressed": DECOMPRESSED_DIR,
        "outputs": OUTPUT_DIR,
        "input": INPUT_DIR
    }

    if folder not in folders:
        return "Invalid folder", 404

    file_path = folders[folder] / filename
    if not file_path.exists():
        return "File not found", 404

    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)