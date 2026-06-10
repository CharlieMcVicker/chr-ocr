---
id: TASK-14
title: Implement Column Bounding Box Grouping and Filtering
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-10 19:21'
updated_date: '2026-06-10 19:30'
labels: []
dependencies: []
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update extract_columns in layout.py to group raw text blocks into columns and discard small, noisy groups.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement fuzzy grouping logic in extract_columns
- [x] #2 Add filtering to discard groups with few boxes or small area
- [x] #3 Return merged column crops instead of raw blocks
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated extract_columns in layout.py to use fuzzy grouping and area-based filtering to properly group blocks into column crops.
<!-- SECTION:FINAL_SUMMARY:END -->
