#!/usr/bin/env python3
import os
import json
import argparse
from PIL import Image
import pytesseract
import Levenshtein

# Helper function to do OCR using pytesseract
def ocr_line(pil_img, model_dir=None, model_name=None):
    if model_dir and model_name:
        config = f"--tessdata-dir {model_dir} --psm 7"
        lang = model_name
    else:
        config = "--psm 7"
        lang = "chr"
    
    try:
        # Get OCR text
        ocr_text = pytesseract.image_to_string(pil_img, lang=lang, config=config)
        return ocr_text.strip()
    except Exception as e:
        print(f"OCR failed with lang={lang}, model_dir={model_dir}: {e}")
        return ""

def align_words_to_lines(words, line_ocrs):
    """
    Given a list of words from the ground truth text, and a list of noisy line OCR transcriptions,
    finds the partition of the word list into len(line_ocrs) segments that minimizes the
    total Levenshtein distance between the segment strings and the line OCRs.
    
    Uses dynamic programming or recursion with memoization.
    """
    n_words = len(words)
    n_lines = len(line_ocrs)
    
    if n_lines == 0:
        return []
    
    # Memoization table: memo[(word_idx, line_idx)] = (cost, split_index_after)
    memo = {}
    
    def solve(w_idx, l_idx):
        if l_idx == n_lines:
            if w_idx == n_words:
                return 0, []
            else:
                return float('inf'), []
        
        if w_idx == n_words:
            # We ran out of words but still have lines left
            # All remaining lines get empty text
            cost = 0
            splits = []
            for i in range(l_idx, n_lines):
                cost += Levenshtein.distance("", line_ocrs[i])
                splits.append(n_words)
            return cost, splits
            
        state = (w_idx, l_idx)
        if state in memo:
            return memo[state]
            
        best_cost = float('inf')
        best_splits = []
        
        # If it's the last line, it MUST consume all remaining words
        if l_idx == n_lines - 1:
            segment_str = " ".join(words[w_idx:])
            cost = Levenshtein.distance(segment_str, line_ocrs[l_idx])
            res = (cost, [n_words])
            memo[state] = res
            return res
            
        # Try all possible ending indices for the current line's word segment
        # The segment can be empty (ending at w_idx) or contain words up to n_words
        for next_w_idx in range(w_idx, n_words + 1):
            segment_str = " ".join(words[w_idx:next_w_idx])
            line_cost = Levenshtein.distance(segment_str, line_ocrs[l_idx])
            
            sub_cost, sub_splits = solve(next_w_idx, l_idx + 1)
            total_cost = line_cost + sub_cost
            
            if total_cost < best_cost:
                best_cost = total_cost
                best_splits = [next_w_idx] + sub_splits
                
        res = (best_cost, best_splits)
        memo[state] = res
        return res

    _, splits = solve(0, 0)
    
    # Reconstruct segments
    segments = []
    curr_w_idx = 0
    for split in splits:
        segments.append(" ".join(words[curr_w_idx:split]))
        curr_w_idx = split
    return segments

