#!/usr/bin/env python3
"""
This script loads the labeled dataset of Cherokee and English line crops,
extracts Tesseract OCR confidence metrics (eng, chr, FTM) and character counts,
and performs a grid/parameter search to find the optimal classification heuristic.
"""
import os
import sys
import json
from PIL import Image
import pytesseract
from concurrent.futures import ThreadPoolExecutor

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

CHR_DIR = "/Users/charlesmcvicker/code/phoenix/chr_lines"
ENG_DIR = "/Users/charlesmcvicker/code/phoenix/eng_lines"
MANIFEST_PATH = "training_data/manifest_w_lang.json"
CACHE_FILE = "training_data/line_classification_features.json"

MODEL_DIR = "/Users/charlesmcvicker/code/phoenix/training_data/dataset/model"
FTM_MODEL = "chr_best_finetuned"
FTM_CONFIG = f"--tessdata-dir {MODEL_DIR} --psm 7"

def is_cherokee_char(c: str) -> bool:
    o = ord(c)
    return (0x13A0 <= o <= 0x13FF) or (0xAB70 <= o <= 0xABBF)

def is_latin_char(c: str) -> bool:
    return c.isascii() and c.isalpha()

def extract_features_for_image(image_path, true_label):
    try:
        with Image.open(image_path) as img:
            img = img.convert("RGB")
            
            # 1. OCR with FTM
            ftm_data = pytesseract.image_to_data(img, lang=FTM_MODEL, config=FTM_CONFIG, output_type=pytesseract.Output.DICT)
            ftm_confs = [c for c in ftm_data['conf'] if c != -1]
            ftm_conf = sum(ftm_confs) / len(ftm_confs) if ftm_confs else 0.0
            ftm_text = " ".join([w for w in ftm_data['text'] if w.strip()])
            
            # 2. OCR with chr
            chr_data = pytesseract.image_to_data(img, lang="chr", config="--psm 7", output_type=pytesseract.Output.DICT)
            chr_confs = [c for c in chr_data['conf'] if c != -1]
            chr_conf = sum(chr_confs) / len(chr_confs) if chr_confs else 0.0
            chr_text = " ".join([w for w in chr_data['text'] if w.strip()])
            
            # 3. OCR with eng
            eng_data = pytesseract.image_to_data(img, lang="eng", config="--psm 7", output_type=pytesseract.Output.DICT)
            eng_confs = [c for c in eng_data['conf'] if c != -1]
            eng_conf = sum(eng_confs) / len(eng_confs) if eng_confs else 0.0
            eng_text = " ".join([w for w in eng_data['text'] if w.strip()])
            
            # 4. OCR with chr+eng for character counting
            chreng_data = pytesseract.image_to_data(img, lang="chr+eng", config="--psm 7", output_type=pytesseract.Output.DICT)
            chreng_text = " ".join([w for w in chreng_data['text'] if w.strip()])
            
            cherokee_count = sum(1 for c in chreng_text if is_cherokee_char(c))
            latin_count = sum(1 for c in chreng_text if is_latin_char(c))
            total_chars = cherokee_count + latin_count
            pct_cherokee = cherokee_count / total_chars if total_chars > 0 else 0.0
            
            return {
                "image_path": image_path,
                "true_label": true_label,
                "ftm_conf": round(ftm_conf, 2),
                "ftm_text": ftm_text,
                "chr_conf": round(chr_conf, 2),
                "chr_text": chr_text,
                "eng_conf": round(eng_conf, 2),
                "eng_text": eng_text,
                "pct_cherokee": round(pct_cherokee, 4),
                "cherokee_count": cherokee_count,
                "latin_count": latin_count,
                "total_chars": total_chars
            }
    except Exception as e:
        print(f"Error processing {image_path}: {e}")
        return None

