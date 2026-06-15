#!/usr/bin/env python3
import argparse
import json
import os
import sqlite3
import subprocess
import sys
from bs4 import BeautifulSoup

DB_PATH = "candidates.db"
LANG = "chr"

def get_hocr(image_path, lang=LANG):
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

def init_db():
    """Initialize database and virtual tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Create the regular metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS line_metadata (
            id TEXT PRIMARY KEY,
            image_path TEXT,
            label TEXT,
            predicted_lang TEXT,
            initial_ocr TEXT
        )
    """)
    # Create FTS5 virtual table
    # We index candidate words as a space-separated string
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_candidates USING fts5(
            id UNINDEXED,
            candidates
        )
    """)
    conn.commit()
    conn.close()

def build_db(limit_count=100):
    """Load manifest, extract top-2 candidates, and save to FTS5 database."""
    init_db()
    
    manifest_path = "training_data_v2/manifest_w_lang.json"
    if not os.path.exists(manifest_path):
        # Fall back to manifest.json if manifest_w_lang.json is not present
        manifest_path = "training_data_v2/manifest.json"
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read Cherokee/labeled entries
    entries = []
    for line_id, entry in manifest.items():
        # Only process entries with Cherokee predicted or labeled language
        if entry.get('predicted_lang') == 'Cherokee' or entry.get('label'):
            entries.append((line_id, entry))
            
    print(f"Found {len(entries)} matching entries. Building DB with limit={limit_count}...")
    
    processed = 0
    for line_id, entry in entries:
        if processed >= limit_count:
            break
            
        img_relative = entry['image_path']
        img_path = os.path.join("training_data_v2", img_relative)
        
        if not os.path.exists(img_path):
            # Try dataset folder fallback if not found in training_data_v2 directly
            base_name = os.path.splitext(os.path.basename(img_relative))[0]
            img_path = os.path.join("training_data_v2/dataset/train", f"{base_name}_base_otsu.png")
            if not os.path.exists(img_path):
                img_path = os.path.join("training_data_v2/dataset/train", f"{base_name}_base_sauvola.png")
                if not os.path.exists(img_path):
                    continue
                    
        hocr = get_hocr(img_path)
        word_choices_list = parse_hocr_lstm_alternatives(hocr)
        
        # Extract top-2 candidates for each word on the line
        all_candidates = []
        for wc in word_choices_list:
            cands = generate_candidates(wc, limit=2)
            all_candidates.extend(cands)
            
        candidates_str = " ".join(all_candidates)
        
        # Save to SQLite
        cursor.execute(
            "INSERT OR REPLACE INTO line_metadata (id, image_path, label, predicted_lang, initial_ocr) VALUES (?, ?, ?, ?, ?)",
            (line_id, img_path, entry.get('label', ''), entry.get('predicted_lang', ''), entry.get('initial_ocr', ''))
        )
        cursor.execute(
            "INSERT OR REPLACE INTO fts_candidates (id, candidates) VALUES (?, ?)",
            (line_id, candidates_str)
        )
        conn.commit()
        
        processed += 1
        if processed % 10 == 0:
            print(f"Processed {processed} lines...")
            
    conn.close()
    print(f"Successfully built DB with {processed} lines.")

def search_db(term):
    """Search for matching terms in the FTS5 table."""
    if not os.path.exists(DB_PATH):
        print(f"Database {DB_PATH} not found. Please run --build first.")
        sys.exit(1)
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Query using FTS5 match
    query = """
        SELECT m.id, m.image_path, m.initial_ocr, m.label, f.candidates
        FROM fts_candidates f
        JOIN line_metadata m ON f.id = m.id
        WHERE f.candidates MATCH ?
    """
    
    try:
        # Wrap term in quotes to query FTS5 correctly
        cursor.execute(query, (f'"{term}"',))
        rows = cursor.fetchall()
        
        print(f"\nSearch results for: '{term}' (Found {len(rows)} matching lines)")
        print("=" * 80)
        for row in rows:
            line_id, img_path, initial_ocr, label, candidates = row
            print(f"Line ID:     {line_id}")
            print(f"Image Path:  {img_path}")
            print(f"Initial OCR: {initial_ocr}")
            print(f"Label (GT):  {label}")
            print(f"Candidates:  {candidates}")
            print("-" * 80)
    except sqlite3.OperationalError as e:
        print(f"Search query failed: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQLite FTS5 LSTM OCR Candidate Search")
    parser.add_argument("--build", action="store_true", help="Build the search index database")
    parser.add_argument("--limit", type=int, default=100, help="Number of lines to index during build")
    parser.add_argument("--search", type=str, help="Search for a term in the candidates database")
    
    args = parser.parse_args()
    
    if args.build:
        build_db(args.limit)
    elif args.search:
        search_db(args.search)
    else:
        parser.print_help()
