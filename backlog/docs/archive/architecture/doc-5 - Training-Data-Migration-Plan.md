---
id: doc-5
title: Training Data Migration Plan
type: other
created_date: '2026-06-10 19:41'
updated_date: '2026-06-10 19:41'
---
# Non-Destructive Training Data Migration Plan

To ensure we do not overwrite or interfere with the current training data (which contains existing manual labels), we will transition to a versioned directory approach.

### 1. New Output Directory: `training_data_v2`
We will update the pipeline scripts and the web server to point to a new directory: `training_data_v2`.
- **Crops**: `training_data_v2/line_crops/`
- **Manifest**: `training_data_v2/manifest.json`
- **Progress**: `training_data_v2/completed_scans.json`

### 2. Switch to Tesseract Line Extraction
Currently, we use Surya's `DetectionPredictor` to detect lines within the column crops. We will:
- Remove Surya line detection.
- Run Tesseract with `tsv` output (`tesseract image.png stdout tsv`).
- Parse the TSV output for entries where `level == 4` (line level) or aggregate word bounding boxes (`level == 5`) into lines.
- Crop the image based on these Tesseract-derived line bounding boxes instead.

### 3. Label Reconsolidation Script
We will create a script that reads both `training_data/manifest.json` (the old data) and `training_data_v2/manifest.json` (the new empty data).
For every labeled line in the old data, the script will:
1. Translate the old column-relative bounding box back to absolute page coordinates (using the old column boxes).
2. Find the new Tesseract line box in `v2` that has the highest Intersection over Union (IoU) overlap with the absolute page coordinates.
3. If the overlap is above a certain threshold (e.g., 50%), automatically copy the user's label to the new `v2` manifest entry.
