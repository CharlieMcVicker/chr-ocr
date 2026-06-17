import os
import argparse
from scripts.segment_verses import process_book_verses
from scripts.align_verses import align_book_transcriptions

def main():
    parser = argparse.ArgumentParser(description="Segment and align all scraped New Testament books.")
    parser.add_argument("--cnt-dir", default="training_data/cnt", help="Root directory for scraped books")
    parser.add_argument("--model-dir", default="training_data/dataset/model", help="Model directory containing chr_best_finetuned")
    parser.add_argument("--model-name", default="chr_best_finetuned", help="Name of the model file without extension")
    parser.add_argument("--force", action="store_true", help="Re-run all stages even if output files already exist")
    parser.add_argument("--skip", default="", help="Comma-separated book numbers to skip")
    args = parser.parse_args()

    skip_books = [int(x.strip()) for x in args.skip.split(",") if x.strip().isdigit()]

    for i in range(1, 28):
        if i in skip_books:
            print(f"\n==========================================")
            print(f"Book {i:02d}: skipping as requested (skip list).")
            print(f"==========================================")
            continue

        book_dir = os.path.join(args.cnt_dir, f"book_{i:02d}")
        if not os.path.isdir(book_dir):
            print(f"Book {i:02d}: directory not found, skipping.")
            continue

        segment_map_path = os.path.join(book_dir, "segment_map.json")
        aligned_manifest_path = os.path.join(book_dir, "aligned_manifest.json")

        print(f"\n==========================================")
        print(f"Book {i:02d}: {book_dir}")
        print(f"==========================================")

        # Stage 1: Segmentation — skip if segment_map.json already exists
        if not args.force and os.path.exists(segment_map_path):
            print(f"  [SKIP] Segmentation — segment_map.json already exists.")
        else:
            print(f"  [RUN]  Segmenting verses...")
            try:
                process_book_verses(book_dir)
            except Exception as e:
                print(f"  ERROR segmenting Book {i:02d}: {e}")
                continue

        # Stage 2: Alignment — skip if aligned_manifest.json already exists
        if not args.force and os.path.exists(aligned_manifest_path):
            print(f"  [SKIP] Alignment — aligned_manifest.json already exists.")
        else:
            print(f"  [RUN]  Aligning transcriptions (batch OCR + DP)...")
            try:
                align_book_transcriptions(book_dir, args.model_dir, args.model_name)
            except Exception as e:
                print(f"  ERROR aligning Book {i:02d}: {e}")
                continue

    print("\nAll books processed.")

if __name__ == "__main__":
    main()
