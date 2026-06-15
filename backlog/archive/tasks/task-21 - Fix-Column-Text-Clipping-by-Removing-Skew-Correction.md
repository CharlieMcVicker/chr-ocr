---
id: TASK-21
title: Fix Column Text Clipping by Removing Skew Correction
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-10 20:36'
updated_date: '2026-06-10 20:43'
labels: []
dependencies: []
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Mathematical skew correction on column crops causes wavy text to rotate out of bounds and clip. Remove skew correction and rely entirely on AI line detection to naturally map curved lines.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Revert centroid matching logic from extract_lines.py
- [ ] #2 Remove skew correction from extract_lines.py
- [ ] #3 Verify crops with inspect.html
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Removed math-based skew correction from column isolation phase and ported changes to prepare_training_data.py.
<!-- SECTION:FINAL_SUMMARY:END -->
