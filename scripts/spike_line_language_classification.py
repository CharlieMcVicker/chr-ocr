#!/usr/bin/env python3
import argparse
import sys
import os
import shutil
import json
from PIL import Image

# Ensure server package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.layout import extract_columns
from surya.inference import SuryaInferenceManager
from surya.detection import DetectionPredictor
from server.line_utils import crop_pad_normalize_line
from server.process_file import ocr_image_to_text
from scripts.classify_layout import analyze_text

def analyze_ocr_result(text):
    """Reuse existing analyze_text but return basic metrics"""
    analysis = analyze_text(text)
    return {
        "text": text.strip(),
        "total": analysis["cherokee_count"] + analysis["latin_count"],
        "cherokee_count": analysis["cherokee_count"],
        "latin_count": analysis["latin_count"],
        "classification": analysis["classification"]
    }

def main():
    parser = argparse.ArgumentParser(
        description="Spike: Extract lines and compare OCR language models to classify line language."
    )
    parser.add_argument(
        "--image",
        default="/Users/charlesmcvicker/code/phoenix/scans/1828-02-28/seq-3.jp2",
        help="Path to the input scan image file",
    )
    parser.add_argument(
        "--output-dir",
        default="spike_line_classification_output",
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

    print("Using Surya for line detection.")
    detector = DetectionPredictor()

    print("Step 1: Running layout detection...")
    try:
        columns = extract_columns(pil_img)
    except Exception as e:
        print(f"Layout detection failed: {e}.", file=sys.stderr)
        sys.exit(1)

    report_lines = []

    if columns:
        print(f"Detected {len(columns)} columns/text blocks.")
        
        for col_idx, col in enumerate(columns):
            print(f"\nProcessing Column {col_idx:02d}...")
            margin_x = 20
            margin_y = 20
            c_xmin, c_ymin, c_xmax, c_ymax = col["bbox"]
            c_xmin = max(0, c_xmin - margin_x)
            c_ymin = max(0, c_ymin - margin_y)
            c_xmax = min(pil_img.width, c_xmax + margin_x)
            c_ymax = min(pil_img.height, c_ymax + margin_y)
            
            col_crop = pil_img.crop((c_xmin, c_ymin, c_xmax, c_ymax))
            
            # Analyze column language first
            col_ocr = ocr_image_to_text(col_crop, lang="chr+eng")
            col_analysis = analyze_text(col_ocr)
            col_lang = col_analysis["classification"]
            
            print(f"  Column {col_idx:02d} is classified as: {col_lang}")
            
            # Only process "Mixed" columns for this spike to keep it focused
            if col_lang != "Mixed":
                print(f"  Skipping column {col_idx:02d} because it is {col_lang}, not Mixed.")
                continue
                
            col_crop_filename = f"column_{col_idx:02d}.png"
            col_crop.save(os.path.join(args.output_dir, col_crop_filename))
            
            predictions = detector([col_crop])
            pred = predictions[0]
            
            detected_lines = sorted(pred.bboxes, key=lambda b: b.bbox[1])[:20]
            print(f"  Detected {len(pred.bboxes)} lines in Column {col_idx:02d}, analyzing first 20.")
            
            col_lines_data = []
            for line_idx, line in enumerate(detected_lines):
                line_crop, padded_bbox = crop_pad_normalize_line(
                    col_crop, line.bbox, args.padding_x, args.padding_y
                )
                
                line_filename = f"col_{col_idx:02d}_line_{line_idx:03d}.png"
                line_crop.save(os.path.join(args.output_dir, line_filename))
                
                # Run OCR across 3 languages
                res_chreng = ocr_image_to_text(line_crop, lang="chr+eng")
                res_chr = ocr_image_to_text(line_crop, lang="chr")
                res_eng = ocr_image_to_text(line_crop, lang="eng")
                
                analysis_chreng = analyze_ocr_result(res_chreng)
                analysis_chr = analyze_ocr_result(res_chr)
                analysis_eng = analyze_ocr_result(res_eng)
                
                col_lines_data.append({
                    "filename": line_filename,
                    "index": line_idx,
                    "confidence": line.confidence,
                    "ocr_chreng": analysis_chreng,
                    "ocr_chr": analysis_chr,
                    "ocr_eng": analysis_eng
                })
            
            report_lines.append({
                "column_index": col_idx,
                "column_filename": col_crop_filename,
                "lines": col_lines_data
            })
    else:
        print("No columns detected.")
        sys.exit(1)

    # Generate HTML report
    html_path = os.path.join(args.output_dir, "inspect.html")
    print(f"Generating HTML report: {html_path}")
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Line Language Classification Spike Report</title>
    <style>
        body { font-family: sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }
        .column-section { background-color: #1e293b; border-radius: 12px; padding: 20px; margin-bottom: 32px; border: 1px solid #334155; }
        table { width: 100%; border-collapse: collapse; }
        th { text-align: left; padding: 12px; background-color: #0f172a; color: #94a3b8; font-size: 14px; border-bottom: 2px solid #334155; }
        td { padding: 12px; border-bottom: 1px solid #334155; vertical-align: top; }
        .line-img { max-height: 48px; background-color: white; padding: 4px; border-radius: 4px; }
        .metric-block { font-family: monospace; font-size: 12px; background: #0f172a; padding: 8px; border-radius: 4px; margin-bottom: 4px; white-space: pre-wrap; word-break: break-all;}
        .cherokee-text { color: #38bdf8; }
        .english-text { color: #f472b6; }
        .mixed-text { color: #fbbf24; }
        .empty-text { color: #94a3b8; }
    </style>
</head>
<body>
    <h1>Line Language Classification Spike Report</h1>
    <p>Comparing Tesseract results with chr+eng, chr, and eng models on Mixed column lines.</p>
"""

    for col in report_lines:
        html_content += f"""
    <div class="column-section">
        <h2>Column {col['column_index']:02d}</h2>
        <img src="{col['column_filename']}" style="max-height: 200px; border-radius: 4px; margin-bottom: 16px;">
        <table>
            <thead>
                <tr>
                    <th style="width: 50px;">Line</th>
                    <th style="width: 30%;">Image</th>
                    <th style="width: 23%;">chr+eng Model</th>
                    <th style="width: 23%;">chr Model</th>
                    <th style="width: 23%;">eng Model</th>
                </tr>
            </thead>
            <tbody>
"""
        for line in col["lines"]:
            def render_ocr_block(data):
                color_class = {
                    "Cherokee": "cherokee-text",
                    "English": "english-text",
                    "Mixed": "mixed-text",
                    "Empty": "empty-text"
                }.get(data['classification'], "empty-text")
                
                return f"""
                <div class="metric-block">
                    <div><b>Text:</b> {data['text']}</div>
                    <div style="margin-top:4px;"><b>Class:</b> <span class="{color_class}">{data['classification']}</span></div>
                    <div><b>Chr/Lat/Tot:</b> {data['cherokee_count']} / {data['latin_count']} / {data['total']}</div>
                </div>
                """

            html_content += f"""
                <tr>
                    <td>#{line['index']:03d}</td>
                    <td><img class="line-img" src="{line['filename']}"></td>
                    <td>{render_ocr_block(line['ocr_chreng'])}</td>
                    <td>{render_ocr_block(line['ocr_chr'])}</td>
                    <td>{render_ocr_block(line['ocr_eng'])}</td>
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

    print(f"\nDone! Report saved to '{args.output_dir}/inspect.html'")

if __name__ == "__main__":
    main()
