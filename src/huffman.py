import heapq
import json
import os
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Optional, Tuple


@dataclass
class HuffmanNode:
    char: Optional[str]
    freq: int
    left: Optional["HuffmanNode"] = None
    right: Optional["HuffmanNode"] = None

    def __lt__(self, other: "HuffmanNode") -> bool:
        return self.freq < other.freq


def calculate_frequency(text: str) -> Dict[str, int]:
    return dict(Counter(text))


def build_huffman_tree(frequency: Dict[str, int]) -> Optional[HuffmanNode]:
    if not frequency:
        return None

    heap = [HuffmanNode(char, freq) for char, freq in frequency.items()]
    heapq.heapify(heap)

    if len(heap) == 1:
        only = heapq.heappop(heap)
        return HuffmanNode(None, only.freq, only, None)

    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq, left, right)
        heapq.heappush(heap, merged)

    return heap[0]


def generate_codes(root: Optional[HuffmanNode]) -> Dict[str, str]:
    codes: Dict[str, str] = {}

    def walk(node: Optional[HuffmanNode], code: str) -> None:
        if node is None:
            return

        if node.char is not None:
            codes[node.char] = code if code else "0"
            return

        walk(node.left, code + "0")
        walk(node.right, code + "1")

    walk(root, "")
    return codes


def encode_text(text: str, codes: Dict[str, str]) -> str:
    return "".join(codes[ch] for ch in text)


def pad_encoded_text(encoded_text: str) -> str:
    extra_padding = 8 - len(encoded_text) % 8
    if extra_padding == 8:
        extra_padding = 0

    padded_info = f"{extra_padding:08b}"
    encoded_text += "0" * extra_padding
    return padded_info + encoded_text


def bits_to_bytes(padded_encoded_text: str) -> bytes:
    output = bytearray()
    for i in range(0, len(padded_encoded_text), 8):
        byte = padded_encoded_text[i:i + 8]
        output.append(int(byte, 2))
    return bytes(output)


def bytes_to_bits(data: bytes) -> str:
    return "".join(f"{byte:08b}" for byte in data)


def remove_padding(bit_string: str) -> str:
    if len(bit_string) < 8:
        return ""

    padding = int(bit_string[:8], 2)
    bit_string = bit_string[8:]

    if padding > 0:
        bit_string = bit_string[:-padding]

    return bit_string


def decode_text(encoded_text: str, reverse_codes: Dict[str, str]) -> str:
    current_code = ""
    decoded_chars = []

    for bit in encoded_text:
        current_code += bit
        if current_code in reverse_codes:
            decoded_chars.append(reverse_codes[current_code])
            current_code = ""

    return "".join(decoded_chars)


def compress_file(input_path: str, output_path: str, meta_path: str) -> Dict:
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    frequency = calculate_frequency(text)
    root = build_huffman_tree(frequency)
    codes = generate_codes(root)
    encoded_text = encode_text(text, codes)
    padded_text = pad_encoded_text(encoded_text)
    compressed_bytes = bits_to_bytes(padded_text)

    with open(output_path, "wb") as file:
        file.write(compressed_bytes)

    metadata = {
        "codes": codes,
        "frequency": frequency,
        "original_file": os.path.basename(input_path),
        "original_size_bytes": os.path.getsize(input_path),
        "compressed_size_bytes": os.path.getsize(output_path),
        "compression_ratio_percent": round(
            (1 - os.path.getsize(output_path) / os.path.getsize(input_path)) * 100, 2
        ) if os.path.getsize(input_path) else 0,
        "unique_characters": len(frequency),
        "total_characters": len(text)
    }

    with open(meta_path, "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=4)

    return metadata


def decompress_file(compressed_path: str, meta_path: str, output_path: str) -> str:
    with open(meta_path, "r", encoding="utf-8") as file:
        metadata = json.load(file)

    codes = metadata["codes"]
    reverse_codes = {code: char for char, code in codes.items()}

    with open(compressed_path, "rb") as file:
        compressed_data = file.read()

    bit_string = bytes_to_bits(compressed_data)
    encoded_text = remove_padding(bit_string)
    decoded_text = decode_text(encoded_text, reverse_codes)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(decoded_text)

    return decoded_text


def verify_files(original_path: str, decompressed_path: str) -> bool:
    with open(original_path, "r", encoding="utf-8") as f1, open(decompressed_path, "r", encoding="utf-8") as f2:
        return f1.read() == f2.read()