#!/usr/bin/env python3
import os
import json
import argparse
from PIL import Image
import pytesseract
import Levenshtein
from scripts.find_missing_spaces import find_missing_spaces
from scripts.apply_space_corrections import apply_space_corrections

# Helper function to do OCR using pytesseract
def ocr_line_with_confidence(pil_img, model_dir=None, model_name=None):
    if model_dir and model_name:
        config = f"--tessdata-dir {model_dir} --psm 7"
        lang = model_name
    else:
        config = "--psm 7"
        lang = "chr"
    
    try:
        data = pytesseract.image_to_data(pil_img, lang=lang, config=config, output_type=pytesseract.Output.DICT)
        words = [w for w in data['text'] if w.strip()]
        ocr_text = ' '.join(words).strip()
        confs = [c for c in data['conf'] if c != -1]
        mean_conf = sum(confs) / len(confs) if confs else 0.0
        return ocr_text, round(mean_conf, 2)
    except Exception as e:
        print(f"OCR failed with lang={lang}, model_dir={model_dir}: {e}")
        return "", 0.0

def ocr_line(pil_img, model_dir=None, model_name=None):
    txt, _ = ocr_line_with_confidence(pil_img, model_dir, model_name)
    return txt

def align_words_to_lines(words, line_ocrs):
    """
    Given a list of words from the ground truth text, and a list of noisy line OCR transcriptions,
    finds the partition of the word list into len(line_ocrs) segments that minimizes the
    total Levenshtein distance between the segment strings and the line OCRs.
    
    Uses dynamic programming or recursion with memoization.
    """
    n_lines = len(line_ocrs)
    if n_lines == 0:
        return []

    # Preprocess words to detect and split hyphenated words split across lines
    def clean_word(w):
        return "".join(c for c in w if c.isalnum() or '\u13A0' <= c <= '\u13FF' or '\uAB70' <= c <= '\uABBF')

    words = list(words)
    start_search_idx = 0
    for i in range(n_lines - 1):
        line_str = line_ocrs[i].rstrip()
        line_words = line_str.split()
        if not line_words:
            continue
            
        # Look for hyphen in the last word, or the second-to-last word if the last is very short garbage
        last_word = line_words[-1]
        has_hyphen = "-" in last_word
        if not has_hyphen and len(line_words) > 1 and len(last_word) <= 2:
            if "-" in line_words[-2]:
                last_word = line_words[-2]
                has_hyphen = True
                
        if not has_hyphen:
            continue
            
        part1 = last_word.split("-")[0]
        
        next_line_words = line_ocrs[i+1].split()
        if not next_line_words:
            continue
        part2 = next_line_words[0]
        
        target = clean_word(part1) + clean_word(part2)
        if not target:
            continue
            
        best_match_idx = -1
        best_dist = float('inf')
        search_limit = min(len(words), start_search_idx + 15)
        for w_idx in range(start_search_idx, search_limit):
            w_clean = clean_word(words[w_idx])
            if not w_clean:
                continue
            dist = Levenshtein.distance(w_clean, target)
            if dist < best_dist:
                best_dist = dist
                best_match_idx = w_idx
                
        if best_match_idx != -1 and best_dist <= 3 and best_dist < len(clean_word(words[best_match_idx])) * 0.4:
            matched_word = words[best_match_idx]
            best_k = 1
            min_split_cost = float('inf')
            for k in range(1, len(matched_word)):
                w1 = matched_word[:k]
                w2 = matched_word[k:]
                split_cost = Levenshtein.distance(clean_word(w1), clean_word(part1)) + Levenshtein.distance(clean_word(w2), clean_word(part2))
                if split_cost < min_split_cost:
                    min_split_cost = split_cost
                    best_k = k
                    
            word1 = matched_word[:best_k] + "-"
            word2 = matched_word[best_k:]
            words[best_match_idx:best_match_idx+1] = [word1, word2]
            start_search_idx = best_match_idx + 2

    n_words = len(words)
    
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

def align_book_transcriptions(book_dir, model_dir, model_name, realign_if_corrected=True):
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
        ftm_confs = []
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
            ftm_txt, ftm_conf = ocr_line_with_confidence(pil_img, model_dir, model_name)
            ftm_ocrs.append(ftm_txt)
            ftm_confs.append(ftm_conf)
            
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
                "ftm_raw_ocr": ftm_ocrs[idx] if idx < len(ftm_ocrs) else "",
                "ftm_confidence": ftm_confs[idx] if idx < len(ftm_confs) else 0.0
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
    
    # Run missing space candidate detection
    print("Checking for missing space candidates in ground truth...")
    try:
        candidates = find_missing_spaces(out_json)
        candidates_out = os.path.join(book_dir, "missing_spaces_candidates.json")
        with open(candidates_out, "w", encoding="utf-8") as f:
            json.dump(candidates, f, ensure_ascii=False, indent=2)
        print(f"Found {len(candidates)} missing space candidates. Report saved to {candidates_out}")

        if realign_if_corrected:
            print("Applying automatic space corrections (if any)...")
            applied = apply_space_corrections(book_dir)
            if applied > 0:
                print("Space corrections applied. Re-running alignment to sync changes...")
                align_book_transcriptions(book_dir, model_dir, model_name, realign_if_corrected=False)
    except Exception as e:
        print(f"Failed to run missing space detection or correction: {e}")


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