def main():
    # Load cache if it exists
    if os.path.exists(CACHE_FILE):
        print(f"Loading cached features from {CACHE_FILE}...")
        with open(CACHE_FILE, "r") as f:
            dataset = json.load(f)
    else:
        print("Feature cache not found. Running OCR on dataset...")
        tasks = []
        
        # 1. Add chr_lines (labeled Cherokee)
        if os.path.exists(CHR_DIR):
            for f in os.listdir(CHR_DIR):
                if f.endswith(".png"):
                    tasks.append((os.path.join(CHR_DIR, f), "Cherokee"))
                    
        # 2. Add eng_lines (labeled English)
        if os.path.exists(ENG_DIR):
            for f in os.listdir(ENG_DIR):
                if f.endswith(".png"):
                    tasks.append((os.path.join(ENG_DIR, f), "English"))
                    
        # 3. Add Cherokee false positives (status == not_cherokee in manifest)
        if os.path.exists(MANIFEST_PATH):
            with open(MANIFEST_PATH, "r") as f:
                manifest = json.load(f)
            for k, v in manifest.items():
                if v.get("status") == "not_cherokee":
                    img_path = os.path.join("training_data", v["image_path"])
                    if os.path.exists(img_path):
                        tasks.append((img_path, "English")) # labeled English/not_cherokee
                        
        print(f"Total tasks to run OCR on: {len(tasks)}")
        
        dataset = []
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(extract_features_for_image, p, l) for p, l in tasks]
            for i, fut in enumerate(futures):
                res = fut.result()
                if res:
                    dataset.append(res)
                if (i+1) % 50 == 0:
                    print(f"Processed {i+1}/{len(tasks)} images...")
                    
        print(f"Saving features cache to {CACHE_FILE}...")
        with open(CACHE_FILE, "w") as f:
            json.dump(dataset, f, indent=2)
            
    print(f"Loaded {len(dataset)} items in dataset.")
    
    # Run Grid Search
    best_accuracy = 0.0
    best_params = {}
    
    print("\n--- Running Grid Search for Optimal Heuristics ---")
    
    # We want to search:
    # 1. Simple model combining weights: Score = w_ftm * ftm_conf + w_chr * chr_conf - w_eng * eng_conf + w_pct * (pct_cherokee * 100)
    # Let's search various combinations of thresholds and weights
    # Specifically, we want to maximize classification accuracy of Cherokee vs English.
    
    import numpy as np
    
    # Grid of parameters
    for w_ftm in [0.0, 0.2, 0.5, 0.8, 1.0]:
        for w_chr in [0.0, 0.2, 0.5, 0.8, 1.0]:
            for w_eng in [0.0, 0.2, 0.5, 0.8, 1.0]:
                for w_pct in [0.0, 0.5, 1.0, 2.0, 5.0]:
                    # Evaluate on various thresholds
                    scores = []
                    for item in dataset:
                        # Normalize inputs to 0-100 range
                        ftm_val = item["ftm_conf"]
                        chr_val = item["chr_conf"]
                        eng_val = item["eng_conf"]
                        pct_val = item["pct_cherokee"] * 100.0
                        
                        score = w_ftm * ftm_val + w_chr * chr_val - w_eng * eng_val + w_pct * pct_val
                        scores.append(score)
                        
                    # Find best threshold for this weight combo
                    if not scores:
                        continue
                    min_s, max_s = min(scores), max(scores)
                    for thresh in np.linspace(min_s, max_s, 20):
                        correct = 0
                        for idx, item in enumerate(dataset):
                            score = scores[idx]
                            # If score >= thresh, predict Cherokee, else English
                            pred = "Cherokee" if score >= thresh else "English"
                            if pred == item["true_label"]:
                                correct += 1
                                
                        accuracy = correct / len(dataset)
                        if accuracy > best_accuracy:
                            best_accuracy = accuracy
                            best_params = {
                                "w_ftm": w_ftm,
                                "w_chr": w_chr,
                                "w_eng": w_eng,
                                "w_pct": w_pct,
                                "threshold": thresh
                            }
                            
    print(f"\nBest Grid Search Accuracy: {best_accuracy * 100.0:.2f}%")
    print("Best Parameters:")
    for k, v in best_params.items():
        print(f"  {k}: {v:.4f}" if isinstance(v, float) else f"  {k}: {v}")
        
    # Let's also evaluate a simple, highly interpretable decision tree/rule heuristic:
    # Rule: Classify as Cherokee if:
    # 1. pct_cherokee > thresh_pct
    # OR (pct_cherokee > thresh_min_pct AND ftm_conf > thresh_ftm AND chr_conf > thresh_chr)
    # AND eng_conf < thresh_eng
    
    print("\n--- Running Grid Search for Decision Rule Heuristics ---")
    best_rule_accuracy = 0.0
    best_rule = None
    
    # We will search:
    # thresh_pct (0.3 to 0.6)
    # thresh_ftm (5.0 to 50.0)
    # thresh_chr (5.0 to 50.0)
    # thresh_eng (5.0 to 80.0)
    
    for t_pct in [0.30, 0.35, 0.40, 0.45, 0.50]:
        for t_ftm in [5.0, 10.0, 15.0, 20.0, 30.0, 40.0]:
            for t_chr in [5.0, 10.0, 15.0, 20.0, 30.0, 40.0]:
                for t_eng in [30.0, 40.0, 50.0, 60.0, 70.0, 80.0]:
                    correct = 0
                    for item in dataset:
                        pct = item["pct_cherokee"]
                        ftm = item["ftm_conf"]
                        chr_c = item["chr_conf"]
                        eng = item["eng_conf"]
                        
                        # Rule heuristic
                        # Cherokee if Tesseract pct_cherokee is high
                        # OR if FTM/chr confidences are strong and eng is weak
                        is_chr_by_pct = pct >= t_pct
                        is_chr_by_conf = (pct >= 0.15) and (ftm >= t_ftm) and (chr_c >= t_chr) and (eng < t_eng)
                        
                        pred = "Cherokee" if (is_chr_by_pct or is_chr_by_conf) else "English"
                        if pred == item["true_label"]:
                            correct += 1
                            
                    accuracy = correct / len(dataset)
                    if accuracy > best_rule_accuracy:
                        best_rule_accuracy = accuracy
                        best_rule = (t_pct, t_ftm, t_chr, t_eng)
                        
    print(f"Best Rule Accuracy: {best_rule_accuracy * 100.0:.2f}%")
    print(f"Best Rule Thresholds: pct_cherokee >= {best_rule[0]:.2f} OR (pct >= 0.15 AND ftm_conf >= {best_rule[1]:.1f} AND chr_conf >= {best_rule[2]:.1f} AND eng_conf < {best_rule[3]:.1f})")

    # Generate Confusion Matrix for best rule
    t_pct, t_ftm, t_chr, t_eng = best_rule
    cm = {"Cherokee": {"Cherokee": 0, "English": 0}, "English": {"Cherokee": 0, "English": 0}}
    
    for item in dataset:
        pct = item["pct_cherokee"]
        ftm = item["ftm_conf"]
        chr_c = item["chr_conf"]
        eng = item["eng_conf"]
        
        is_chr_by_pct = pct >= t_pct
        is_chr_by_conf = (pct >= 0.15) and (ftm >= t_ftm) and (chr_c >= t_chr) and (eng < t_eng)
        
        pred = "Cherokee" if (is_chr_by_pct or is_chr_by_conf) else "English"
        cm[item["true_label"]][pred] += 1
        
    print("\nConfusion Matrix for Decision Rule:")
    print("True \\ Pred | Cherokee | English")
    for tl in ["Cherokee", "English"]:
        print(f"{tl:>11} | {cm[tl]['Cherokee']:>8} | {cm[tl]['English']:>7}")

if __name__ == "__main__":
    main()
