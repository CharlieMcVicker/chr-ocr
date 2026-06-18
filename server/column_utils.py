"""
Utility functions for grouping, filtering, and scoring text line crops into columns.
Allows identifying low-confidence columns in the Cherokee Phoenix OCR training dataset.
"""

import json
import os

def load_manifest(manifest_path):
    """
    Loads the training manifest JSON file.
    """
    if not os.path.exists(manifest_path):
        return {}
    try:
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def group_manifest_by_columns(manifest):
    """
    Groups manifest line items by column, uniquely identified by (source_scan, column_index).
    
    Args:
        manifest (dict): The training data manifest.
        
    Returns:
        dict: A dictionary mapping column keys to lists of line dicts sorted by line_index.
    """
    columns = {}
    for item in manifest.values():
        scan = item.get("source_scan")
        col_idx = item.get("column_index")
        if scan is None or col_idx is None:
            continue
            
        col_key = f"{scan}__col__{col_idx}"
        if col_key not in columns:
            columns[col_key] = []
        columns[col_key].append(item)
        
    # Sort lines in each column by line_index ascending
    for col_key in columns:
        columns[col_key].sort(key=lambda x: int(x.get("line_index", 0)))
        
    return columns

def get_low_confidence_columns(manifest_path, threshold=75.0):
    """
    Identifies and analyzes low-confidence columns.
    
    Args:
        manifest_path (str): Path to the training manifest JSON.
        threshold (float): Mean confidence threshold below which a column is considered low-confidence.
        
    Returns:
        list: A sorted list of analyzed column dictionaries with metadata, sorted by mean confidence ascending.
    """
    manifest = load_manifest(manifest_path)
    columns_map = group_manifest_by_columns(manifest)
    
    low_confidence_cols = []
    
    for col_key, lines in columns_map.items():
        if not lines:
            continue
            
        # Extract source_scan and column_index from the first line
        first_line = lines[0]
        source_scan = first_line.get("source_scan")
        column_index = first_line.get("column_index")
        
        # Calculate mean confidence of the column
        confidences = []
        for line in lines:
            # Handle possible missing, None, or string ftm_confidence values
            conf = line.get("ftm_confidence")
            if conf is None or conf == "":
                confidences.append(0.0)
            else:
                try:
                    confidences.append(float(conf))
                except (ValueError, TypeError):
                    confidences.append(0.0)
                    
        mean_conf = sum(confidences) / len(lines) if lines else 0.0
        
        # Count status progress
        unlabeled_count = sum(1 for x in lines if x.get("status", "unlabeled") == "unlabeled")
        labeled_count = sum(1 for x in lines if x.get("status") == "labeled")
        not_cherokee_count = sum(1 for x in lines if x.get("status") == "not_cherokee")
        nasty_crop_count = sum(1 for x in lines if x.get("status") == "nasty_crop")
        
        # If mean confidence is below threshold, add to list
        if mean_conf < threshold:
            low_confidence_cols.append({
                "id": col_key,
                "source_scan": source_scan,
                "column_index": column_index,
                "mean_confidence": round(mean_conf, 2),
                "total_lines": len(lines),
                "unlabeled_count": unlabeled_count,
                "labeled_count": labeled_count,
                "not_cherokee_count": not_cherokee_count,
                "nasty_crop_count": nasty_crop_count,
                "lines": lines
            })
            
    # Sort columns: we want to prioritize columns with unlabeled lines, and then lowest mean confidence
    low_confidence_cols.sort(key=lambda x: (x["unlabeled_count"] == 0, x["mean_confidence"]))
    
    return low_confidence_cols
