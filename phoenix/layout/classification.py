"""
This module classifies detected layout columns / bounding boxes in images using Tesseract
OCR (with both Cherokee and English languages loaded) and analyzes character proportions
to categorize sections as Cherokee, English, Mixed, or Empty.
"""

import sys
import os
import json
import csv
import pytesseract
from PIL import Image

def is_cherokee_char(c: str) -> bool:
    """
    Checks if a given character is within the Cherokee Unicode blocks.
    """
    o = ord(c)
    # Cherokee: U+13A0 to U+13FF, Cherokee Supplement: U+AB70 to U+ABBF
    return (0x13A0 <= o <= 0x13FF) or (0xAB70 <= o <= 0xABBF)

def is_latin_char(c: str) -> bool:
    """
    Checks if a given character is a Latin alphabet letter.
    """
    return c.isascii() and c.isalpha()

def analyze_text(text: str) -> dict:
    """
    Analyzes OCR string text to determine Cherokee vs Latin characters,
    calculates proportions, and classifies the dominant language.
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
        "text": text.strip(),
    }

def classify_line_image(pil_img) -> str:
    """
    Classifies a PIL line crop image using the optimal confidence-weighted scoring heuristic.
    Returns: 'Cherokee', 'English', 'Mixed', or 'Empty'.
    """
    model_dir = "/Users/charlesmcvicker/code/phoenix/training_data/dataset/model"
    ftm_model = "chr_lang_prediction"
    ftm_config = f"--tessdata-dir {model_dir} --psm 7"
    
    try:
        # 1. OCR with FTM
        ftm_data = pytesseract.image_to_data(pil_img, lang=ftm_model, config=ftm_config, output_type=pytesseract.Output.DICT)
        ftm_confs = [c for c in ftm_data['conf'] if c != -1]
        ftm_conf = sum(ftm_confs) / len(ftm_confs) if ftm_confs else 0.0
        
        # 2. OCR with chr
        chr_data = pytesseract.image_to_data(pil_img, lang="chr", config="--psm 7", output_type=pytesseract.Output.DICT)
        chr_confs = [c for c in chr_data['conf'] if c != -1]
        chr_conf = sum(chr_confs) / len(chr_confs) if chr_confs else 0.0
        
        # 3. OCR with eng
        eng_data = pytesseract.image_to_data(pil_img, lang="eng", config="--psm 7", output_type=pytesseract.Output.DICT)
        eng_confs = [c for c in eng_data['conf'] if c != -1]
        eng_conf = sum(eng_confs) / len(eng_confs) if eng_confs else 0.0
        
        # 4. OCR with chr+eng for character counting
        chreng_data = pytesseract.image_to_data(pil_img, lang="chr+eng", config="--psm 7", output_type=pytesseract.Output.DICT)
        chreng_text = " ".join([w for w in chreng_data['text'] if w.strip()])
        
        cherokee_count = sum(1 for c in chreng_text if is_cherokee_char(c))
        latin_count = sum(1 for c in chreng_text if is_latin_char(c))
        total_chars = cherokee_count + latin_count
        pct_cherokee = cherokee_count / total_chars if total_chars > 0 else 0.0
        
        if total_chars == 0 and ftm_conf == 0.0 and chr_conf == 0.0:
            return "Empty"
            
        score = 0.20 * ftm_conf + 0.50 * chr_conf - 0.50 * eng_conf + 0.50 * (pct_cherokee * 100.0)
        
        if score >= 32.1158:
            return "Cherokee"
        elif pct_cherokee > 0.05 or score >= 20.0:
            return "Mixed"
        else:
            return "English"
    except Exception as e:
        print(f"Error classifying line: {e}")
        return "English"
