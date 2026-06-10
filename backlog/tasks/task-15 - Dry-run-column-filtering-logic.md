---
id: TASK-15
title: Dry run column filtering logic
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-10 19:22'
updated_date: '2026-06-10 19:24'
labels: []
dependencies: []
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Run the proposed column grouping and filtering logic on a sample of scans to see how many columns would be dropped, without saving any files to disk.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create dry run script
- [x] #2 Analyze how many columns drop
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Ran dry run script on 3 scans. It successfully dropped 4 tiny noise columns (each ~1% of page height) across the scans, leaving exactly 5 valid text columns for each scan.
<!-- SECTION:FINAL_SUMMARY:END -->
