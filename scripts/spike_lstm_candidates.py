import json
import os
import subprocess
from bs4 import BeautifulSoup

def get_hocr(image_path, lang='chr'):
    """Run Tesseract with lstm_choice_mode=2 and return hOCR HTML."""
    try:
        cmd = ["tesseract", image_path, "stdout", "-l", lang, "--psm", "7", "-c", "lstm_choice_mode=2", "hocr"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running tesseract on {image_path}: {e.stderr}")
        return None

def parse_hocr_lstm_alternatives(hocr_content):
    """
    Parse the hOCR HTML content.
    Returns a list of word candidates for the line.
    Structure returned: a list of words, where each word is a list of lists (alternatives for each character position).
    Each alternative is a tuple: (char, confidence).
    """
    if not hocr_content:
        return []
    
    soup = BeautifulSoup(hocr_content, 'html.parser')
    words_data = []
    
    for word_span in soup.find_all('span', class_='ocrx_word'):
        choices_spans = word_span.find_all('span', class_='ocrx_cinfo', id=lambda x: x and x.startswith('lstm_choices_'))
        
        word_choices = []
        for choice_span in choices_spans:
            char_options = []
            for option in choice_span.find_all('span', class_='ocrx_cinfo', id=lambda x: x and x.startswith('choice_')):
                char = option.get_text()
                title = option.get('title', '')
                conf = 0.0
                if 'x_confs' in title:
                    try:
                        conf = float(title.split('x_confs')[1].strip())
                    except ValueError:
                        pass
                char_options.append((char, conf))
            
            if char_options:
                char_options.sort(key=lambda x: x[1], reverse=True)
                word_choices.append(char_options)
        
        if word_choices:
            words_data.append(word_choices)
            
    return words_data

def generate_candidates(word_choices, limit=10):
    """
    Generate candidate words using Cartesian product / beam search over character choices.
    """
    candidates = [("", 0.0)]
    
    for char_options in word_choices:
        next_candidates = []
        for current_str, current_score in candidates:
            for char, conf in char_options:
                next_candidates.append((current_str + char, current_score + conf))
        
        next_candidates.sort(key=lambda x: x[1], reverse=True)
        candidates = next_candidates[:limit]
        
    seen = set()
    unique_candidates = []
    for s, score in candidates:
        s_clean = s.strip()
        if s_clean not in seen:
            seen.add(s_clean)
            unique_candidates.append((s_clean, score))
            
    return unique_candidates

def evaluate_predictions():
    manifest_path = "training_data_v2/manifest_w_lang.json"
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    labeled_entries = [
        entry for entry in manifest.values()
        if (entry.get('status') == 'labeled' or entry.get('label')) and entry.get('predicted_lang') == 'Cherokee'
    ]
    
    train_dir = "/Users/charlesmcvicker/.gemini/antigravity/worktrees/phoenix/implement-task-fifty-four/training_data_v2/dataset/train"
    
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
            line_candidates.append([c[0] for c in cands])
            
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
