#!/usr/bin/env python3
"""
This script analyzes Cherokee character frequencies within the training dataset
manifest and identifies the bottom 20% under-represented characters.
"""
import os
import json
import argparse
import sys
from collections import Counter

def is_cherokee(char):
    code = ord(char)
    # Cherokee range: 13A0-13FF and AB70-ABFF
    return (0x13A0 <= code <= 0x13FF) or (0xAB70 <= code <= 0xABFF)

def main():
    parser = argparse.ArgumentParser(description="Analyze dataset character frequencies and identify rare characters.")
    parser.add_argument("--manifest", default="training_data/manifest_mixed.json", help="Path to training manifest")
    parser.add_argument("--output", default="training_data/rare_characters.json", help="Path to save rare characters list")
    args = parser.parse_args()

    if not os.path.exists(args.manifest):
        print(f"Error: Manifest path '{args.manifest}' does not exist.")
        sys.exit(1)

    with open(args.manifest, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Filter labeled items
    labeled_items = [
        item for item in manifest.values()
        if item.get("status") == "labeled" and item.get("predicted_lang") == "Cherokee"
    ]

    print(f"Analyzing {len(labeled_items)} labeled Cherokee items from {args.manifest}...")

    # Count character frequencies
    char_counts = Counter()
    for item in labeled_items:
        label = item.get("label") or item.get("truth") or ""
        for char in label:
            if is_cherokee(char):
                char_counts[char] += 1

    if not char_counts:
        print("No Cherokee characters found in the labeled items.")
        sys.exit(0)

    # Sort characters by frequency (ascending)
    sorted_chars = sorted(char_counts.items(), key=lambda x: x[1])

    print("\n--- Cherokee Character Frequencies (Sorted Ascending) ---")
    for rank, (char, count) in enumerate(sorted_chars, 1):
        print(f"{rank:3d}. Character: '{char}' (U+{ord(char):04X}) | Count: {count:4d}")

    # Determine bottom 20% under-represented characters
    # If there are N unique characters, the bottom 20% are the first N // 5 characters (at least 1 if N > 0)
    num_unique = len(sorted_chars)
    cutoff_index = max(1, num_unique // 5)
    
    rare_char_info = sorted_chars[:cutoff_index]
    rare_chars = [char for char, count in rare_char_info]

    print(f"\nTotal Unique Cherokee Characters: {num_unique}")
    print(f"Bottom 20% Cutoff Index: {cutoff_index}")
    print(f"Identified {len(rare_chars)} rare characters:")
    for rank, (char, count) in enumerate(rare_char_info, 1):
        print(f"  - '{char}' (U+{ord(char):04X}) with count {count}")

    # Save to JSON
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(rare_chars, f, ensure_ascii=False, indent=2)
    print(f"\nSaved rare characters list to {args.output}")

if __name__ == "__main__":
    main()
