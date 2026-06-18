import os
import json
import argparse

def main():
    parser = argparse.ArgumentParser(description="Integrate aligned New Testament crops into a new merged manifest.")
    parser.add_argument("--phoenix-manifest", default="training_data/manifest_w_lang.json", help="Original Phoenix manifest path")
    parser.add_argument("--cnt-dir", default="training_data/cnt", help="Root directory for scraped books")
    parser.add_argument("--output-manifest", default="training_data/manifest_with_cnt.json", help="Merged manifest output path")
    args = parser.parse_args()

    if not os.path.exists(args.phoenix_manifest):
        # Fall back if path variable name parsing issue
        manifest_path = "training_data/manifest_w_lang.json"
    else:
        manifest_path = args.phoenix_manifest

    print(f"Loading original Phoenix manifest from {manifest_path}...")
    with open(manifest_path, "r", encoding="utf-8") as f:
        merged_manifest = json.load(f)

    original_count = len(merged_manifest)
    print(f"Loaded {original_count} original items.")

    cnt_count = 0
    # Loop over all books 01 to 27
    for book_idx in range(1, 28):
        book_str = f"{book_idx:02d}"
        book_dir = os.path.join(args.cnt_dir, f"book_{book_str}")
        aligned_manifest_path = os.path.join(book_dir, "aligned_manifest.json")
        
        if not os.path.exists(aligned_manifest_path):
            continue
            
        print(f"Integrating Book {book_str} from {aligned_manifest_path}...")
        with open(aligned_manifest_path, "r", encoding="utf-8") as f:
            aligned_data = json.load(f)
            
        for verse_key, info in aligned_data.items():
            for line_idx, line in enumerate(info["lines"]):
                # Get the fine-tuned aligned ground truth text
                gt_text = line.get("ftm_aligned", "").strip()
                if not gt_text:
                    continue
                    
                crop_rel_path = line["line_crop"]
                # The crop path relative to training_data/ is: cnt/book_XX/line_crops/...
                image_path = os.path.join("cnt", f"book_{book_str}", crop_rel_path)
                
                # Verify that the crop file actually exists
                crop_full_path = os.path.join("training_data", image_path)
                if not os.path.exists(crop_full_path):
                    continue
                    
                item_id = f"cnt_{book_str}_{verse_key}_line_{line_idx:02d}"
                
                merged_manifest[item_id] = {
                    "id": item_id,
                    "image_path": image_path,
                    "label": gt_text,
                    "status": "labeled",
                    "predicted_lang": "Cherokee"
                }
                cnt_count += 1

    print(f"Integrated {cnt_count} New Testament lines.")
    print(f"Writing new merged manifest containing {len(merged_manifest)} total items to {args.output_manifest}...")
    with open(args.output_manifest, "w", encoding="utf-8") as f:
        json.dump(merged_manifest, f, ensure_ascii=False, indent=2)
    print("Integration complete!")

if __name__ == "__main__":
    main()
