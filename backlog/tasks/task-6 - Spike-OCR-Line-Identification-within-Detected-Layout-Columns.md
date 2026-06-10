---
id: TASK-6
title: Spike OCR Line Identification within Detected Layout Columns
status: Done
assignee:
  - '@agent'
created_date: '2026-06-10 14:33'
updated_date: '2026-06-10 14:33'
labels: []
dependencies: []
modified_files:
  - scripts/extract_lines.py
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Develop scripts/extract_lines.py to spike line identification using Surya DetectionPredictor nested within extracted layout columns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Extract layout columns and apply skew correction
- [x] #2 Run Surya line detection inside each column crop with configurable padding
- [x] #3 Sort lines top-to-bottom and left-to-right
- [x] #4 Generate a visual HTML report inspecting crop files with confidence scores
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Set up Surya line detection in scripts/extract_lines.py\n2. Extract lines nested inside layout column crops\n3. Sort lines and apply padding\n4. Output inspect.html report
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Developed scripts/extract_lines.py to detect and extract individual lines nested within layout column crops, generating an interactive HTML report to verify the output.
<!-- SECTION:FINAL_SUMMARY:END -->
