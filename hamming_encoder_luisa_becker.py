"""
Hamming (31,26) encoder
"""

import argparse
from typing import List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Encode binary input using Hamming (31,26).")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--bits', type=str, help='Binary string to encode.')
    group.add_argument('--file', type=str, help='Path to file containing binary digits.')
    parser.add_argument('--out', type=str, help='Output file to write codewords (one per line).')
    return parser.parse_args()


def read_bits_from_file(path: str) -> str:
    """Read a file and return a concatenated string of 0/1 characters."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        raise SystemExit(f"Error reading file {path}: {e}")
    # Filter out all characters that are not '0' or '1'
    bits = ''.join(c for c in content if c in '01')
    return bits


def chunk_bits(bits: str, chunk_size: int = 26) -> List[str]:
    """Split the binary string into chunks of size `chunk_size`, padding the last chunk with zeros."""
    chunks: List[str] = []
    for i in range(0, len(bits), chunk_size):
        chunk = bits[i:i + chunk_size]
        if len(chunk) < chunk_size:
            chunk = chunk + '0' * (chunk_size - len(chunk))
        chunks.append(chunk)
    return chunks


def encode_hamming_31_26(chunk: str) -> str:
    """
    Encode a 26‑bit binary string into a 31‑bit Hamming (31,26) codeword.

    Parameters
    ----------
    chunk : str
        A string of length 26 containing only '0' and '1'.

    Returns
    -------
    str
        The 31‑bit codeword.
    """
    if len(chunk) != 26:
        raise ValueError(f"Chunk length must be 26 bits, got {len(chunk)} bits.")

    # Positions are 1‑indexed; positions 1,2,4,8,16 are parity bits.
    parity_positions = [1, 2, 4, 8, 16]
    codeword = ['0'] * 31  # index 0 corresponds to position 1

    # Fill data bits into positions that are not parity positions.
    data_index = 0
    for pos in range(1, 32):  # 1 through 31 inclusive
        if pos not in parity_positions:
            # Place the next data bit (1 or 0) into this position.
            codeword[pos - 1] = chunk[data_index]
            data_index += 1

    # Compute parity bits for positions 1,2,4,8,16
    for p in parity_positions:
        parity = 0
        # Iterate over positions 1..31; if the position's bitwise AND with p is non‑zero,
        # include that bit in the parity calculation.
        for pos in range(1, 32):
            if (pos & p) != 0:
                parity ^= int(codeword[pos - 1])
        # Set parity bit such that the total parity is even (parity bit completes the XOR to 0).
        codeword[p - 1] = str(parity)
    return ''.join(codeword)


def main() -> None:
    args = parse_args()
    # Read input bits
    if args.bits:
        bits = ''.join(c for c in args.bits if c in '01')
        if not bits:
            raise SystemExit("--bits argument must contain at least one binary digit (0 or 1).")
    else:
        bits = read_bits_from_file(args.file)
        if not bits:
            raise SystemExit(f"Input file {args.file} contains no binary digits.")

    # Chunk input bits
    chunks = chunk_bits(bits, 26)
    # Encode each chunk
    codewords: List[str] = [encode_hamming_31_26(chunk) for chunk in chunks]
    # Calculate padding if needed
    padding = 0
    if len(bits) % 26 != 0:
        padding = 26 - (len(bits) % 26)
    summary_lines = [
        f"Original length: {len(bits)} bits",
        f"Chunks (26 bits each): {len(chunks)}",
        f"Padding added to last chunk: {padding} bits"
    ]

    # Output results
    if args.out:
        # Write codewords to file, one per line.
        try:
            with open(args.out, 'w', encoding='utf-8') as f:
                for cw in codewords:
                    f.write(cw + '\n')
        except OSError as e:
            raise SystemExit(f"Error writing to output file {args.out}: {e}")
        # Print summary to stdout
        for line in summary_lines:
            print(line)
        print(f"Codewords written to {args.out}")
    else:
        # Print codewords and summary to stdout
        for line in summary_lines:
            print(line)
        print("Codewords:")
        for cw in codewords:
            print(cw)


if __name__ == '__main__':
    main()
