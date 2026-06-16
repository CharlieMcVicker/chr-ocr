import subprocess
import sys
from bs4 import BeautifulSoup

def get_hocr(image_path, lang='chr'):
    """Run Tesseract with lstm_choice_mode=2 and return hOCR HTML."""
    try:
        cmd = ["tesseract", image_path, "stdout", "-l", lang, "--psm", "7", "-c", "lstm_choice_mode=2", "hocr"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running tesseract on {image_path}: {e.stderr}", file=sys.stderr)
        return None

def parse_hocr_lstm_alternatives(hocr_content):
    """
    Parse the hOCR HTML content.
    Returns a list of word choices. Each word choice is a list of lists of (char, confidence).
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

def generate_candidates(word_choices, limit=2):
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
            unique_candidates.append(s_clean)
            
    return unique_candidates
