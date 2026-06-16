import json

def analyze_discrepancies(manifest_path):
    with open(manifest_path, 'r') as f:
        data = json.load(f)
    
    total_lines = len(data)
    initial_only = 0
    ftm_only = 0
    both_empty = 0
    both_text = 0
    
    for item in data.values():
        initial = item.get('initial_ocr', '').strip()
        ftm = item.get('ftm_ocr', '').strip()
        
        has_initial = bool(initial)
        has_ftm = bool(ftm)
        
        if has_initial and not has_ftm:
            initial_only += 1
        elif has_ftm and not has_initial:
            ftm_only += 1
        elif not has_initial and not has_ftm:
            both_empty += 1
        else:
            both_text += 1
            
    print(f"Total lines: {total_lines}")
    print(f"Lines with only initial OCR: {initial_only}")
    print(f"Lines with only FTM OCR: {ftm_only}")
    print(f"Lines with both OCR: {both_text}")
    print(f"Lines with neither OCR: {both_empty}")

if __name__ == '__main__':
    analyze_discrepancies('./training_data/manifest_w_lang.json')
