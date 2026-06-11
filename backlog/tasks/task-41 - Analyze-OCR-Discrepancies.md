---
id: TASK-41
title: Analyze OCR Discrepancies
status: Done
assignee: []
created_date: '2026-06-11 22:30'
updated_date: '2026-06-11 22:31'
labels: []
dependencies: []
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Analyze manifest_w_lang.json to flag discrepancies between baseline OCR predictions and fine-tuned model predictions, specifically cases where one model predicts text and the other doesn't. Propose further investigations.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Write script to analyze discrepancies
- [x] #2 Report discrepancy counts
- [x] #3 Propose further investigation steps
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Analyzed manifest_w_lang.json. Found 144 lines where initial OCR predicts text but FTM predicts nothing. Script written to scripts/analyze_ocr_discrepancies.py and proposed investigations recorded in ocr_discrepancy_report.md.
<!-- SECTION:FINAL_SUMMARY:END -->
