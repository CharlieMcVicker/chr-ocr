#!/usr/bin/env python3
import os
import json
import Levenshtein

def main():
    aligned_manifest_path = "training_data/cnt/book_01/aligned_manifest.json"
    book_dir = "training_data/cnt/book_01"
    output_html_path = os.path.join(book_dir, "ocr_viewer.html")

    if not os.path.exists(aligned_manifest_path):
        print(f"Error: Aligned manifest not found at {aligned_manifest_path}")
        return

    with open(aligned_manifest_path, "r", encoding="utf-8") as f:
        aligned_data = json.load(f)

    records = []
    
    total_confs = 0.0
    total_cers = 0.0
    valid_lines = 0

    for verse_key, info in aligned_data.items():
        verse_num = info.get("verse_number", "")
        lines = info.get("lines", [])
        for line_idx, line in enumerate(lines):
            ftm_aligned = line.get("ftm_aligned", "").strip()
            ftm_raw_ocr = line.get("ftm_raw_ocr", "").strip()
            ftm_conf = line.get("ftm_confidence", 0.0)

            # Ignore lines with no ground truth if any
            if not ftm_aligned:
                continue

            edit_dist = Levenshtein.distance(ftm_raw_ocr, ftm_aligned)
            cer = edit_dist / max(1, len(ftm_aligned))

            # Categorization
            if ftm_conf >= 80.0 and edit_dist > 0:
                category = "confidently_disagrees"
            elif ftm_conf < 70.0:
                category = "low_confidence"
            else:
                category = "high_confidence_correct" if edit_dist == 0 else "low_error_other"

            records.append({
                "verse_key": verse_key,
                "verse_number": verse_num,
                "line_idx": line_idx,
                "line_crop": line["line_crop"], # relative path e.g. line_crops/010101_line_00.png
                "ftm_aligned": ftm_aligned,
                "ftm_raw_ocr": ftm_raw_ocr,
                "ftm_confidence": ftm_conf,
                "cer": round(cer * 100, 2), # percentage
                "edit_distance": edit_dist,
                "category": category
            })

            total_confs += ftm_conf
            total_cers += cer
            valid_lines += 1

    # Sort records initially by CER descending
    records.sort(key=lambda x: x["cer"], reverse=True)

    # HTML template with embedded JSON records and sleek responsive UX
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cherokee NT OCR Performance Dashboard</title>
    <!-- Outfit Font -->
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0b0f19;
            --panel-bg: rgba(17, 24, 39, 0.75);
            --card-bg: rgba(31, 41, 55, 0.5);
            --accent-color: #6366f1;
            --accent-hover: #4f46e5;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: rgba(255, 255, 255, 0.08);
            --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Outfit', sans-serif;
            padding: 2rem;
            min-height: 100vh;
            background-image: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.05) 0%, transparent 40%),
                              radial-gradient(circle at 90% 80%, rgba(16, 185, 129, 0.05) 0%, transparent 40%);
        }}

        header {{
            margin-bottom: 2rem;
        }}

        .logo-area {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1.5rem;
        }}

        h1 {{
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(to right, #818cf8, #34d399);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .badge-total {{
            background: rgba(99, 102, 241, 0.15);
            border: 1px solid rgba(99, 102, 241, 0.3);
            color: #818cf8;
            padding: 0.4rem 1rem;
            border-radius: 9999px;
            font-size: 0.9rem;
            font-weight: 600;
        }}

        /* Stats Cards */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: var(--panel-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            box-shadow: var(--shadow);
            position: relative;
            overflow: hidden;
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background: var(--accent-color);
        }}

        .stat-card.danger::before {{ background: var(--danger); }}
        .stat-card.warning::before {{ background: var(--warning); }}
        .stat-card.success::before {{ background: var(--success); }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.5rem;
        }}

        .stat-val {{
            font-size: 1.8rem;
            font-weight: 700;
        }}

        /* Toolbar Controls */
        .toolbar {{
            background: var(--panel-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.25rem;
            backdrop-filter: blur(12px);
            box-shadow: var(--shadow);
            margin-bottom: 2rem;
            display: flex;
            flex-wrap: wrap;
            gap: 1.5rem;
            align-items: center;
            justify-content: space-between;
        }}

        .filters-group {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            padding: 0.6rem 1.2rem;
            border-radius: 10px;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}

        .filter-btn:hover {{
            background: rgba(255, 255, 255, 0.1);
            color: var(--text-primary);
        }}

        .filter-btn.active {{
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}

        .controls-group {{
            display: flex;
            gap: 1rem;
            flex-grow: 1;
            max-width: 600px;
        }}

        .search-input {{
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.6rem 1rem;
            border-radius: 10px;
            font-size: 0.9rem;
            width: 100%;
            outline: none;
            transition: border-color 0.2s;
            font-family: inherit;
        }}

        .search-input:focus {{
            border-color: var(--accent-color);
        }}

        .sort-select {{
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border);
            color: var(--text-primary);
            padding: 0.6rem 1rem;
            border-radius: 10px;
            font-size: 0.9rem;
            outline: none;
            cursor: pointer;
            font-family: inherit;
            min-width: 160px;
        }}

        /* Grid */
        .list-container {{
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }}

        .card {{
            background: var(--panel-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1.5rem;
            backdrop-filter: blur(12px);
            box-shadow: var(--shadow);
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .card:hover {{
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.15);
        }}

        .card-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.75rem;
        }}

        .ref-info {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #818cf8;
        }}

        .card-tags {{
            display: flex;
            gap: 0.5rem;
        }}

        .tag {{
            font-size: 0.75rem;
            font-weight: 600;
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            text-transform: uppercase;
        }}

        .tag.confidently_disagrees {{
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }}

        .tag.low_confidence {{
            background: rgba(245, 158, 11, 0.15);
            color: #fbbf24;
            border: 1px solid rgba(245, 158, 11, 0.3);
        }}

        .tag.high_confidence_correct {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .tag.low_error_other {{
            background: rgba(107, 114, 128, 0.15);
            color: #9ca3af;
            border: 1px solid rgba(107, 114, 128, 0.3);
        }}

        /* Image Display */
        .image-frame {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 0.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 80px;
        }}

        .crop-img {{
            max-height: 55px;
            max-width: 100%;
            object-fit: contain;
            filter: brightness(0.9) contrast(1.1);
        }}

        /* Text Diff Box */
        .diff-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.5rem;
        }}

        @media (max-width: 768px) {{
            .diff-grid {{
                grid-template-columns: 1fr;
                gap: 1rem;
            }}
        }}

        .text-panel {{
            background: rgba(0, 0, 0, 0.2);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1rem;
            position: relative;
        }}

        .panel-label {{
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            position: absolute;
            top: -0.6rem;
            left: 0.8rem;
            background: #111827;
            padding: 0 0.5rem;
            border-radius: 4px;
            border: 1px solid var(--border);
        }}

        .text-content {{
            font-size: 1.15rem;
            line-height: 1.6;
            margin-top: 0.25rem;
            white-space: pre-wrap;
            word-break: break-all;
        }}

        /* Metric Highlights */
        .card-metrics {{
            display: flex;
            gap: 2rem;
            margin-top: 0.5rem;
        }}

        .metric-item {{
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }}

        .metric-lbl {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        .metric-val-group {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .metric-val {{
            font-size: 1.1rem;
            font-weight: 700;
        }}

        .metric-bar-outer {{
            width: 80px;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            overflow: hidden;
        }}

        .metric-bar-inner {{
            height: 100%;
            border-radius: 3px;
        }}

        /* Diff Highlights */
        .del {{
            background-color: rgba(239, 68, 68, 0.3);
            text-decoration: line-through;
            border-radius: 2px;
            padding: 0 2px;
        }}

        .ins {{
            background-color: rgba(16, 185, 129, 0.3);
            border-radius: 2px;
            padding: 0 2px;
        }}

        .empty-state {{
            text-align: center;
            padding: 4rem;
            color: var(--text-secondary);
            font-size: 1.2rem;
            background: var(--panel-bg);
            border: 1px solid var(--border);
            border-radius: 16px;
        }}
    </style>
</head>
<body>

    <header>
        <div class="logo-area">
            <h1>Cherokee NT OCR Performance Dashboard</h1>
            <span class="badge-total" id="total-count-badge">0 Lines Loaded</span>
        </div>

        <div class="stats-grid">
            <div class="stat-card danger">
                <div class="stat-label">Confidently Disagrees</div>
                <div class="stat-val" id="stat-conf-disagree">0</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-label">Low Confidence</div>
                <div class="stat-val" id="stat-low-conf">0</div>
            </div>
            <div class="stat-card success">
                <div class="stat-label">Mean Confidence</div>
                <div class="stat-val" id="stat-mean-conf">0.0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Mean CER</div>
                <div class="stat-val" id="stat-mean-cer">0.0%</div>
            </div>
        </div>
    </header>

    <div class="toolbar">
        <div class="filters-group">
            <button class="filter-btn active" onclick="setFilter('all')">All</button>
            <button class="filter-btn" onclick="setFilter('confidently_disagrees')">Confidently Disagrees</button>
            <button class="filter-btn" onclick="setFilter('low_confidence')">Low Confidence</button>
            <button class="filter-btn" onclick="setFilter('high_confidence_correct')">Correct</button>
        </div>

        <div class="controls-group">
            <input type="text" id="search-box" class="search-input" placeholder="Search by Ground Truth or OCR text..." oninput="handleSearch()">
            <select id="sort-select" class="sort-select" onchange="handleSort()">
                <option value="cer-desc">CER (High &rarr; Low)</option>
                <option value="cer-asc">CER (Low &rarr; High)</option>
                <option value="conf-desc">Confidence (High &rarr; Low)</option>
                <option value="conf-asc">Confidence (Low &rarr; High)</option>
                <option value="ref-asc">Verse Reference</option>
            </select>
        </div>
    </div>

    <div id="list-container" class="list-container">
        <!-- Cards will be dynamically injected here -->
    </div>

    <script>
        // Injected data payload
        const records = {json.dumps(records, ensure_ascii=False)};

        let currentFilter = 'all';
        let searchQuery = '';
        let currentSort = 'cer-desc';

        function init() {{
            calculateStats();
            render();
        }}

        function calculateStats() {{
            const total = records.length;
            const confidentlyDisagrees = records.filter(r => r.category === 'confidently_disagrees').length;
            const lowConfidence = records.filter(r => r.category === 'low_confidence').length;
            
            let sumConf = 0;
            let sumCer = 0;
            records.forEach(r => {{
                sumConf += r.ftm_confidence;
                sumCer += r.cer;
            }});

            const meanConf = total > 0 ? (sumConf / total).toFixed(1) : 0.0;
            const meanCer = total > 0 ? (sumCer / total).toFixed(1) : 0.0;

            document.getElementById('total-count-badge').textContent = `${{total}} Lines Total`;
            document.getElementById('stat-conf-disagree').textContent = confidentlyDisagrees;
            document.getElementById('stat-low-conf').textContent = lowConfidence;
            document.getElementById('stat-mean-conf').textContent = `${{meanConf}}%`;
            document.getElementById('stat-mean-cer').textContent = `${{meanCer}}%`;
        }}

        function setFilter(filterType) {{
            currentFilter = filterType;
            // Update active states
            const buttons = document.querySelectorAll('.filter-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            render();
        }}

        function handleSearch() {{
            searchQuery = document.getElementById('search-box').value.toLowerCase().trim();
            render();
        }}

        function handleSort() {{
            currentSort = document.getElementById('sort-select').value;
            render();
        }}

        // Simple LCS algorithm to compute text diff between GT (str1) and OCR (str2)
        function generateDiff(gt, ocr) {{
            const gtChars = Array.from(gt);
            const ocrChars = Array.from(ocr);
            
            const dp = Array(gtChars.length + 1).fill(null).map(() => Array(ocrChars.length + 1).fill(0));
            
            for (let i = 1; i <= gtChars.length; i++) {{
                for (let j = 1; j <= ocrChars.length; j++) {{
                    if (gtChars[i - 1] === ocrChars[j - 1]) {{
                        dp[i][j] = dp[i - 1][j - 1] + 1;
                    }} else {{
                        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
                    }}
                }}
            }}

            let i = gtChars.length;
            let j = ocrChars.length;
            let diffGt = [];
            let diffOcr = [];

            while (i > 0 || j > 0) {{
                if (i > 0 && j > 0 && gtChars[i - 1] === ocrChars[j - 1]) {{
                    diffGt.unshift(gtChars[i - 1]);
                    diffOcr.unshift(ocrChars[j - 1]);
                    i--;
                    j--;
                }} else if (j > 0 && (i === 0 || dp[i][j - 1] >= dp[i - 1][j])) {{
                    diffOcr.unshift(`<span class="ins">${{ocrChars[j - 1]}}</span>`);
                    j--;
                }} else {{
                    diffGt.unshift(`<span class="del">${{gtChars[i - 1]}}</span>`);
                    i--;
                }}
            }}

            return {{
                gtHtml: diffGt.join(''),
                ocrHtml: diffOcr.join('')
            }};
        }}

        function getCategoryLabel(cat) {{
            switch(cat) {{
                case 'confidently_disagrees': return 'Confidently Disagrees';
                case 'low_confidence': return 'Low Confidence';
                case 'high_confidence_correct': return 'Correct';
                case 'low_error_other': return 'Low Error';
                default: return cat;
            }}
        }}

        function getConfColor(conf) {{
            if (conf >= 80) return 'var(--success)';
            if (conf >= 70) return 'var(--warning)';
            return 'var(--danger)';
        }}

        function getCerColor(cer) {{
            if (cer === 0) return 'var(--success)';
            if (cer < 10) return 'var(--warning)';
            return 'var(--danger)';
        }}

        function render() {{
            let filtered = [...records];

            // Apply category filter
            if (currentFilter !== 'all') {{
                filtered = filtered.filter(r => r.category === currentFilter);
            }}

            // Apply search
            if (searchQuery) {{
                filtered = filtered.filter(r => 
                    r.ftm_aligned.toLowerCase().includes(searchQuery) ||
                    r.ftm_raw_ocr.toLowerCase().includes(searchQuery) ||
                    r.verse_key.includes(searchQuery)
                );
            }}

            // Apply sort
            filtered.sort((a, b) => {{
                if (currentSort === 'cer-desc') return b.cer - a.cer;
                if (currentSort === 'cer-asc') return a.cer - b.cer;
                if (currentSort === 'conf-desc') return b.ftm_confidence - a.ftm_confidence;
                if (currentSort === 'conf-asc') return a.ftm_confidence - b.ftm_confidence;
                if (currentSort === 'ref-asc') {{
                    if (a.verse_key !== b.verse_key) {{
                        return a.verse_key.localeCompare(b.verse_key);
                    }}
                    return a.line_idx - b.line_idx;
                }}
                return 0;
            }});

            const container = document.getElementById('list-container');
            container.innerHTML = '';

            if (filtered.length === 0) {{
                container.innerHTML = '<div class="empty-state">No matching records found. Try adjusting your filter or search.</div>';
                return;
            }}

            filtered.forEach(r => {{
                const ch = parseInt(r.verse_key.substring(2, 4));
                const v = parseInt(r.verse_key.substring(4, 6));
                const refText = `Matthew ${{ch}}:${{v}}, Line ${{r.line_idx}}`;

                const {{ gtHtml, ocrHtml }} = generateDiff(r.ftm_aligned, r.ftm_raw_ocr);

                const card = document.createElement('div');
                card.className = 'card';
                card.innerHTML = `
                    <div class="card-header">
                        <div class="ref-info">${{refText}}</div>
                        <div class="card-tags">
                            <span class="tag ${{r.category}}">${{getCategoryLabel(r.category)}}</span>
                        </div>
                    </div>

                    <div class="image-frame">
                        <img class="crop-img" src="${{r.line_crop}}" alt="Line Crop Image" />
                    </div>

                    <div class="diff-grid">
                        <div class="text-panel">
                            <span class="panel-label">Aligned Ground Truth</span>
                            <div class="text-content">${{gtHtml}}</div>
                        </div>
                        <div class="text-panel">
                            <span class="panel-label">OCR Prediction (FTM)</span>
                            <div class="text-content">${{ocrHtml}}</div>
                        </div>
                    </div>

                    <div class="card-metrics">
                        <div class="metric-item">
                            <span class="metric-lbl">Confidence</span>
                            <div class="metric-val-group">
                                <span class="metric-val" style="color: ${{getConfColor(r.ftm_confidence)}}">${{r.ftm_confidence}}%</span>
                                <div class="metric-bar-outer">
                                    <div class="metric-bar-inner" style="width: ${{r.ftm_confidence}}%; background-color: ${{getConfColor(r.ftm_confidence)}}"></div>
                                </div>
                            </div>
                        </div>
                        <div class="metric-item">
                            <span class="metric-lbl">Character Error Rate (CER)</span>
                            <div class="metric-val-group">
                                <span class="metric-val" style="color: ${{getCerColor(r.cer)}}">${{r.cer}}%</span>
                                <div class="metric-bar-outer">
                                    <div class="metric-bar-inner" style="width: ${{Math.min(100, r.cer)}}%; background-color: ${{getCerColor(r.cer)}}"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            }});
        }}

        window.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
"""

    with open(output_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated Cherokee NT OCR performance report: {output_html_path}")

if __name__ == "__main__":
    main()
