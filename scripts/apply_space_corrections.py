#!/usr/bin/env python3
import os
import json
import argparse
from scripts.find_missing_spaces import find_missing_spaces

def load_exclusions(exclusions_path):
    if not exclusions_path or not os.path.exists(exclusions_path):
        return None
    try:
        with open(exclusions_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Failed to load exclusions from {exclusions_path}: {e}")
        return None

def is_excluded(verse_key, original_word, exclusions):
    if not exclusions:
        return False
    if isinstance(exclusions, list):
        for item in exclusions:
            if isinstance(item, dict):
                if item.get("verse_key") == verse_key and item.get("original_word") == original_word:
                    return True
            elif isinstance(item, str):
                if item == f"{verse_key}:{original_word}":
                    return True
    elif isinstance(exclusions, dict):
        if verse_key in exclusions:
            val = exclusions[verse_key]
            if isinstance(val, list):
                return original_word in val
            elif isinstance(val, str):
                return original_word == val
    return False

def apply_replacement(cherokee_text, original_word, suggested_split):
    words = cherokee_text.split()
    changed = False
    for idx, w in enumerate(words):
        if w == original_word:
            words[idx] = suggested_split
            changed = True
    if changed:
        return " ".join(words), True
    return cherokee_text, False

def apply_space_corrections(book_dir, exclusions_path=None):
    aligned_manifest_path = os.path.join(book_dir, "aligned_manifest.json")
    if not os.path.exists(aligned_manifest_path):
        print(f"No aligned manifest found at {aligned_manifest_path}. Cannot detect missing spaces.")
        return 0

    segment_map_path = os.path.join(book_dir, "segment_map.json")
    metadata_path = os.path.join(book_dir, "metadata.json")

    if not os.path.exists(segment_map_path) or not os.path.exists(metadata_path):
        print(f"Error: segment_map.json or metadata.json not found in {book_dir}")
        return 0

    print("Running missing space detection...")
    candidates = find_missing_spaces(aligned_manifest_path)
    if not candidates:
        print("No missing space candidates detected.")
        return 0

    if exclusions_path is None:
        exclusions_path = os.path.join(book_dir, "space_correction_exclusions.json")
    exclusions = load_exclusions(exclusions_path)

    # Filter candidates based on exclusions
    active_corrections = []
    for c in candidates:
        vk = c["verse_key"]
        orig = c["original_word"]
        sugg = c["suggested_split"]
        if is_excluded(vk, orig, exclusions):
            print(f"Excluding correction for verse {vk}: '{orig}' -> '{sugg}'")
        else:
            active_corrections.append(c)

    if not active_corrections:
        print("All detected candidates are excluded or no new corrections to apply.")
        return 0

    # Load segment_map and metadata
    with open(segment_map_path, "r", encoding="utf-8") as f:
        segment_map = json.load(f)
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    applied_count = 0
    for c in active_corrections:
        vk = c["verse_key"]
        orig = c["original_word"]
        sugg = c["suggested_split"]

        # Apply to segment_map
        if vk in segment_map and "cherokee" in segment_map[vk]:
            new_text, changed = apply_replacement(segment_map[vk]["cherokee"], orig, sugg)
            if changed:
                segment_map[vk]["cherokee"] = new_text
                applied_count += 1
                print(f"Applied space correction in segment_map.json for {vk}: '{orig}' -> '{sugg}'")

        # Apply to metadata
        if vk in metadata and "cherokee" in metadata[vk]:
            new_text, changed = apply_replacement(metadata[vk]["cherokee"], orig, sugg)
            if changed:
                metadata[vk]["cherokee"] = new_text
                print(f"Applied space correction in metadata.json for {vk}: '{orig}' -> '{sugg}'")

    if applied_count > 0:
        with open(segment_map_path, "w", encoding="utf-8") as f:
            json.dump(segment_map, f, ensure_ascii=False, indent=2)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"Successfully saved updated segment_map.json and metadata.json with {applied_count} corrections.")
    else:
        print("No changes were applied to files.")

    return applied_count

def main():
    parser = argparse.ArgumentParser(description="Apply detected space corrections to segment_map.json and metadata.json.")
    parser.add_argument("--book-dir", default="training_data/cnt/book_01", help="Book directory path containing JSON files")
    parser.add_argument("--exclusions", default=None, help="Path to space_correction_exclusions.json")
    args = parser.parse_args()

    apply_space_corrections(args.book_dir, args.exclusions)

if __name__ == "__main__":
    main()
