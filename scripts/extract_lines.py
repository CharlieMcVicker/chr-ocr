#!/usr/bin/env python
import argparse
import sys
import os
import shutil
from PIL import Image

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.layout import extract_columns
from surya.inference import SuryaInferenceManager
from surya.detection import DetectionPredictor
from server.line_utils import crop_pad_normalize_line

def main():
    parser = argparse.ArgumentParser(
        description="Extract and crop text lines from a Cherokee Phoenix scan."
    )
    parser.add_argument(
        "--image",
        default="/Users/charlesmcvicker/code/phoenix/scans/1828-02-28/seq-3.jp2",
        help="Path to the input scan image file",
    )
    parser.add_argument(
        "--output-dir",
        default="line_crops_spike",
        help="Directory to save line crop images and visual report",
    )
    parser.add_argument(
        "--padding-y",
        type=int,
        default=3,
        help="Top/bottom padding in pixels for line crops",
    )
    parser.add_argument(
        "--padding-x",
        type=int,
        default=5,
        help="Left/right padding in pixels for line crops",
    )
    args = parser.parse_args()

    if not os.path.exists(args.image):
        print(f"Error: image '{args.image}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Loading image: {args.image}")
    try:
        pil_img = Image.open(args.image).convert("RGB")
    except Exception as e:
        print(f"Failed to open image: {e}", file=sys.stderr)
        sys.exit(1)

    # Recreate output directory
    if os.path.exists(args.output_dir):
        shutil.rmtree(args.output_dir)
    os.makedirs(args.output_dir, exist_ok=True)

    # Initialize line detector
    print("Using Surya for line detection.")
    detector = DetectionPredictor()

    # Step 1: Detect columns
    print("Step 1: Running layout detection...")
    try:
        columns = extract_columns(pil_img)
    except Exception as e:
        print(f"Layout detection failed: {e}. Falling back to full page.", file=sys.stderr)
        columns = []

    report_lines = []

    if columns:
        print(f"Detected {len(columns)} columns/text blocks.")
        # Sort columns left-to-right by xmin
        columns = sorted(columns, key=lambda c: c["bbox"][0])
        
        for col_idx, col in enumerate(columns):
            print(f"\nProcessing Column {col_idx:02d} (bbox: {col['bbox']})...")
            # Crop and pad the column (NO skew correction)
            margin_x = 20
            margin_y = 20
            c_xmin, c_ymin, c_xmax, c_ymax = col["bbox"]
            c_xmin = max(0, c_xmin - margin_x)
            c_ymin = max(0, c_ymin - margin_y)
            c_xmax = min(pil_img.width, c_xmax + margin_x)
            c_ymax = min(pil_img.height, c_ymax + margin_y)
            
            col_crop = pil_img.crop((c_xmin, c_ymin, c_xmax, c_ymax))
            
            # Save column crop for reference
            col_crop_filename = f"column_{col_idx:02d}.png"
            col_crop.save(os.path.join(args.output_dir, col_crop_filename))
            
            # Run line detection on the column crop
            predictions = detector([col_crop])
            pred = predictions[0]
            
            # Sort lines within column top-to-bottom by ymin
            detected_lines = sorted(pred.bboxes, key=lambda b: b.bbox[1])
            print(f"  Detected {len(detected_lines)} lines in Column {col_idx:02d}.")
            
            col_lines = []
            for line_idx, line in enumerate(detected_lines):
                # Crop, pad, and normalize line
                line_crop, padded_bbox = crop_pad_normalize_line(
                    col_crop, line.bbox, args.padding_x, args.padding_y
                )
                lx1_pad, ly1_pad, lx2_pad, ly2_pad = padded_bbox
                
                line_filename = f"col_{col_idx:02d}_line_{line_idx:03d}.png"
                line_crop.save(os.path.join(args.output_dir, line_filename))
                
                col_lines.append({
                    "filename": line_filename,
                    "bbox": [lx1_pad, ly1_pad, lx2_pad, ly2_pad],
                    "confidence": line.confidence,
                    "index": line_idx
                })
            
            report_lines.append({
                "column_index": col_idx,
                "column_filename": col_crop_filename,
                "column_bbox": col["bbox"],
                "lines": col_lines
            })
    else:
        print("No columns detected or layout detection failed. Processing full page...")
        predictions = detector([pil_img])
        pred = predictions[0]
        
        # Sort top-to-bottom by ymin
        detected_lines = sorted(pred.bboxes, key=lambda b: b.bbox[1])
        print(f"Detected {len(detected_lines)} lines on full page.")
        
        col_lines = []
        for line_idx, line in enumerate(detected_lines):
            # Crop, pad, and normalize line
            line_crop, padded_bbox = crop_pad_normalize_line(
                pil_img, line.bbox, args.padding_x, args.padding_y
            )
            lx1_pad, ly1_pad, lx2_pad, ly2_pad = padded_bbox
            line_filename = f"line_{line_idx:03d}.png"
            line_crop.save(os.path.join(args.output_dir, line_filename))
            
            col_lines.append({
                "filename": line_filename,
                "bbox": [lx1_pad, ly1_pad, lx2_pad, ly2_pad],
                "confidence": line.confidence,
                "index": line_idx
            })
            
        report_lines.append({
            "column_index": 0,
            "column_filename": None,
            "column_bbox": [0, 0, pil_img.width, pil_img.height],
            "lines": col_lines
        })

    # Generate HTML report
    html_path = os.path.join(args.output_dir, "inspect.html")
    print(f"Generating HTML report: {html_path}")
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Line Identification Spike Results</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 24px;
        }
        h1 {
            color: #38bdf8;
            margin-bottom: 8px;
        }
        .subtitle {
            color: #94a3b8;
            margin-bottom: 32px;
        }
        .column-section {
            background-color: #1e293b;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 32px;
            border: 1px solid #334155;
        }
        .column-title {
            font-size: 20px;
            font-weight: 600;
            color: #f1f5f9;
            margin-top: 0;
            margin-bottom: 16px;
            border-bottom: 1px solid #475569;
            padding-bottom: 8px;
        }
        .column-ref {
            max-width: 300px;
            border-radius: 6px;
            border: 1px solid #475569;
            margin-bottom: 16px;
            display: block;
        }
        .lines-table {
            width: 100%;
            border-collapse: collapse;
        }
        .lines-table th {
            text-align: left;
            padding: 12px;
            background-color: #0f172a;
            color: #94a3b8;
            font-size: 14px;
            border-bottom: 2px solid #334155;
        }
        .lines-table td {
            padding: 12px;
            border-bottom: 1px solid #334155;
            vertical-align: middle;
        }
        .line-img-container {
            background-color: #ffffff;
            padding: 8px;
            border-radius: 6px;
            display: inline-block;
        }
        .line-img {
            max-height: 48px;
            display: block;
        }
        .meta-text {
            font-family: monospace;
            font-size: 13px;
            color: #cbd5e1;
        }
        .confidence-badge {
            display: inline-block;
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }
        .conf-high {
            background-color: #064e3b;
            color: #6ee7b7;
        }
        .conf-med {
            background-color: #78350f;
            color: #fcd34d;
        }
        .conf-low {
            background-color: #7f1d1d;
            color: #fca5a5;
        }
    </style>
