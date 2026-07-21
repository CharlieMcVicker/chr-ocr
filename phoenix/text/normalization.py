import unicodedata

def normalize_truth(text: str) -> str:
    """
    Centralized ground-truth text normalization.
    Performs:
    1. Unicode NFC normalization.
    2. Cherokee lowercase to uppercase conversion.
    3. Replacement of fancy/curly quotes with standard ASCII quotes (' and ").
    4. Whitespace standardisation (whitespace replacement and stripping).
    """
    if not text:
        return ""
    
    # 1. Unicode NFC normalization
    normalized = unicodedata.normalize("NFC", text)
    
    # 2. Convert Cherokee lowercase to uppercase
    normalized = normalized.upper()
    
    # 3. Replace fancy/curly quotes with ASCII equivalents
    normalized = normalized.replace("’", "'").replace("‘", "'").replace("`", "'")
    normalized = normalized.replace("“", '"').replace("”", '"')
    
    # 4. Whitespace normalization (replace multiple whitespace with a single space, strip)
    normalized = " ".join(normalized.split())
    
    return normalized
