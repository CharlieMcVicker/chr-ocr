#!/usr/bin/env python3
"""
This script implements backlog task 90.1.
It mixes the Cherokee Phoenix dataset with a stably sampled subset (10%) of the Cherokee New Testament (CNT) dataset.
"""

import os
import json
import random
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phoenix-manifest", default="training_data/manifest_w_lang.json")
    parser.add_argument("--cnt-dir", default="training_data/cnt")
    parser.add_argument("--output-manifest", default="training_data/manifest_mixed.json")
    parser.add_argument("--phoenix-split", type=float, default=0.8, help="Train split ratio for Phoenix")
    parser.add_argument("--cnt-fraction", type=float, default=0.1, help="Sampling fraction for CNT lines")
    parser.add_argument("--cnt-split", type=float, default=0.8, help="Train split ratio for CNT sampled lines")
    args = parser.parse_args()

    # 1. Load training_data/manifest_w_lang.json
    if not os.path.exists(args.phoenix-manifest if hasattr(args, "phoenix-manifest") else args.phoenix_manifest):
        print(f"Manifest not found: {args.phoenix_manifest}")
        sys.exit(1)

    phoenix_manifest_path = args.phoenix_manifest
    with open(phoenix_manifest_path, "r", encoding="utf-8") as f:
        phoenix_data = json.load(f)

    # 2. Assign split to all Phoenix labeled Cherokee items
    labeled_phoenix_items = [
        item for item in phoenix_data.values()
        if item.get("status") == "labeled" and item.get("predicted_lang") == "Cherokee"
    ]

    accumulator = 0.0
    for item in labeled_phoenix_items:
        accumulator += (1.0 - args.phoenix_split)
        if accumulator >= 1.0:
            item["split"] = "test"
            accumulator -= 1.0
        else:
            item["split"] = "train"

    # Count splits for Phoenix
    phx_train_count = sum(1 for item in labeled_phoenix_items if item.get("split") == "train")
    phx_test_count = sum(1 for item in labeled_phoenix_items if item.get("split") == "test")
    print(f"Phoenix labeled Cherokee items: {len(labeled_phoenix_items)} (Train: {phx_train_count}, Test: {phx_test_count})")

    # 3. Process each CNT book 01 to 27
    mixed_data = dict(phoenix_data)
    total_cnt_processed = 0
    cnt_train_count = 0
    cnt_test_count = 0

    for book_idx in range(1, 28):
        book_dir = os.path.join(args.cnt_dir, f"book_{book_idx:02d}")
        manifest_path = os.path.join(book_dir, "aligned_manifest.json")
        if not os.path.exists(manifest_path):
            continue

        with open(manifest_path, "r", encoding="utf-8") as f:
            aligned_manifest = json.load(f)

        # Identify lines with non-empty ftm_aligned text
        valid_lines = []
        for verse_key in sorted(aligned_manifest.keys()):
            verse = aligned_manifest[verse_key]
            for line_idx, line in enumerate(verse.get("lines", [])):
                ftm_aligned = line.get("ftm_aligned", "").strip()
                if ftm_aligned:
                    valid_lines.append({
                        "verse_key": verse_key,
                        "line_idx": line_idx,
                        "line": line
                    })

        # 4. Set up a book-specific random.Random seeded with f"cnt_book_salt_book_{book_idx:02d}"
        seed_str = f"cnt_book_salt_book_{book_idx:02d}"
        rng = random.Random(seed_str)

        # 5. Stable-sample 10% of the lines
        k = int(len(valid_lines) * args.cnt_fraction)
        sampled_lines = rng.sample(valid_lines, k)

        # 6. Split these sampled lines into 80% train and 20% test using the same Random generator
        rng.shuffle(sampled_lines)
        num_train = int(len(sampled_lines) * args.cnt_split)
        
        # 7. Format mixed items and populate fields
        for idx, item_info in enumerate(sampled_lines):
            verse_key = item_info["verse_key"]
            line_idx = item_info["line_idx"]
            line = item_info["line"]
            
            item_id = f"cnt_{book_idx:02d}_{verse_key}_line_{line_idx:02d}"
            image_path = f"cnt/book_{book_idx:02d}/line_crops/{verse_key}_line_{line_idx:02d}.png"
            
            # Verify file exists locally (relative to training_data/)
            full_img_path = os.path.join("training_data", image_path)
            if not os.path.exists(full_img_path):
                print(f"Warning: Image file not found: {full_img_path}")

            split_val = "train" if idx < num_train else "test"
            if split_val == "train":
                cnt_train_count += 1
            else:
                cnt_test_count += 1

            mixed_data[item_id] = {
                "id": item_id,
                "image_path": image_path,
                "label": line["ftm_aligned"],
                "status": "labeled",
                "predicted_lang": "Cherokee",
                "dataset": "cnt",
                "split": split_val
            }
            total_cnt_processed += 1

    # 8. Save the merged dictionary to output_manifest
    with open(args.output_manifest, "w", encoding="utf-8") as f:
        json.dump(mixed_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully mixed datasets!")
    print(f"Total CNT items added: {total_cnt_processed} (Train: {cnt_train_count}, Test: {cnt_test_count})")
    print(f"Total items in manifest: {len(mixed_data)}")

if __name__ == "__main__":
    main()
