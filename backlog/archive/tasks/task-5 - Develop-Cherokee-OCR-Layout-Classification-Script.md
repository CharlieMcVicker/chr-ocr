---
id: TASK-5
title: Develop Cherokee OCR Layout Classification Script
status: Done
assignee:
  - '@agent'
created_date: '2026-06-10 14:33'
updated_date: '2026-06-10 14:33'
labels: []
dependencies: []
modified_files:
  - scripts/classify_layout.py
  - scripts/process_all_scans.py
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Develop scripts/classify_layout.py to run Tesseract OCR on extracted layout bounding boxes, classify language contents (Cherokee/English/Mixed/Empty), and generate reports.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Classify characters into Cherokee or Latin unicode ranges
- [x] #2 Calculate percentage of Cherokee characters to determine text language class (Cherokee, English, Mixed, Empty)
- [x] #3 Process input folders recursively and save cropped bounding box images into folders organized by predicted class
- [x] #4 Generate CSV and JSON classification reports
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement unicode ranges checks in scripts/classify_layout.py\n2. Calculate Cherokee character ratios\n3. OCR-process extracted column crops and sort them\n4. Output reports in JSON and CSV format
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Developed scripts/classify_layout.py and scripts/process_all_scans.py to perform Tesseract OCR (chr+eng) on extracted column crops, classify language content based on character ratio, organize crops, and output CSV/JSON reports.
<!-- SECTION:FINAL_SUMMARY:END -->