def align_book_transcriptions(book_dir, model_dir, model_name):
    segment_map_path = os.path.join(book_dir, "segment_map.json")
    if not os.path.isfile(segment_map_path):
        print(f"Error: segment_map.json not found in {book_dir}")
        return
        
    with open(segment_map_path, "r", encoding="utf-8") as f:
        segment_map = json.load(f)
        
    aligned_results = {}
    
    # We will generate a verification report
    report_rows = []
    
    for verse_key, info in segment_map.items():
        print(f"Aligning verse {verse_key}...")
        line_crops = info["line_crops"]
        cherokee_gt = info["cherokee"]
        
        # Split the verse key to extract the verse number
        # verse_key looks like e.g. "010102"
        # Let's parse the verse number (last 2 digits)
        try:
            verse_num = str(int(verse_key[-2:]))
        except ValueError:
            verse_num = ""
            
        # 1. Read crops and run OCR using stock and fine-tuned
        stock_ocrs = []
        ftm_ocrs = []
        pil_images = []
        
        for crop_rel_path in line_crops:
            crop_path = os.path.join(book_dir, crop_rel_path)
            if not os.path.isfile(crop_path):
                print(f"  Warning: Crop file not found: {crop_path}")
                continue
            
            try:
                pil_img = Image.open(crop_path).convert("RGB")
            except Exception as e:
                print(f"  Failed to load crop {crop_path}: {e}")
                continue
                
            pil_images.append((crop_rel_path, pil_img))
            
            # Run Stock Tesseract
            stock_txt = ocr_line(pil_img)
            stock_ocrs.append(stock_txt)
            
            # Run Fine-tuned Tesseract
            ftm_txt = ocr_line(pil_img, model_dir, model_name)
            ftm_ocrs.append(ftm_txt)
            
        if not pil_images:
            continue
            
        # Tokenize ground truth
        words = cherokee_gt.split()
        
        # 2. Align ground truth to the line crops using both OCR candidates
        stock_aligned = align_words_to_lines(words, stock_ocrs)
        ftm_aligned = align_words_to_lines(words, ftm_ocrs)
        
        # We will keep the fine-tuned aligned as the main choice, but fallback or record both
        # Let's save both versions in the aligned_results metadata for study
        aligned_results[verse_key] = {
            "image_path": info["image_path"],
            "cherokee_gt": cherokee_gt,
            "verse_number": verse_num,
            "lines": []
        }
        
        for idx, (crop_rel, pil_img) in enumerate(pil_images):
            stock_text = stock_aligned[idx] if idx < len(stock_aligned) else ""
            ftm_text = ftm_aligned[idx] if idx < len(ftm_aligned) else ""
            
            # Prepend verse number to the very first line crop of the verse
            # The prompt says: "the verse number will just be the number with no dot"
            stock_formatted = stock_text
            ftm_formatted = ftm_text
            if idx == 0 and verse_num:
                if stock_formatted:
                    stock_formatted = f"{verse_num} {stock_formatted}"
                else:
                    stock_formatted = verse_num
                    
                if ftm_formatted:
                    ftm_formatted = f"{verse_num} {ftm_formatted}"
                else:
                    ftm_formatted = verse_num
            
            aligned_results[verse_key]["lines"].append({
                "line_crop": crop_rel,
                "stock_aligned": stock_formatted,
                "stock_raw_ocr": stock_ocrs[idx] if idx < len(stock_ocrs) else "",
                "ftm_aligned": ftm_formatted,
                "ftm_raw_ocr": ftm_ocrs[idx] if idx < len(ftm_ocrs) else ""
            })
            
            # Prepare row for HTML report
            report_rows.append({
                "verse_key": verse_key,
                "line_idx": idx,
                "crop_rel": os.path.join(os.path.basename(book_dir), crop_rel),
                "stock_ocr": stock_ocrs[idx] if idx < len(stock_ocrs) else "",
                "stock_aligned": stock_formatted,
                "ftm_ocr": ftm_ocrs[idx] if idx < len(ftm_ocrs) else "",
                "ftm_aligned": ftm_formatted
            })

    # Save aligned results
    out_json = os.path.join(book_dir, "aligned_manifest.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(aligned_results, f, ensure_ascii=False, indent=2)
    print(f"Aligned results saved to {out_json}")
    
    # Generate verification HTML report
    html_path = os.path.join(book_dir, "alignment_verification.html")
    generate_html_report(html_path, report_rows)
    print(f"Verification report created at {html_path}")

def generate_html_report(html_path, rows):
    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Cherokee NT Alignment Verification</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 20px; }
        h1 { color: #333; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; background-color: #fff; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        th, td { padding: 12px; border: 1px solid #dee2e6; text-align: left; }
        th { background-color: #343a40; color: white; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .crop-img { max-height: 60px; border: 1px solid #ccc; }
        .ocr-raw { font-style: italic; color: #555; font-size: 0.9em; }
        .aligned-text { font-weight: bold; color: #2b5c8f; font-size: 1.1em; }
        .verse-num { background-color: #e9ecef; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
    </style>
</head>
<body>
    <h1>Cherokee NT Alignment Verification Report</h1>
    <p>Compare the line crop, the Tesseract raw OCR outputs, and the aligned ground-truth text segments.</p>
    <table>
        <thead>
            <tr>
                <th>Verse</th>
                <th>Line Index</th>
                <th>Crop Image</th>
                <th>Stock Raw OCR</th>
                <th>Stock Aligned GT</th>
                <th>FTM Raw OCR</th>
                <th>FTM Aligned GT</th>
            </tr>
        </thead>
        <tbody>
    """
    for r in rows:
        html_content += f"""
            <tr>
                <td><span class="verse-num">{r['verse_key']}</span></td>
                <td>{r['line_idx']}</td>
                <td><img class="crop-img" src="{r['crop_rel']}" alt="crop" /></td>
                <td class="ocr-raw">{r['stock_ocr']}</td>
                <td class="aligned-text">{r['stock_aligned']}</td>
                <td class="ocr-raw">{r['ftm_ocr']}</td>
                <td class="aligned-text">{r['ftm_aligned']}</td>
            </tr>
        """
        
    html_content += """
        </tbody>
    </table>
</body>
</html>
    """
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Align Cherokee NT transcriptions with extracted line crops.")
    parser.add_argument("--book-dir", default="training_data/cnt/book_01", help="Book directory containing images, crops, metadata")
    parser.add_argument("--model-dir", default="/Users/charlesmcvicker/code/phoenix/training_data/dataset/model", help="Tessdata directory containing the fine-tuned model")
    parser.add_argument("--model-name", default="chr_best_finetuned", help="Name of the fine-tuned model file (without .traineddata)")
    
    args = parser.parse_args()
    align_book_transcriptions(args.book_dir, args.model_dir, args.model_name)
