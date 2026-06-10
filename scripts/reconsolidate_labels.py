#!/usr/bin/env python
import os
import json
import difflib
import argparse

def main():
    parser = argparse.ArgumentParser(description="Map old training labels to new line crops using fuzzy text matching.")
    parser.add_argument("--old-manifest", default="training_data/manifest.json")
    parser.add_argument("--new-manifest", default="training_data_v2/manifest.json")
    args = parser.parse_args()

    if not os.path.exists(args.old_manifest):
        print(f"Old manifest not found at {args.old_manifest}")
        return

    if not os.path.exists(args.new_manifest):
        print(f"New manifest not found at {args.new_manifest}. Please run prepare_training_data.py first.")
        return

    with open(args.old_manifest, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    with open(args.new_manifest, "r", encoding="utf-8") as f:
        new_data = json.load(f)

    # Group new items by source scan
    new_by_scan = {}
    for new_id, new_item in new_data.items():
        scan = new_item.get("source_scan")
        if scan not in new_by_scan:
            new_by_scan[scan] = []
        new_by_scan[scan].append(new_item)

    transferred_count = 0

    for old_id, old_item in old_data.items():
        if old_item.get("status") not in ["labeled", "not_cherokee", "nasty_crop"]:
            continue

        scan = old_item.get("source_scan")
        if scan not in new_by_scan:
            continue

        # Use the label if available, otherwise initial OCR
        reference_text = old_item.get("label", "").strip()
        if not reference_text:
            reference_text = old_item.get("initial_ocr", "").strip()
            
        if not reference_text:
            continue

        best_match = None
        best_ratio = 0.0

        for new_item in new_by_scan[scan]:
            if new_item.get("status") != "unlabeled":
                continue # Already mapped
            
            new_text = new_item.get("initial_ocr", "").strip()
            if not new_text:
                continue

            ratio = difflib.SequenceMatcher(None, reference_text, new_text).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = new_item

        if best_ratio > 0.75 and best_match is not None:
            best_match["status"] = old_item["status"]
            if "label" in old_item and old_item["label"]:
                best_match["label"] = old_item["label"]
            transferred_count += 1
            print(f"Matched {old_id} -> {best_match['id']} (Confidence: {best_ratio:.2f})")

    # Save the updated new manifest
    with open(args.new_manifest, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print(f"\nReconsolidation complete. Transferred {transferred_count} labeled items to the new manifest.")

if __name__ == "__main__":
    main()
