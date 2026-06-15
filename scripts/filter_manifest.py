"""
This module filters the training manifest to clean and retain high-quality dataset entries.
It processes entries in parallel, performs Tesseract OCR on unlabeled samples, classifies
their language content, and filters out short or low-quality transcriptions.
"""
import os
import sys
import json
import shutil
import subprocess
from PIL import Image
import tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from scripts.classify_layout import classify_line_image

def is_cherokee_char(c: str) -> bool:
    """
    Checks if a character belongs to the Cherokee Unicode ranges.
    
    Args:
        c: A single-character string.
        
    Returns:
        True if Cherokee, False otherwise.
    """
    o = ord(c)
    return (0x13A0 <= o <= 0x13FF) or (0xAB70 <= o <= 0xABBF)

def is_latin_char(c: str) -> bool:
    """
    Checks if a character is a Latin letter.
    
    Args:
        c: A single-character string.
        
    Returns:
        True if a Latin letter, False otherwise.
    """
    return c.isascii() and c.isalpha()

def analyze_text(text: str) -> dict:
    """
    Analyzes counts of Cherokee vs Latin characters to categorize text segment language.
    
    Args:
        text: OCR text.
        
    Returns:
        Dict detailing character counts, total counts, and classification.
    """
    cherokee_count = 0
    latin_count = 0
    for c in text:
        if is_cherokee_char(c):
            cherokee_count += 1
        elif is_latin_char(c):
            latin_count += 1

    total = cherokee_count + latin_count
    pct_cherokee = cherokee_count / total if total else 0

    if total == 0:
        classification = "Empty"
    elif pct_cherokee < 0.40:
        classification = "English"
    elif pct_cherokee > 0.45:
        classification = "Cherokee"
    else:
        classification = "Mixed"

    return {
        "cherokee_count": cherokee_count,
        "latin_count": latin_count,
        "classification": classification,
        "total": total
    }

def run_ocr(image_path):
    """
    Performs OCR in single-line mode on the given image after converting it via temporary PNG.
    
    Args:
        image_path: Path to the image file.
        
    Returns:
        Stripped OCR output string.
    """
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        temp_img_path = tmp.name
    try:
        img = Image.open(image_path).convert("RGB")
        img.save(temp_img_path)
        result = subprocess.run(
            ["tesseract", "--psm", "7", "--dpi", "300", "-l", "chr+eng", temp_img_path, "stdout"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error OCR-ing {image_path}: {e}")
        return ""
    finally:
        if os.path.exists(temp_img_path):
            try:
                os.remove(temp_img_path)
            except Exception:
                pass

def process_item(item_id, item):
    """
    Filters and enriches a single manifest item based on label status, path validity,
    and text classification criteria.
    
    Args:
        item_id: Key of the item.
        item: Dict value of the item.
        
    Returns:
        Tuple of (item_id, updated_item_or_None, category_reason).
    """
    if item.get("status") != "unlabeled":
        return item_id, item, "keep_labeled"
    
    # Check if initial_ocr has > 10 characters
    initial_ocr = item.get("initial_ocr", "")
    if len(initial_ocr) <= 10:
        return item_id, None, "skip_short_initial"
    
    # Run OCR with chr+eng
    image_path = os.path.join("training_data", item["image_path"])
    if not os.path.exists(image_path):
        return item_id, None, "missing_file"
    
    try:
        img = Image.open(image_path).convert("RGB")
        classification = classify_line_image(img)
    except Exception as e:
        print(f"Error classifying {image_path}: {e}")
        return item_id, None, "error_reading_image"
        
    if classification in ["English", "Empty"]:
        return item_id, None, f"skip_{classification.lower()}"
        
    new_text = run_ocr(image_path)
    updated_item = item.copy()
    updated_item["initial_ocr"] = new_text
    return item_id, updated_item, f"keep_matched_{classification.lower()}"

def main():
    """
    Main entry point to back up the manifest, run parallelized filtering of items
    using ThreadPoolExecutor, display processing statistics, and overwrite the JSON file.
    """
    manifest_path = "training_data/manifest.json"
    backup_path = "training_data/manifest.json.bak"
    
    print("Creating backup of manifest.json...")
    shutil.copyfile(manifest_path, backup_path)
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    print(f"Loaded {len(manifest)} items from manifest.")
    
    # Process items in parallel
    new_manifest = {}
    stats = {}
    
    items_to_process = list(manifest.items())
    
    print("Processing items using ThreadPoolExecutor...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda pair: process_item(pair[0], pair[1]), items_to_process)
        
        for item_id, updated_item, category in results:
            stats[category] = stats.get(category, 0) + 1
            if updated_item is not None:
                new_manifest[item_id] = updated_item
                
    print("\nProcessing complete! Statistics:")
    for cat, count in stats.items():
        print(f"  {cat}: {count}")
        
    print(f"\nWriting new manifest with {len(new_manifest)} items to {manifest_path}...")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(new_manifest, f, indent=2, ensure_ascii=False)
    print("Done!")

if __name__ == "__main__":
    main()
