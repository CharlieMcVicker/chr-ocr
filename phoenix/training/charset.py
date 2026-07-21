"""
Master character set definition and validation for Cherokee Phoenix OCR.
Ensures that all training runs strictly conform to the required unicharset.
"""

import os
import re
from typing import Set

# Required character set including Cherokee syllabary, punctuation, digits, historic Ꮐ, brackets, and ?
REQUIRED_CHARACTERS: Set[str] = {
    # Core Cherokee Syllabary
    'Ꭰ', 'Ꭱ', 'Ꭲ', 'Ꭳ', 'Ꭴ', 'Ꭵ', 'Ꭶ', 'Ꭷ', 'Ꭸ', 'Ꭹ', 'Ꭺ', 'Ꭻ', 'Ꭼ', 'Ꭽ', 'Ꭾ', 'Ꭿ', 'Ꮀ', 'Ꮁ', 'Ꮂ',
    'Ꮃ', 'Ꮄ', 'Ꮅ', 'Ꮆ', 'Ꮇ', 'Ꮈ', 'Ꮉ', 'Ꮋ', 'Ꮎ', 'Ꮏ', 'Ꮑ', 'Ꮒ', 'Ꮓ', 'Ꮔ', 'Ꮕ', 'Ꮖ', 'Ꮗ',
    'Ꮘ', 'Ꮙ', 'Ꮚ', 'Ꮜ', 'Ꮝ', 'Ꮞ', 'Ꮟ', 'Ꮠ', 'Ꮡ', 'Ꮢ', 'Ꮣ', 'Ꮤ', 'Ꮥ', 'Ꮦ', 'Ꮧ', 'Ꮨ', 'Ꮩ', 'Ꮪ',
    'Ꮫ', 'Ꮬ', 'Ꮭ', 'Ꮮ', 'Ꮯ', 'Ꮰ', 'Ꮱ', 'Ꮲ', 'Ꮳ', 'Ꮴ', 'Ꮵ', 'Ꮶ', 'Ꮷ', 'Ꮸ', 'Ꮹ', 'Ꮺ', 'Ꮻ', 'Ꮼ', 'Ꮽ',
    'Ꮾ', 'Ꮿ', 'Ᏸ', 'Ᏹ', 'Ᏺ', 'Ᏻ', 'Ᏼ',
    # Historic Character
    'Ꮐ',  # U+13C0 (Cherokee Letter Nah)
    # Digits
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    # Punctuation & Brackets
    ',', '.', '!', '?', ';', ':', '-', '’', '“', '”', '(', ')', '[', ']', '…'
}

def parse_unicharset_file(unicharset_path: str) -> Set[str]:
    """
    Extracts set of characters from a Tesseract .lstm-unicharset file.
    """
    characters = set()
    if not os.path.exists(unicharset_path):
        raise FileNotFoundError(f"Unicharset file not found at: {unicharset_path}")

    with open(unicharset_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    # Skip first line if it's the character count header
    start_idx = 1 if lines and lines[0].strip().isdigit() else 0

    for line in lines[start_idx:]:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if parts:
            char = parts[0]
            # Ignore special tesseract tokens
            if char in ("NULL", "Joined", "|Broken|0|1"):
                continue
            characters.add(char)
    return characters

def validate_unicharset(unicharset_path: str) -> bool:
    """
    Validates that a unicharset file contains all REQUIRED_CHARACTERS.
    Raises ValueError if any required character is missing.
    """
    present_chars = parse_unicharset_file(unicharset_path)
    missing = REQUIRED_CHARACTERS - present_chars
    if missing:
        raise ValueError(
            f"Unicharset validation failed for {unicharset_path}! "
            f"Missing required characters ({len(missing)}): {sorted(list(missing))}"
        )
    return True
