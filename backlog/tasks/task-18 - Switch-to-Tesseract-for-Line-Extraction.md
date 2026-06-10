---
id: TASK-18
title: Switch to Tesseract for Line Extraction
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-10 19:40'
updated_date: '2026-06-10 19:43'
labels: []
dependencies: []
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace Surya line detection with Tesseract TSV output to identify text lines within columns, and build a script to map existing labels to the new bounding boxes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Modify prepare_training_data.py to use Tesseract TSV for lines
- [ ] #2 Create label reconsolidation script
<!-- AC:END -->
