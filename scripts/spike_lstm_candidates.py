import json
import os
import sys

# Add project root to sys.path so we can import inference
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from inference import get_hocr, parse_hocr_lstm_alternatives, generate_candidates

def evaluate_predictions():
    manifest_path = "training_data/manifest_w_lang.json"
    if not os.path.exists(manifest_path):
        manifest_path = "training_data/manifest.json"
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    labeled_entries = [
        entry for entry in manifest.values()
        if (entry.get('status') == 'labeled' or entry.get('label')) and entry.get('predicted_lang') == 'Cherokee'
    ]
    
    train_dir = "training_data/dataset/train"
    
    total_gt_words = 0
    captured_top1 = 0
    captured_top2 = 0
    captured_top5 = 0
    processed_count = 0
    
    for entry in labeled_entries:
        base_name = os.path.splitext(os.path.basename(entry['image_path']))[0]
        image_path = os.path.join(train_dir, f"{base_name}_base_otsu.png")
        
        if not os.path.exists(image_path):
            image_path = os.path.join(train_dir, f"{base_name}_base_sauvola.png")
            if not os.path.exists(image_path):
                continue
            
        gt_label = entry['label'].strip()
        hocr = get_hocr(image_path, lang='chr')
        word_choices_list = parse_hocr_lstm_alternatives(hocr)
        
        gt_words = [w.strip() for w in gt_label.split() if w.strip()]
        total_gt_words += len(gt_words)
        
        line_candidates = []
        for wc in word_choices_list:
            cands = generate_candidates(wc, limit=10)
            line_candidates.append(cands)
            
        if len(line_candidates) == len(gt_words):
            for gt_w, cands in zip(gt_words, line_candidates):
                clean_gt = gt_w.strip(".,!?\"()'-“”)")
                clean_cands = [c.strip(".,!?\"()'-“”)") for c in cands]
                
                if clean_cands and clean_gt == clean_cands[0]:
                    captured_top1 += 1
                if clean_gt in clean_cands[:2]:
                    captured_top2 += 1
                if clean_gt in clean_cands[:5]:
                    captured_top5 += 1
        else:
            for gt_w in gt_words:
                clean_gt = gt_w.strip(".,!?\"()'-“”)")
                found_top1 = False
                found_top2 = False
                found_top5 = False
                for cands in line_candidates:
                    clean_cands = [c.strip(".,!?\"()'-“”)") for c in cands]
                    if clean_cands and clean_gt == clean_cands[0]:
                        found_top1 = True
                    if clean_gt in clean_cands[:2]:
                        found_top2 = True
                    if clean_gt in clean_cands[:5]:
                        found_top5 = True
                
                if found_top1:
                    captured_top1 += 1
                if found_top2:
                    captured_top2 += 1
                if found_top5:
                    captured_top5 += 1
                    
        processed_count += 1
        if processed_count >= 100:
            break
        
    print(f"Processed {processed_count} lines found in train dataset folder.")
    if total_gt_words > 0:
        pct_top1 = (captured_top1 / total_gt_words) * 100
        pct_top2 = (captured_top2 / total_gt_words) * 100
        pct_top5 = (captured_top5 / total_gt_words) * 100
        
        print("\n=== Evaluation Results ===")
        print(f"Total Ground Truth Words Evaluated: {total_gt_words}")
        print(f"Captured in Top-1 (Standard OCR): {captured_top1} ({pct_top1:.2f}%)")
        print(f"Captured in Top-2 Candidates:     {captured_top2} ({pct_top2:.2f}%)")
        print(f"Captured in Top-5 Candidates:     {captured_top5} ({pct_top5:.2f}%)")
        print(f"Relative Recall Improvement (Top-2 vs Top-1): {((pct_top2 - pct_top1) / pct_top1 * 100):.2f}%")
        print("===========================\n")

if __name__ == "__main__":
    evaluate_predictions()
