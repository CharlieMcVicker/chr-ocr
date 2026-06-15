---
id: TASK-4
title: Implement Layout Column Detection and Skew Correction Pipeline
status: Done
assignee:
  - '@agent'
created_date: '2026-06-10 14:33'
updated_date: '2026-06-12 02:35'
labels: []
dependencies: []
modified_files:
  - server/layout.py
  - scripts/plot_layout.py
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create layout and skew correction utilities in server/layout.py and a plotting/visualizer script in scripts/plot_layout.py to identify text columns and resolve document skew.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Apply stain cleaning using morphological closing and CLAHE contrast enhancement
- [x] #2 Implement document skew detection using variance of horizontal row projection profile
- [x] #3 Extract text/list columns using Surya layout detection models
- [x] #4 Develop scripts/plot_layout.py to plot coordinates of merged columns and save unmerged/merged crops
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implement apply_stain_cleaning and apply_adaptive_threshold in server/layout.py\n2. Implement detect_and_fix_skew using projection variance\n3. Implement extract_columns using LayoutPredictor\n4. Develop scripts/plot_layout.py visualizer
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Found 144 lines where initial OCR predicts text but FTM predicts nothing. Script written to analyze.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented core document preprocessing and column extraction in server/layout.py including background morph closing, CLAHE, and projection variance-based skew correction. Built scripts/plot_layout.py to visualize column bounds.
<!-- SECTION:FINAL_SUMMARY:END -->
