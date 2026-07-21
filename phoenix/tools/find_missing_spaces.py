#!/usr/bin/env python3
import os
import json
import argparse
import Levenshtein

def clean_word(w):
    return "".join(c for c in w if c.isalnum() or '\u13A0' <= c <= '\u13FF' or '\uAB70' <= c <= '\uABBF')

def find_missing_spaces(aligned_manifest_path):
    with open(aligned_manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    candidates = []
    
    for verse_key, verse_data in manifest.items():
        cherokee_gt = verse_data["cherokee_gt"]
        gt_words = cherokee_gt.split()
        
        # We gather tokens from all lines *concatenated*.
        # To distinguish a natural line-break hyphenation from a missing space,
        # we can check if the split occurs across lines *and* the first line ends with a hyphen ('-').
        # If the first line does NOT end with a hyphen, but the models both split the word
        # across the line boundary, it could be a missing space (or poor layout segmentation, but worth checking).
        # More commonly, missing space typos occur within the same line, or across lines without a hyphen.
        
        # Let's keep track of which token came from which line index
        stock_tokens_info = []
        ftm_tokens_info = []
        
        for l_idx, line in enumerate(verse_data["lines"]):
            s_tokens = line["stock_raw_ocr"].split()
            f_tokens = line["ftm_raw_ocr"].split()
            
            # Record token and whether its line ended with a hyphen
            s_ends_with_hyphen = line["stock_raw_ocr"].rstrip().endswith("-")
            f_ends_with_hyphen = line["ftm_raw_ocr"].rstrip().endswith("-")
            
            for t in s_tokens:
                if clean_word(t):
                    stock_tokens_info.append((clean_word(t), l_idx, s_ends_with_hyphen))
            for t in f_tokens:
                if clean_word(t):
                    ftm_tokens_info.append((clean_word(t), l_idx, f_ends_with_hyphen))
                    
        for gt_word in gt_words:
            cleaned_gt = clean_word(gt_word)
            if len(cleaned_gt) < 5: 
                continue
                
            for split_idx in range(2, len(cleaned_gt) - 1):
                part1 = cleaned_gt[:split_idx]
                part2 = cleaned_gt[split_idx:]
                
                max_dist1 = max(0, int(len(part1) * 0.15))
                max_dist2 = max(0, int(len(part2) * 0.15))
                
                # Check stock split
                stock_has_split = False
                for i in range(len(stock_tokens_info) - 1):
                    t1, l1, h1 = stock_tokens_info[i]
                    t2, l2, h2 = stock_tokens_info[i+1]
                    if Levenshtein.distance(t1, part1) <= max_dist1 and Levenshtein.distance(t2, part2) <= max_dist2:
                        # If it crosses a line boundary, only accept it if the boundary was NOT hyphenated.
                        # (If it's within the same line, l1 == l2, which is always accepted)
                        if l1 == l2 or not h1:
                            stock_has_split = True
                            break
                            
                # Check FTM split
                ftm_has_split = False
                for i in range(len(ftm_tokens_info) - 1):
                    t1, l1, h1 = ftm_tokens_info[i]
                    t2, l2, h2 = ftm_tokens_info[i+1]
                    if Levenshtein.distance(t1, part1) <= max_dist1 and Levenshtein.distance(t2, part2) <= max_dist2:
                        if l1 == l2 or not h1:
                            ftm_has_split = True
                            break
                            
                if stock_has_split and ftm_has_split:
                    original_split_idx = -1
                    clean_char_count = 0
                    for orig_i, c in enumerate(gt_word):
                        if clean_char_count == split_idx:
                            original_split_idx = orig_i
                            break
                        if c in cleaned_gt[clean_char_count:clean_char_count+1]:
                            clean_char_count += 1
                            
                    if original_split_idx != -1:
                        suggested_split = gt_word[:original_split_idx] + " " + gt_word[original_split_idx:]
                    else:
                        suggested_split = part1 + " " + part2
                        
                    candidates.append({
                        "verse_key": verse_key,
                        "original_word": gt_word,
                        "suggested_split": suggested_split,
                        "stock_words": [part1, part2],
                        "ftm_words": [part1, part2]
                    })
                    break
                    
    return candidates

def main():
    parser = argparse.ArgumentParser(description="Find missing spaces in ground truth transcriptions.")
    parser.add_argument("--manifest", default="training_data/cnt/book_01/aligned_manifest.json", help="Path to aligned_manifest.json")
    parser.add_argument("--output", default="training_data/cnt/book_01/missing_spaces_candidates.json", help="Path to save candidate output JSON")
    args = parser.parse_args()
    
    if not os.path.exists(args.manifest):
        print(f"Error: Manifest file {args.manifest} does not exist.")
        return
        
    candidates = find_missing_spaces(args.manifest)
    
    seen = set()
    deduped = []
    for c in candidates:
        key = (c["verse_key"], c["original_word"], c["suggested_split"])
        if key not in seen:
            seen.add(key)
            deduped.append(c)
            
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(deduped, f, ensure_ascii=False, indent=2)
        
    print(f"Found {len(deduped)} candidates. Saved to {args.output}")
    for c in deduped:
        print(f"Verse {c['verse_key']}: '{c['original_word']}' -> '{c['suggested_split']}'")

if __name__ == "__main__":
    main()
