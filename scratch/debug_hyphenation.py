#!/usr/bin/env python3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.align_verses import preprocess_hyphenated_words

def test_hyphenation():
    # Matthew 1:5 ground truth words
    cherokee_gt = "ᏌᎵᎹᏃ ᏉᏏ ᎤᏕᏁᎴᎢ ᎴᎭᏫ ᎤᎾᎸᎪᏫᏎᎢ; ᏉᏏᏃ ᎣᏇᏗ ᎤᏕᏁᎴᎢ ᎷᏏ ᎤᎾᏄᎪᏫᏎᎢ; ᎣᏇᏗᏃ ᏤᏏ ᎤᏕᏁᎴᎢ;"
    words = cherokee_gt.split()
    
    # Stock OCR lines for Matthew 1:5
    stock_ocrs = [
        "Ꮦ ᏌᎵᎹᏃ ᏉᏏ ᎤᏕᏁᎴᎢ ᎴᎭᏫ",
        "ᎤᎾᏄᎪᏫᏎᎢ Ꮆ ᏉᏏᏃ ᏇᏇᏘ ᎤᏕᏁᎴᎢ",
        "ᎷᏏ ᎤᎧᏄᎪᏫᏎᎢ 3 ᏇᏇᏘᏃ ᏤᏏ ᎤᏕ-",
        "ᏁᎴᎢ 5"
    ]
    
    # Fine-tuned OCR lines for Matthew 1:5
    ftm_ocrs = [
        "5 ᏌᎹᏃ ᏉᏏ ᎤᏕᏁᎴᎢ ᎴᎭᎾᏫ",
        "ᎤᎾᏄᎪᏫᏎᎢ; ᏉᏏᏃ ᎣᏇᏗ ᎤᏕᏁᎴᎢ",
        "ᎷᏏ ᎤᎾᏄᎪᏫᏎᎢ ;Ꮆ ᎧᏇᏗᏃ ᏤᏏ ᎤᏕ-",
        "ᏁᎴᎢ;"
    ]
    
    print("=== Original GT Words ===")
    print(words)
    print()
    
    print("=== Processing Stock OCR ===")
    processed_stock = preprocess_hyphenated_words(words, stock_ocrs)
    print("Processed words:")
    print(processed_stock)
    print()
    
    print("=== Processing Fine-tuned OCR ===")
    processed_ftm = preprocess_hyphenated_words(words, ftm_ocrs)
    print("Processed words:")
    print(processed_ftm)
    print()

if __name__ == "__main__":
    test_hyphenation()
