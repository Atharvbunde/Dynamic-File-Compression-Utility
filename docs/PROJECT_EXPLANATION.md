# Project Explanation

## What is Dynamic File Compression Utility?

It is a software tool that reduces file size using Huffman Coding. It also decompresses the file to recover the original data.

## Why Compression Is Important

Compression saves storage, reduces transfer time, and is used in backups, logs, cloud storage, and data transfer systems.

## Huffman Coding

Huffman Coding is a lossless greedy algorithm. It gives shorter binary codes to frequently occurring characters and longer codes to less frequent characters.

## Data Structures

1. Dictionary: stores character frequencies.
2. Min Heap: selects the two lowest-frequency nodes.
3. Binary Tree: stores Huffman Tree.
4. Dictionary: stores final Huffman codes.

## Complexity

- Frequency calculation: O(n)
- Heap building: O(k log k)
- Encoding: O(n)
- Decoding: O(n)

Where n is total characters and k is unique characters.