import os
import json
import sqlite3
import sys
from .candidate_extractor import get_hocr, parse_hocr_lstm_alternatives, generate_candidates

DB_PATH = "candidates.db"

def init_db(db_path=DB_PATH):
    """Initialize database and virtual tables."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS line_metadata (
            id TEXT PRIMARY KEY,
            image_path TEXT,
            label TEXT,
            predicted_lang TEXT,
            initial_ocr TEXT
        )
    """)
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS fts_candidates USING fts5(
            id UNINDEXED,
            candidates
        )
    """)
    conn.commit()
    conn.close()

def build_db(limit_count=100, db_path=DB_PATH):
    """Load manifest, extract top-2 candidates, and save to FTS5 database."""
    init_db(db_path)
    
    manifest_path = "training_data_v2/manifest_w_lang.json"
    if not os.path.exists(manifest_path):
        manifest_path = "training_data_v2/manifest.json"
        
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    entries = []
    for line_id, entry in manifest.items():
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
            base_name = os.path.splitext(os.path.basename(img_relative))[0]
            img_path = os.path.join("training_data_v2/dataset/train", f"{base_name}_base_otsu.png")
            if not os.path.exists(img_path):
                img_path = os.path.join("training_data_v2/dataset/train", f"{base_name}_base_sauvola.png")
                if not os.path.exists(img_path):
                    continue
                    
        hocr = get_hocr(img_path)
        word_choices_list = parse_hocr_lstm_alternatives(hocr)
        
        all_candidates = []
        for wc in word_choices_list:
            cands = generate_candidates(wc, limit=2)
            all_candidates.extend(cands)
            
        candidates_str = " ".join(all_candidates)
        
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

def search_db(term, db_path=DB_PATH):
    """Search for matching terms in the FTS5 table."""
    if not os.path.exists(db_path):
        print(f"Database {db_path} not found. Please run --build first.")
        sys.exit(1)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = """
        SELECT m.id, m.image_path, m.initial_ocr, m.label, f.candidates
        FROM fts_candidates f
        JOIN line_metadata m ON f.id = m.id
        WHERE f.candidates MATCH ?
    """
    
    try:
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
