---
id: TASK-111
title: Create OCR confidence heatmaps on sample scan documents
status: Done
assignee:
  - '@myself'
created_date: '2026-06-18 19:52'
updated_date: '2026-06-18 19:54'
labels: []
dependencies: []
ordinal: 125000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate a graph/visualization showing OCR confidence heatmaps on a couple of sample scan documents.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify sample scans with abundant confidence data
- [x] #2 Implement a Python script to plot bounding boxes with color-coded confidence levels
- [x] #3 Save high-quality visualization heatmaps in the codebase
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented scripts/generate_confidence_heatmaps.py to parse confidence data and overlay bounding boxes on sample page scans. Saved heatmaps for 1828-11-19/seq-2, 1828-03-13/seq-1, and 1829-01-21/seq-3 to training_data/performance_analysis/.
<!-- SECTION:FINAL_SUMMARY:END -->
