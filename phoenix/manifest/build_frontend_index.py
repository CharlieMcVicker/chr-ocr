import os
import json

def main():
    manifest_path = "training_data/manifest_w_lang.json"
    if not os.path.exists(manifest_path):
        print(f"Error: {manifest_path} not found.")
        return

    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    # Group by (source_scan, column_index)
    columns = {}
    for key, entry in manifest.items():
        scan = entry.get("source_scan", "unknown_scan")
        col_idx = entry.get("column_index", 0)
        
        col_key = f"{scan.replace('/', '_').replace('.', '_')}_col_{col_idx:02d}"
        
        if col_key not in columns:
            columns[col_key] = {
                "id": col_key,
                "source_scan": scan,
                "column_index": col_idx,
                "lines": []
            }
            
        columns[col_key]["lines"].append({
            "id": entry["id"],
            "line_index": entry.get("line_index", 0),
            "bbox": entry.get("line_bbox", [0, 0, 100, 50]),
            "text": entry.get("initial_ocr", ""),
            "label": entry.get("label", "")
        })

    # Filter out columns with no lines, and sort lines by line_index or top-to-bottom y-coordinate
    compiled_columns = []
    for col_key, col in columns.items():
        if not col["lines"]:
            continue
        # Sort by ymin (bbox[1]) to ensure natural top-to-bottom reading
        col["lines"].sort(key=lambda x: x["bbox"][1])
        
        # Calculate full column bounding box to normalize line coordinates
        xmins = [line["bbox"][0] for line in col["lines"]]
        ymins = [line["bbox"][1] for line in col["lines"]]
        xmaxs = [line["bbox"][2] for line in col["lines"]]
        ymaxs = [line["bbox"][3] for line in col["lines"]]
        
        col_xmin = min(xmins) - 20
        col_ymin = min(ymins) - 20
        col_xmax = max(xmaxs) + 20
        col_ymax = max(ymaxs) + 20
        
        col["bbox"] = [col_xmin, col_ymin, col_xmax, col_ymax]
        col["width"] = col_xmax - col_xmin
        col["height"] = col_ymax - col_ymin
        
        # Normalize line bboxes to be relative to the column crop
        for line in col["lines"]:
            line_xmin, line_ymin, line_xmax, line_ymax = line["bbox"]
            line["relative_bbox"] = [
                line_xmin - col_xmin,
                line_ymin - col_ymin,
                line_xmax - col_xmin,
                line_ymax - col_ymin
            ]
            
        compiled_columns.append(col)

    # Let's sort compiled columns so the list is stable
    compiled_columns.sort(key=lambda x: x["id"])
    
    # We only need a reasonable number of columns for the frontend demonstration,
    # let's write all of them or a subset of e.g. 50 columns to keep the file size highly optimized.
    output_path = "frontend/public/ocr_data.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(compiled_columns[:100], f, indent=2, ensure_ascii=False)
        
    print(f"Successfully compiled {len(compiled_columns[:100])} columns to {output_path}")

if __name__ == "__main__":
    main()
