"""
Core functional operations for manifest manipulation:
- Filtering and language classification
- Splitting train/test data
- Cleaning errors from manifests
- Reconsolidating hand-labeled items via fuzzy matching
"""
import os
import sys
import json
import shutil
import random
import difflib
import subprocess
import tempfile
from pathlib import Path
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# We import classify_line_image dynamically or directly depending on sys.path
try:
    from scripts.classify_layout import classify_line_image
except ImportError:
    # Fallback to make sure we can import even if run from different cwd
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
    try:
        from scripts.classify_layout import classify_line_image
    except ImportError:
        classify_line_image = None


def is_cherokee_char(c: str) -> bool:
    """
    Checks if a character belongs to the Cherokee Unicode ranges.
    """
    o = ord(c)
    return (0x13A0 <= o <= 0x13FF) or (0xAB70 <= o <= 0xABBF)


def is_latin_char(c: str) -> bool:
    """
    Checks if a character is a Latin letter.
    """
    return c.isascii() and c.isalpha()


def analyze_text(text: str) -> dict:
    """
    Analyzes counts of Cherokee vs Latin characters to categorize text segment language.
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


def run_ocr(image_path: str) -> str:
    """
    Performs OCR in single-line mode on the given image after converting it via temporary PNG.
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


def process_item(item_id: str, item: dict, image_dir: str) -> tuple:
    """
    Filters and enriches a single manifest item based on label status, path validity,
    and text classification criteria.
    """
    if item.get("status") != "unlabeled":
        return item_id, item, "keep_labeled"
    
    # Check if initial_ocr has > 10 characters
    initial_ocr = item.get("initial_ocr", "")
    if len(initial_ocr) <= 10:
        return item_id, None, "skip_short_initial"
    
    # Run OCR with chr+eng
    image_path = os.path.join(image_dir, item["image_path"])
    if not os.path.exists(image_path):
        return item_id, None, "missing_file"
    
    try:
        img = Image.open(image_path).convert("RGB")
        if classify_line_image is not None:
            classification = classify_line_image(img)
        else:
            # Fallback if import failed
            classification = "Cherokee"
    except Exception as e:
        print(f"Error classifying {image_path}: {e}")
        return item_id, None, "error_reading_image"
        
    if classification in ["English", "Empty"]:
        return item_id, None, f"skip_{classification.lower()}"
        
    new_text = run_ocr(image_path)
    updated_item = item.copy()
    updated_item["initial_ocr"] = new_text
    return item_id, updated_item, f"keep_matched_{classification.lower()}"


def filter_manifest(manifest_path: str, image_dir: str) -> dict:
    """
    Performs parallelized filtering of items in a manifest using ThreadPoolExecutor.
    Creates a backup first. Returns the new manifest dict.
    """
    backup_path = manifest_path + ".bak"
    print(f"Creating backup of {manifest_path}...")
    shutil.copyfile(manifest_path, backup_path)
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    print(f"Loaded {len(manifest)} items from manifest.")
    
    new_manifest = {}
    stats = {}
    items_to_process = list(manifest.items())
    
    print("Processing items using ThreadPoolExecutor...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(lambda pair: process_item(pair[0], pair[1], image_dir), items_to_process)
        
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
    
    return new_manifest


def split_data(src_dir: str, train_dir: str, test_dir: str, split_ratio: float = 0.8, seed: int = 42):
    """
    Randomly splits line assets (images, ground-truths, and boxes) into distinct
    train and test groups based on a given ratio, copying the matching file triplets.
    """
    random.seed(seed)
    
    src_path = Path(src_dir)
    train_path = Path(train_dir)
    test_path = Path(test_dir)
    
    train_path.mkdir(parents=True, exist_ok=True)
    test_path.mkdir(parents=True, exist_ok=True)
    
    png_files = sorted(list(src_path.glob("*.png")))
    random.shuffle(png_files)
    
    has_g_files = []
    no_g_files = []
    
    for png_file in png_files:
        gt_file = png_file.with_suffix(".gt.txt")
        has_g = False
        if gt_file.exists():
            with open(gt_file, "r", encoding="utf-8") as f:
                content = f.read()
                if "Ꮐ" in content:
                    has_g = True
        
        if has_g:
            has_g_files.append(png_file)
        else:
            no_g_files.append(png_file)
            
    print(f"Total PNG files: {len(png_files)}")
    print(f"Files containing 'Ꮐ': {len(has_g_files)}")
    
    g_split_idx = int(len(has_g_files) * split_ratio)
    no_g_split_idx = int(len(no_g_files) * split_ratio)
    
    train_files = has_g_files[:g_split_idx] + no_g_files[:no_g_split_idx]
    test_files = has_g_files[g_split_idx:] + no_g_files[no_g_split_idx:]
    
    print(f"Training files: {len(train_files)} ({len(has_g_files[:g_split_idx])} with 'Ꮐ')")
    print(f"Testing files: {len(test_files)} ({len(has_g_files[g_split_idx:])} with 'Ꮐ')")
    
    for files, target_dir in [(train_files, train_path), (test_files, test_path)]:
        for png_file in files:
            # Copy PNG
            shutil.copy2(png_file, target_dir / png_file.name)
            # Copy GT.TXT
            gt_file = png_file.with_suffix(".gt.txt")
            if gt_file.exists():
                shutil.copy2(gt_file, target_dir / gt_file.name)
            # Copy BOX
            box_file = png_file.with_suffix(".box")
            if box_file.exists():
                shutil.copy2(box_file, target_dir / box_file.name)


def clean_manifest_errors(paths: list):
    """
    Cleans error entries from the specified manifest files.
    """
    for path in paths:
        if not os.path.exists(path):
            print(f"Manifest not found at {path}, skipping clean.")
            continue
        with open(path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        
        keys_to_remove = []
        for k, v in manifest.items():
            if v.get("ftm_ocr") == "Error" or v.get("predicted_lang") == "Error":
                keys_to_remove.append(k)
                
        for k in keys_to_remove:
            del manifest[k]
            
        with open(path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
            
        print(f"Removed {len(keys_to_remove)} error entries from {path}")


def reconsolidate_labels(old_manifest_path: str, new_manifest_path: str):
    """
    Maps old training labels to newly created line crop manifest entries using fuzzy text matching.
    """
    if not os.path.exists(old_manifest_path):
        print(f"Old manifest not found at {old_manifest_path}")
        return

    if not os.path.exists(new_manifest_path):
        print(f"New manifest not found at {new_manifest_path}.")
        return

    with open(old_manifest_path, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    with open(new_manifest_path, "r", encoding="utf-8") as f:
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
    with open(new_manifest_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)

    print(f"\nReconsolidation complete. Transferred {transferred_count} labeled items to the new manifest.")
