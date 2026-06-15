---
id: TASK-1
title: Filter Training Manifest and Add Frontend Cherokee-Only Toggle
status: Done
assignee:
  - '@agent'
created_date: '2026-06-10 14:31'
updated_date: '2026-06-10 14:31'
labels: []
dependencies: []
ordinal: 1000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Filter out short/unclassified line crops from the training manifest and add a Cherokee-only toggle with color-coded badges to the training review interface.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create backup of manifest.json and filter out unlabeled lines with initial OCR <= 10 characters or non-Cherokee/English/Mixed classifications
- [x] #2 Add 'Cherokee lines only' toggle checkbox to the frontend training editor sidebar
- [x] #3 Display color-coded language class badges next to each item in the sidebar list
- [x] #4 Update Flask server to dynamically calculate language classifications when serving /training route
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Filter the manifest using a custom python script (filter_manifest.py) that invokes Tesseract with chr+eng models.
2. Add checkbox control and CSS badges to training.html.
3. Integrate classification endpoint processing in server/app.py.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully filtered training_data/manifest.json from 11,623 to 7,414 items using Tesseract OCR (chr+eng) language classification. Integrated a 'Cherokee lines only' toggle checkbox and color-coded language tags in server/templates/training.html. Updated server/app.py to dynamically classify text on the fly when rendering the route.
<!-- SECTION:FINAL_SUMMARY:END -->
