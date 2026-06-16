---
id: TASK-55
title: Investigate and Implement Line-By-Line CHR/ENG Language Classification
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-15 18:05'
updated_date: '2026-06-15 23:20'
labels: []
dependencies: []
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigate and implement Cherokee vs Latin line-by-line language classification (rather than column-by-column) on mixed columns. Implement a line language scoring function combining Tesseract OCR confidence values (from eng and chr models) and FTM (Fine-Tuned Model) confidence ratings, augmented by Cherokee false positives ('not Cherokee' labels extracted from the labeling UX). Execute parameter search to identify optimal weights and threshold values for this classification heuristic, validate accuracy, document findings in a research doc, and integrate the utility into the training/labeling pipeline.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement a line scoring function combining eng, chr, and FTM confidence values, augmented by 'not Cherokee' labels
- [x] #2 Perform parameter search to find optimal scoring weights and threshold settings, measuring false-positive and false-negative rates
- [x] #3 Validate line classification accuracy on the labeled test dataset (chr_lines, eng_lines, and augmented false positives)
- [x] #4 Document findings, metrics, and final recommendations in a research doc under backlog/docs/research/
- [x] #5 Integrate the classification utility into the training data preparation or labeling pipeline
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Merged Task 23 and Task 55. Created scripts/find_line_class_params.py to execute parameter grid-search on 818 test lines combining Tesseract (eng/chr) and FTM confidence values. Achieved 99.76% classification accuracy using a weighted score. Documented findings in backlog/docs/research/doc-14. Integrated the optimal heuristic into scripts/classify_layout.py and scripts/filter_manifest.py.
<!-- SECTION:FINAL_SUMMARY:END -->
