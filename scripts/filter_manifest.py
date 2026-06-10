import os
import sys
import json
import shutil
import subprocess
from PIL import Image
import tempfile
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def is_cherokee_char(c: str) -> bool:
    o = ord(c)
    return (0x13A0 <= o <= 0x13FF) or (0xAB70 <= o <= 0xABBF)

def is_latin_char(c: str) -> bool:
    return c.isascii() and c.isalpha()

def analyze_text(text: str) -> dict:
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
    elif pct_cherokee < 0.20:
        classification = "English"
    elif pct_cherokee > 0.50:
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
    
    new_text = run_ocr(image_path)
    analysis = analyze_text(new_text)
    
    # If the new read has > 10 characters and is Cherokee, English, or Mixed
    if analysis["total"] > 10 and analysis["classification"] in ["Cherokee", "English", "Mixed"]:
        # Update manifest item with new OCR
        updated_item = item.copy()
        updated_item["initial_ocr"] = new_text
        return item_id, updated_item, f"keep_matched_{analysis['classification'].lower()}"
    else:
        return item_id, None, "skip_failed_classification"

def main():
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
