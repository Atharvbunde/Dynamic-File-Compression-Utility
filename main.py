import argparse
import os
from pathlib import Path
from src.huffman import compress_file, decompress_file, verify_files


def main():
    parser = argparse.ArgumentParser(description="Dynamic File Compression Utility using Huffman Coding")
    sub = parser.add_subparsers(dest="command")

    c = sub.add_parser("compress", help="Compress a text file")
    c.add_argument("input", help="Input text file path")
    c.add_argument("--out", default=None, help="Compressed output file path")
    c.add_argument("--meta", default=None, help="Metadata JSON file path")

    d = sub.add_parser("decompress", help="Decompress a .huff file")
    d.add_argument("compressed", help="Compressed file path")
    d.add_argument("meta", help="Metadata JSON path")
    d.add_argument("--out", default=None, help="Decompressed output text file path")

    v = sub.add_parser("verify", help="Verify original and decompressed file")
    v.add_argument("original")
    v.add_argument("decompressed")

    args = parser.parse_args()

    Path("compressed_files").mkdir(exist_ok=True)
    Path("decompressed_files").mkdir(exist_ok=True)
    Path("outputs").mkdir(exist_ok=True)

    if args.command == "compress":
        input_path = Path(args.input)
        out = args.out or f"compressed_files/{input_path.stem}.huff"
        meta = args.meta or f"outputs/{input_path.stem}_metadata.json"

        result = compress_file(str(input_path), out, meta)
        print("Compression completed successfully.")
        print(f"Compressed File: {out}")
        print(f"Metadata File: {meta}")
        print(f"Original Size: {result['original_size_bytes']} bytes")
        print(f"Compressed Size: {result['compressed_size_bytes']} bytes")
        print(f"Compression Ratio: {result['compression_ratio_percent']}%")

    elif args.command == "decompress":
        out = args.out or "decompressed_files/decompressed_output.txt"
        decompress_file(args.compressed, args.meta, out)
        print("Decompression completed successfully.")
        print(f"Decompressed File: {out}")

    elif args.command == "verify":
        print("MATCHED: original and decompressed files are same." if verify_files(args.original, args.decompressed) else "NOT MATCHED.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()