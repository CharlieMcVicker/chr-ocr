---
id: TASK-7
title: Implement Restartable Training Data Extraction Script
status: Done
assignee:
  - '@agent'
created_date: '2026-06-10 14:33'
updated_date: '2026-06-10 14:33'
labels: []
dependencies: []
modified_files:
  - scripts/prepare_training_data.py
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Develop a restartable preprocessing script scripts/prepare_training_data.py to extract text lines from scans, skipping already fully processed scans, and save them to a training manifest.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Locate and loop through all scanned images recursively
- [x] #2 Skip already processed scans using completed_scans.json list or existing manifest items
- [x] #3 Extract lines from Cherokee/Mixed columns, run initial OCR, save line crops, and save progress incrementally after each scan
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Set up scripts/prepare_training_data.py recursively finding scans\n2. Track processed scans with completed_scans.json\n3. Extract columns, classify language, segment lines, run initial Tesseract chr OCR, and save manifest incrementally
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Developed scripts/prepare_training_data.py to extract training line crops recursively, with restartability via completed_scans.json and incremental manifest updates.
<!-- SECTION:FINAL_SUMMARY:END -->