</head>
<body>
    <h1>Line Identification Spike Report</h1>
    <div class="subtitle">Input Image: """ + os.path.basename(args.image) + """</div>
"""

    for col in report_lines:
        html_content += f"""
    <div class="column-section">
        <div class="column-title">Column {col['column_index']:02d} (BBox: {col['column_bbox']})</div>
"""
        if col['column_filename']:
            html_content += f"""
        <img class="column-ref" src="{col['column_filename']}" alt="Column {col['column_index']}">
"""
        html_content += """
        <table class="lines-table">
            <thead>
                <tr>
                    <th style="width: 80px;">Line #</th>
                    <th>Crop Image</th>
                    <th style="width: 250px;">BBox (relative)</th>
                    <th style="width: 120px;">Confidence</th>
                </tr>
            </thead>
            <tbody>
"""
        for line in col["lines"]:
            conf_class = "conf-high" if line["confidence"] >= 0.9 else ("conf-med" if line["confidence"] >= 0.7 else "conf-low")
            html_content += f"""
                <tr>
                    <td class="meta-text">#{line['index']:03d}</td>
                    <td>
                        <div class="line-img-container">
                            <img class="line-img" src="{line['filename']}" alt="Line {line['index']}">
                        </div>
                    </td>
                    <td class="meta-text">{line['bbox']}</td>
                    <td>
                        <span class="confidence-badge {conf_class}">{line['confidence']:.2f}</span>
                    </td>
                </tr>
"""
        html_content += """
            </tbody>
        </table>
    </div>
"""

    html_content += """
</body>
</html>
"""

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"\nDone! Line crops and report saved to '{args.output_dir}/'")

if __name__ == "__main__":
    main()
