import os
import json
import argparse
from PIL import Image
from phoenix.layout.segmentation import extract_lines_from_images_batch

def process_book_verses(book_dir, batch_size=16):
    """
    Processes all verse PNG images in a book directory:
    - Performs line extraction/segmentation on images in batches using Surya.
    - Saves cropped line images in a structured subdirectory.
    - Updates a segment_map metadata mapping the verse image to its line crop file paths.
    """
    images_dir = os.path.join(book_dir, "images")
    metadata_file = os.path.join(book_dir, "metadata.json")
    
    if not os.path.isdir(images_dir) or not os.path.isfile(metadata_file):
        print(f"Error: Missing images or metadata.json in {book_dir}")
        return

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # Output directory for line crops
    lines_output_dir = os.path.join(book_dir, "line_crops")
    os.makedirs(lines_output_dir, exist_ok=True)

    verse_segmentation_map = {}
    
    # Filter valid metadata items
    valid_items = []
    for verse_key, info in metadata.items():
        image_relative_path = info["image_path"]
        image_absolute_path = os.path.join(book_dir, image_relative_path)
        if not os.path.isfile(image_absolute_path):
            print(f"Verse {verse_key}: Image file not found at {image_absolute_path}. Skipping.")
            continue
        valid_items.append((verse_key, info, image_absolute_path))

    # Process in batches
    for i in range(0, len(valid_items), batch_size):
        chunk = valid_items[i:i + batch_size]
        print(f"Processing batch {i // batch_size + 1} ({len(chunk)} verses)...")
        
        chunk_pil_images = []
        for verse_key, info, img_path in chunk:
            try:
                chunk_pil_images.append(Image.open(img_path).convert("RGB"))
            except Exception as e:
                print(f"Failed to load image for verse {verse_key}: {e}")
                # Append None so we keep alignment with chunk indices
                chunk_pil_images.append(None)

        # Filter out None values before batching, but we need to track index mappings
        valid_pil_images = [img for img in chunk_pil_images if img is not None]
        
        # Batch extract lines
        batch_columns_results = []
        if valid_pil_images:
            try:
                batch_columns_results = extract_lines_from_images_batch(valid_pil_images, padding_x=5, padding_y=3, batch_size=batch_size)
            except Exception as e:
                print(f"Batch line extraction failed: {e}")
                
        # Reconstruct result mapping
        result_idx = 0
        for idx, (verse_key, info, img_path) in enumerate(chunk):
            if chunk_pil_images[idx] is None:
                continue
            
            if result_idx >= len(batch_columns_results):
                columns_results = []
            else:
                columns_results = batch_columns_results[result_idx]
            result_idx += 1

            line_files = []
            line_counter = 0

            # Save crops for all detected lines
            for col_data in columns_results:
                for line_data in col_data["lines"]:
                    line_crop = line_data["image"]
                    line_filename = f"{verse_key}_line_{line_counter:02d}.png"
                    line_crop_dest = os.path.join(lines_output_dir, line_filename)
                    
                    line_crop.save(line_crop_dest)
                    line_files.append(os.path.join("line_crops", line_filename))
                    line_counter += 1

            verse_segmentation_map[verse_key] = {
                "image_path": info["image_path"],
                "line_crops": line_files,
                "cherokee": info["cherokee"],
                "english": info["english"],
                "phonetic": info["phonetic"]
            }

    segment_map_path = os.path.join(book_dir, "segment_map.json")
    with open(segment_map_path, "w", encoding="utf-8") as f:
        json.dump(verse_segmentation_map, f, ensure_ascii=False, indent=2)

    print(f"Segmented lines saved. Created map file at {segment_map_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract line images from scraped Cherokee New Testament verse scans.")
    parser.add_argument("--book-dir", default="training_data/cnt/book_01", help="Directory of the book containing images/ and metadata.json")
    parser.add_argument("--batch-size", type=int, default=16, help="Batch size for Surya inference")
    args = parser.parse_args()

    process_book_verses(args.book_dir, batch_size=args.batch_size)

