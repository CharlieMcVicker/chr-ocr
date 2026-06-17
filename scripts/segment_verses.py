import os
import json
import argparse
from PIL import Image
from phoenix.layout.segmentation import extract_lines_from_image

def process_book_verses(book_dir):
    """
    Processes all verse PNG images in a book directory:
    - Performs line extraction/segmentation on each image using Surya.
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

    for verse_key, info in metadata.items():
        image_relative_path = info["image_path"]
        image_absolute_path = os.path.join(book_dir, image_relative_path)
        
        if not os.path.isfile(image_absolute_path):
            print(f"Verse {verse_key}: Image file not found at {image_absolute_path}. Skipping.")
            continue
            
        print(f"Processing verse {verse_key} ({os.path.basename(image_absolute_path)})...")
        try:
            pil_img = Image.open(image_absolute_path).convert("RGB")
        except Exception as e:
            print(f"Failed to load image for verse {verse_key}: {e}")
            continue

        # Extract lines
        try:
            columns_results = extract_lines_from_image(pil_img, padding_x=5, padding_y=3)
        except Exception as e:
            print(f"Line extraction failed for verse {verse_key}: {e}")
            continue

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
            "image_path": image_relative_path,
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
    args = parser.parse_args()

    process_book_verses(args.book_dir)
