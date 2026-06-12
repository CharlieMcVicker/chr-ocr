"""
This module evaluates the accuracy of Cherokee vs. English line language classification.
It processes folders of Cherokee and English line crops, runs OCR in parallel, and
performs a grid search over decision thresholds to find parameters that optimize accuracy.
"""
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import tempfile
import numpy as np

def is_cherokee_char(c: str) -> bool:
    """
    Checks if a character is in the Cherokee or Cherokee Supplement Unicode blocks.
    
    Args:
        c: A single-character string.
        
    Returns:
        True if the character is Cherokee, False otherwise.
    """
    o = ord(c)
    return (0x13A0 <= o <= 0x13FF) or (0xAB70 <= o <= 0xABBF)

def is_latin_char(c: str) -> bool:
    """
    Checks if a character is a Latin letter.
    
    Args:
        c: A single-character string.
        
    Returns:
        True if the character is a Latin letter, False otherwise.
    """
    return c.isascii() and c.isalpha()

def run_ocr(image_path):
    """
    Runs Tesseract OCR in single-line mode on the specified image file and returns text.
    
    Args:
        image_path: Path to the image file to run OCR on.
        
    Returns:
        Stripped OCR output string.
    """
    try:
        result = subprocess.run(
            ["tesseract", "--psm", "7", "--dpi", "300", "-l", "chr+eng", image_path, "stdout"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error OCR-ing {image_path}: {e}")
        return ""

def process_image(image_path, true_label):
    """
    Processes a single image file by running OCR and returning language classification stats.
    
    Args:
        image_path: Path to the image file.
        true_label: Ground truth label ("Cherokee" or "English").
        
    Returns:
        Dict of results containing path, true_label, counts, and proportions.
    """
    text = run_ocr(image_path)
    cherokee_count = 0
    latin_count = 0
    for c in text:
        if is_cherokee_char(c):
            cherokee_count += 1
        elif is_latin_char(c):
            latin_count += 1
            
    total = cherokee_count + latin_count
    pct_cherokee = cherokee_count / total if total > 0 else 0
    
    return {
        "path": image_path,
        "true_label": true_label,
        "text": text,
        "cherokee_count": cherokee_count,
        "latin_count": latin_count,
        "total": total,
        "pct_cherokee": pct_cherokee
    }

def main():
    """
    Main evaluation entry point. Finds test images, executes thread-pooled OCR processes,
    optimizes thresholds via grid-search, and produces a confusion matrix report.
    """
    chr_dir = "chr_lines"
    eng_dir = "eng_lines"
    
    chr_paths = [os.path.join(chr_dir, f) for f in os.listdir(chr_dir) if f.endswith(".png")]
    eng_paths = [os.path.join(eng_dir, f) for f in os.listdir(eng_dir) if f.endswith(".png")]
    
    tasks = [(p, "Cherokee") for p in chr_paths] + [(p, "English") for p in eng_paths]
    
    print(f"Processing {len(chr_paths)} Cherokee and {len(eng_paths)} English lines...")
    
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_image, p, l) for p, l in tasks]
        for i, future in enumerate(futures):
            res = future.result()
            results.append(res)
            if (i+1) % 50 == 0:
                print(f"Processed {i+1}/{len(tasks)}...")
                
    # Evaluate thresholds
    best_acc = 0
    best_thresh = None
    
    # Let's test a single threshold: if pct_cherokee >= T, classify as Cherokee, else English
    # Current code uses two thresholds: < 0.20 English, > 0.50 Cherokee, else Mixed.
    # To keep it simple, maybe we just need a single threshold or we want to tune the two thresholds.
    print("\n--- Tuning Parameters ---")
    for eng_t in np.arange(0.05, 0.50, 0.05):
        for chr_t in np.arange(0.20, 0.80, 0.05):
            if eng_t >= chr_t:
                continue
            
            correct = 0
            empty = 0
            mixed = 0
            for r in results:
                if r["total"] == 0:
                    empty += 1
                    continue
                    
                if r["pct_cherokee"] < eng_t:
                    pred = "English"
                elif r["pct_cherokee"] > chr_t:
                    pred = "Cherokee"
                else:
                    pred = "Mixed"
                    
                if pred == r["true_label"]:
                    correct += 1
                elif pred == "Mixed":
                    mixed += 1
                    
            acc = correct / len(results)
            if acc > best_acc:
                best_acc = acc
                best_thresh = (eng_t, chr_t)
                
    print(f"Best Accuracy: {best_acc:.4f}")
    print(f"Best Thresholds: English < {best_thresh[0]:.2f}, Cherokee > {best_thresh[1]:.2f}")
    
    # Detailed report for best thresholds
    eng_t, chr_t = best_thresh
    cm = {"Cherokee": {"Cherokee":0, "English":0, "Mixed":0, "Empty":0},
          "English": {"Cherokee":0, "English":0, "Mixed":0, "Empty":0}}
          
    for r in results:
        true_l = r["true_label"]
        if r["total"] == 0:
            cm[true_l]["Empty"] += 1
            continue
            
        if r["pct_cherokee"] < eng_t:
            pred = "English"
        elif r["pct_cherokee"] > chr_t:
            pred = "Cherokee"
        else:
            pred = "Mixed"
            
        cm[true_l][pred] += 1
        
    print("\nConfusion Matrix:")
    print("True \\ Pred | Cherokee | English | Mixed | Empty")
    for tl in ["Cherokee", "English"]:
        print(f"{tl:>11} | {cm[tl]['Cherokee']:>8} | {cm[tl]['English']:>7} | {cm[tl]['Mixed']:>5} | {cm[tl]['Empty']:>5}")

if __name__ == '__main__':
    main()
