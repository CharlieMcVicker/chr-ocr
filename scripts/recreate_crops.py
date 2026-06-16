import os
import json
import sys
from PIL import Image

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from server.layout import extract_columns

def reconstruct_normalization_params(H_bbox, padding_y=3, target_height=30):
    if H_bbox <= 51:
        return 1.0, max(1, H_bbox - 2 * padding_y)
    for uh in range(30, H_bbox):
        ratio = target_height / uh
        dynamic_pad_y = int(padding_y / ratio)
        if uh + 2 * dynamic_pad_y == H_bbox:
            return ratio, uh
    approx_ratio = 36 / H_bbox
    approx_uh = int(30 / approx_ratio)
    return approx_ratio, approx_uh

# Load manifests
manifests = ["training_data/manifest_w_lang.json", "training_data/manifest.json"]
all_entries = {}

for m_path in manifests:
    if os.path.exists(m_path):
        with open(m_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                if k not in all_entries:
                    all_entries[k] = v

print(f"Total unique entries across manifests: {len(all_entries)}")

# Filter to find missing entries
missing_by_scan = {}
missing_count = 0
ignored_count = 0

for k, item in all_entries.items():
    status = item.get("status", "unlabeled")
    label = item.get("label", "")
    
    # Ignore "not_cherokee" and "bad_crop" (either in status or label)
    if status in ["not_cherokee", "bad_crop"] or label in ["not_cherokee", "bad_crop"]:
        ignored_count += 1
        continue
        
    image_path = os.path.join("training_data", item["image_path"])
    if not os.path.exists(image_path):
        scan = item["source_scan"]
        if scan not in missing_by_scan:
            missing_by_scan[scan] = []
        missing_by_scan[scan].append(item)
        missing_count += 1

print(f"Ignored entries: {ignored_count}")
print(f"Missing crop files: {missing_count} across {len(missing_by_scan)} unique scans.")

# Recreate crops scan by scan
scans_processed = 0
recreated_count = 0

for scan_rel_path, items in missing_by_scan.items():
    scan_path = os.path.join("scans", scan_rel_path)
    if not os.path.exists(scan_path):
        print(f"Warning: Scan file {scan_path} does not exist. Skipping {len(items)} items.")
        continue
        
    print(f"\nProcessing scan [{scans_processed+1}/{len(missing_by_scan)}]: {scan_rel_path}")
    try:
        img_scan = Image.open(scan_path).convert("RGB")
        columns = extract_columns(img_scan)
    except Exception as e:
        print(f"Error loading scan or extracting columns: {e}. Skipping.")
        continue
        
    scans_processed += 1
    
    # Cache column crops to avoid cropping them repeatedly
    col_crops = {}
    
    for item in items:
        col_idx = item["column_index"]
        if col_idx >= len(columns):
            print(f"  Warning: Column index {col_idx} out of range for {item['id']} (only {len(columns)} columns). Skipping.")
            continue
            
        if col_idx not in col_crops:
            col = columns[col_idx]
            margin_x = 20
            margin_y = 20
            c_xmin, c_ymin, c_xmax, c_ymax = col["bbox"]
            c_xmin = max(0, c_xmin - margin_x)
            c_ymin = max(0, c_ymin - margin_y)
            c_xmax = min(img_scan.width, c_xmax + margin_x)
            c_ymax = min(img_scan.height, c_ymax + margin_y)
            col_crops[col_idx] = img_scan.crop((c_xmin, c_ymin, c_xmax, c_ymax))
            
        col_crop = col_crops[col_idx]
        
        # Crop line
        bbox = item["line_bbox"]
        line_crop = col_crop.crop(bbox)
        
        # Reconstruct scaling
        H_bbox = bbox[3] - bbox[1]
        ratio, uh = reconstruct_normalization_params(H_bbox)
        
        if ratio != 1.0:
            new_width = int(line_crop.width * ratio)
            new_height = int(line_crop.height * ratio)
            line_crop = line_crop.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
        # Save crop
        dst_path = os.path.join("training_data", item["image_path"])
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        line_crop.save(dst_path)
        recreated_count += 1
        
print(f"\nSuccessfully recreated {recreated_count}/{missing_count} crop files.")
