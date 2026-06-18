#!/usr/bin/env python3
"""
Active learning pipeline script to extract low-confidence newspaper line crops
containing specified rare/confused characters from pre-existing FTM predictions.
Generates an interactive, beautiful HTML dashboard and JSON summary.
"""

import os
import sys
import json
import shutil
import argparse
from typing import List, Dict, Any

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract low-confidence crops with rare characters from pre-computed fields in manifest_w_lang.json."
    )
    parser.add_argument(
        "--manifest",
        type=str,
        default="training_data/manifest_w_lang.json",
        help="Path to the training manifest JSON file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="training_data/extracted_low_confidence_crops",
        help="Directory where extracted crops and summaries will be stored"
    )
    parser.add_argument(
        "--max-confidence",
        type=float,
        default=85.0,
        help="Maximum confidence threshold (0-100) below which a line is considered low-confidence"
    )
    parser.add_argument(
        "--characters",
        type=str,
        default="4,?,[,],Ꮐ",
        help="Comma-separated list of target characters to scan for in FTM predictions"
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=200,
        help="Maximum number of crops to extract (default: 200)"
    )
    return parser.parse_args()

def generate_html_report(output_dir: str, matches: List[Dict[str, Any]], target_chars: List[str], max_conf: float):
    """
    Generates a beautiful, responsive static HTML dashboard for viewing and verifying the crops.
    """
    html_path = os.path.join(output_dir, "index.html")
    
    # JSON-serialized matches to embed into the page for searching/filtering in the browser
    matches_js = json.dumps(matches, ensure_ascii=False)
    
    # Render option elements for target characters select
    options_html = "".join(f'<option value="{c}">{c}</option>' for c in target_chars)
    target_chars_js = json.dumps(target_chars)
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Active Learning Extraction Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-primary: #3b82f6;
            --accent-success: #10b981;
            --accent-warning: #f59e0b;
            --border-color: #334155;
            --card-bg: rgba(30, 41, 59, 0.7);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            padding: 2rem;
        }

        header {
            max-width: 1200px;
            margin: 0 auto 2rem auto;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 1.5rem;
        }

        h1 {
            font-family: 'Outfit', sans-serif;
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }

        .subtitle {
            color: var(--text-secondary);
            font-size: 1rem;
        }

        .stats-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            max-width: 1200px;
            margin: 0 auto 2rem auto;
        }

        .stat-card {
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        }

        .stat-val {
            font-family: 'Outfit', sans-serif;
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--accent-primary);
            margin-bottom: 0.25rem;
        }

        .stat-label {
            color: var(--text-secondary);
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .search-filters {
            max-width: 1200px;
            margin: 0 auto 2rem auto;
            background: var(--bg-secondary);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            align-items: center;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .filter-group label {
            font-size: 0.85rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .filter-group input, .filter-group select {
            background: var(--bg-primary);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            padding: 0.5rem 1rem;
            color: var(--text-primary);
            font-size: 0.9rem;
            outline: none;
            transition: border-color 0.2s;
        }

        .filter-group input:focus, .filter-group select:focus {
            border-color: var(--accent-primary);
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 1.5rem;
            max-width: 1200px;
            margin: 0 auto;
        }

        .crop-card {
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, border-color 0.2s;
            backdrop-filter: blur(8px);
        }

        .crop-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-primary);
        }

        .image-container {
            background: #2e3b4e;
            padding: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-bottom: 1px solid var(--border-color);
            min-height: 100px;
        }

        .crop-img {
            max-width: 100%;
            max-height: 80px;
            object-fit: contain;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
        }

        .card-content {
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            flex-grow: 1;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .crop-id {
            font-family: monospace;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            max-width: 180px;
        }

        .confidence-badge {
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.75rem;
        }

        .conf-low {
            background-color: rgba(239, 68, 68, 0.2);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .conf-medium {
            background-color: rgba(245, 158, 11, 0.2);
            color: #f59e0b;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }

        .text-section {
            display: flex;
            flex-direction: column;
            gap: 0.4rem;
        }

        .text-label {
            font-size: 0.7rem;
            text-transform: uppercase;
            color: var(--text-secondary);
            font-weight: 600;
            letter-spacing: 0.05em;
        }

        .text-value {
            font-size: 1.1rem;
            font-weight: 500;
            padding: 0.3rem 0.6rem;
            background: rgba(15, 23, 42, 0.5);
            border-radius: 6px;
            border-left: 3px solid var(--accent-primary);
        }

        .text-value.highlight-chars {
            border-left-color: var(--accent-warning);
        }

        .highlight-char {
            color: #fbbf24;
            background: rgba(251, 191, 36, 0.15);
            padding: 0 0.2rem;
            border-radius: 3px;
            font-weight: 700;
        }

        .metadata-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5rem;
            font-size: 0.75rem;
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
            padding-top: 0.75rem;
            margin-top: auto;
        }

        .metadata-item span {
            color: var(--text-primary);
            font-weight: 500;
        }
    </style>
</head>
<body>

    <header>
        <h1>Active Learning Extraction Dashboard</h1>
        <p class="subtitle">Extracted low-confidence line crops containing target rare/confused characters from manifest predictions</p>
    </header>

    <div class="stats-bar">
        <div class="stat-card">
            <div class="stat-val" id="total-crops">0</div>
            <div class="stat-label">Crops Extracted</div>
        </div>
        <div class="stat-card">
            <div class="stat-val">__MAX_CONFIDENCE__%</div>
            <div class="stat-label">Confidence Threshold</div>
        </div>
        <div class="stat-card">
            <div class="stat-val" style="color: var(--accent-warning);">__RARE_CHARS_STR__</div>
            <div class="stat-label">Rare Characters Filtered</div>
        </div>
    </div>

    <div class="search-filters">
        <div class="filter-group" style="flex-grow: 1; min-width: 250px;">
            <label for="search-input">Search OCR Predictions</label>
            <input type="text" id="search-input" placeholder="Type to filter predictions...">
        </div>
        <div class="filter-group">
            <label for="char-select">Specific Rare Character</label>
            <select id="char-select">
                <option value="all">All Targets</option>
                __OPTIONS_HTML__
            </select>
        </div>
        <div class="filter-group">
            <label for="sort-select">Sort By</label>
            <select id="sort-select">
                <option value="conf-asc">Confidence (Low to High)</option>
                <option value="conf-desc">Confidence (High to Low)</option>
                <option value="id">Crop ID</option>
            </select>
        </div>
    </div>

    <div class="grid" id="crops-grid"></div>

    <script>
        const matches = __MATCHES_JS__;
        const targetChars = __TARGET_CHARS_JS__;

        function highlightRareChars(text) {
            if (!text) return "";
            let html = "";
            for (let char of text) {
                if (targetChars.includes(char)) {
                    html += `<span class="highlight-char">${char}</span>`;
                } else {
                    html += char;
                }
            }
            return html;
        }

        function renderCrops() {
            const grid = document.getElementById("crops-grid");
            const searchVal = document.getElementById("search-input").value.toLowerCase();
            const charFilter = document.getElementById("char-select").value;
            const sortBy = document.getElementById("sort-select").value;

            // Apply Filters
            let filtered = matches.filter(m => {
                const textMatch = m.ftm_ocr.toLowerCase().includes(searchVal) || m.id.toLowerCase().includes(searchVal);
                const charMatch = charFilter === "all" ? true : m.ftm_ocr.includes(charFilter);
                return textMatch && charMatch;
            });

            // Apply Sort
            filtered.sort((a, b) => {
                if (sortBy === "conf-asc") return a.ftm_confidence - b.ftm_confidence;
                if (sortBy === "conf-desc") return b.ftm_confidence - a.ftm_confidence;
                return a.id.localeCompare(b.id);
            });

            document.getElementById("total-crops").innerText = filtered.length;

            grid.innerHTML = filtered.map(m => {
                const confClass = m.ftm_confidence < 50 ? "conf-low" : "conf-medium";
                const relativeImgPath = m.extracted_image_path;

                return `
                    <div class="crop-card">
                        <div class="image-container">
                            <img src="${relativeImgPath}" class="crop-img" alt="Crop ${m.id}">
                        </div>
                        <div class="card-content">
                            <div class="card-header">
                                <span class="crop-id" title="${m.id}">${m.id}</span>
                                <span class="confidence-badge ${confClass}">${m.ftm_confidence}% Conf</span>
                            </div>

                            <div class="text-section">
                                <span class="text-label">FTM OCR Prediction</span>
                                <div class="text-value highlight-chars">${highlightRareChars(m.ftm_ocr)}</div>
                            </div>

                            <div class="text-section">
                                <span class="text-label">Initial OCR</span>
                                <div class="text-value" style="font-size: 0.95rem; opacity: 0.85;">${m.initial_ocr || "(empty)"}</div>
                            </div>

                            <div class="metadata-grid">
                                <div class="metadata-item">Status: <span>${m.status}</span></div>
                                <div class="metadata-item">Scan: <span title="${m.source_scan || ''}">${m.source_scan ? m.source_scan.split('/').pop() : 'N/A'}</span></div>
                            </div>
                        </div>
                    </div>
                `;
            }).join("");
        }

        document.getElementById("search-input").addEventListener("input", renderCrops);
        document.getElementById("char-select").addEventListener("change", renderCrops);
        document.getElementById("sort-select").addEventListener("change", renderCrops);

        // Initial render
        renderCrops();
    </script>
</body>
</html>
"""
    
    # Perform clean replacements without f-string escaping headaches
    html_content = html_template.replace("__MATCHES_JS__", matches_js)
    html_content = html_content.replace("__TARGET_CHARS_JS__", target_chars_js)
    html_content = html_content.replace("__MAX_CONFIDENCE__", str(max_conf))
    html_content = html_content.replace("__RARE_CHARS_STR__", ", ".join(target_chars))
    html_content = html_content.replace("__OPTIONS_HTML__", options_html)
    
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated dashboard HTML report at: {html_path}")

def generate_markdown_summary(output_dir: str, matches: List[Dict[str, Any]], target_chars: List[str], max_conf: float):
    """
    Generates a human-readable markdown report summary.
    """
    md_path = os.path.join(output_dir, "summary.md")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(f"# Extracted Low-Confidence Rare Crop Matches\n\n")
        f.write(f"- **Total crops extracted**: {len(matches)}\n")
        f.write(f"- **Confidence Threshold**: <= {max_conf}%\n")
        f.write(f"- **Target Rare Characters scanned**: `{', '.join(target_chars)}`\n\n")
        
        f.write("| Crop ID | Confidence | FTM OCR | Initial OCR | Image Link |\n")
        f.write("| --- | --- | --- | --- | --- |\n")
        
        for m in matches:
            f.write(f"| `{m['id']}` | {m['ftm_confidence']}% | `{m['ftm_ocr']}` | `{m['initial_ocr']}` | [Image]({m['extracted_image_path']}) |\n")
            
    print(f"Generated markdown summary report at: {md_path}")

def main():
    args = parse_args()
    
    manifest_path = args.manifest
    output_dir = args.output_dir
    max_confidence = args.max_confidence
    target_chars = [c.strip() for c in args.characters.split(",") if c.strip()]
    max_results = args.max_results
    
    if not os.path.exists(manifest_path):
        print(f"Error: Manifest file '{manifest_path}' does not exist.", file=sys.stderr)
        sys.exit(1)
        
    print(f"Scanning manifest '{manifest_path}'...")
    print(f"Target characters to look for: {target_chars}")
    print(f"Maximum confidence threshold: {max_confidence}%")
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    matches = []
    
    for key, item in manifest.items():
        # Retrieve needed fields
        ftm_ocr = item.get("ftm_ocr")
        ftm_confidence = item.get("ftm_confidence")
        
        if ftm_ocr is None or ftm_confidence is None:
            continue
            
        # Ignore obvious error markers or un-predicted runs
        if ftm_ocr == "Error" or ftm_ocr == "":
            continue
            
        # Check if confidence meets the threshold
        if ftm_confidence > max_confidence:
            continue
            
        # Check if the OCR contains any of the target characters
        has_rare_char = any(tc in ftm_ocr for tc in target_chars)
        if not has_rare_char:
            continue
            
        matches.append((key, item))
        
    print(f"Found {len(matches)} matching entries in the manifest.")
    
    # Sort matches by confidence (lowest confidence first)
    matches.sort(key=lambda x: x[1].get("ftm_confidence", 100.0))
    
    # Apply limit
    if len(matches) > max_results:
        print(f"Limiting results to the top {max_results} lowest-confidence items.")
        matches = matches[:max_results]
        
    # Prepare output directories
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Copy images and build structured summary data
    extracted_metadata = []
    copied_count = 0
    
    # Base directory of the manifest is used to resolve image paths
    manifest_base_dir = os.path.dirname(manifest_path) or "."
    
    for crop_id, item in matches:
        original_img_rel = item.get("image_path")
        if not original_img_rel:
            continue
            
        # First try relative to the manifest directory
        img_src_path = os.path.join(manifest_base_dir, original_img_rel)
        if not os.path.exists(img_src_path):
            # Fallback relative to current working directory
            img_src_path = original_img_rel
            
        if not os.path.exists(img_src_path):
            print(f"Warning: Image file not found for crop {crop_id}: '{img_src_path}'")
            continue
            
        # Destination file name
        dest_filename = f"{crop_id}{os.path.splitext(img_src_path)[1]}"
        dest_path = os.path.join(images_dir, dest_filename)
        
        try:
            shutil.copy2(img_src_path, dest_path)
            copied_count += 1
            
            # Record relative path from the output_dir root (e.g. index.html) to the copied image
            extracted_image_path = os.path.join("images", dest_filename)
            
            extracted_metadata.append({
                "id": crop_id,
                "initial_ocr": item.get("initial_ocr", ""),
                "ftm_ocr": item.get("ftm_ocr", ""),
                "ftm_confidence": item.get("ftm_confidence", 0.0),
                "status": item.get("status", ""),
                "predicted_lang": item.get("predicted_lang", ""),
                "source_scan": item.get("source_scan", ""),
                "extracted_image_path": extracted_image_path,
                "line_bbox": item.get("line_bbox", [])
            })
        except Exception as e:
            print(f"Error copying image for crop {crop_id}: {e}", file=sys.stderr)
            
    print(f"Successfully copied {copied_count} crop images to '{images_dir}'.")
    
    # Save json summary
    json_path = os.path.join(output_dir, "summary.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(extracted_metadata, f, indent=2, ensure_ascii=False)
    print(f"Saved metadata summary to: {json_path}")
    
    # Generate interactive HTML dashboard
    generate_html_report(output_dir, extracted_metadata, target_chars, max_confidence)
    
    # Generate markdown summary
    generate_markdown_summary(output_dir, extracted_metadata, target_chars, max_confidence)
    
    print("\nExtraction pipeline completed successfully!")

if __name__ == "__main__":
    main()
