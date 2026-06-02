import gzip
import json
import os
import shutil
from pathlib import Path


CHUNK_SIZE = 1024 * 1024 * 4  # 4 MB chunks


def compress_large_file(input_path: str, output_path: str, meta_path: str) -> dict:
    input_path = Path(input_path)
    output_path = Path(output_path)
    meta_path = Path(meta_path)

    original_size = input_path.stat().st_size

    with open(input_path, "rb") as src, gzip.open(output_path, "wb", compresslevel=6) as dst:
        while True:
            chunk = src.read(CHUNK_SIZE)
            if not chunk:
                break
            dst.write(chunk)

    compressed_size = output_path.stat().st_size

    metadata = {
        "algorithm": "gzip-streaming",
        "note": "Large file mode uses chunk-based streaming compression to avoid RAM/temp crash.",
        "original_file": input_path.name,
        "original_size_bytes": original_size,
        "compressed_size_bytes": compressed_size,
        "compression_ratio_percent": round((1 - compressed_size / original_size) * 100, 2) if original_size else 0,
        "chunk_size_mb": CHUNK_SIZE // (1024 * 1024)
    }

    with open(meta_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    return metadata


def decompress_large_file(compressed_path: str, output_path: str) -> None:
    with gzip.open(compressed_path, "rb") as src, open(output_path, "wb") as dst:
        shutil.copyfileobj(src, dst, length=CHUNK_SIZE)