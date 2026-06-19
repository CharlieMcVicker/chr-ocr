---
id: TASK-84
title: Handle hyphenated word splits in Cherokee New Testament alignment
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 13:38'
updated_date: '2026-06-17 13:48'
labels:
  - cnt-ocr
dependencies: []
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Words split across line boundaries with hyphens ('-') in Tesseract OCR output cause mismatches and false errors. The alignment and evaluation pipelines should detect and handle split words gracefully.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Detect hyphenated words at the end of line OCR predictions
- [x] #2 Reconstruct split words when computing word-to-line alignments
- [x] #3 Verify that reconstructed word splits do not cause false CER or alignment mismatches in the viewer
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented a robust, resilient hyphenated word split detection and ground-truth preprocessing mechanism in the alignment script. It scans near line boundaries for hyphenated predictions, resolves noise/trailing garbage, matches the combined pieces to ground truth words via Levenshtein similarity, and mathematically splits the words at the optimal boundary to align precisely with the model's intent. Verified that the packaging script compiles correct lstmf files without mismatches.
<!-- SECTION:FINAL_SUMMARY:END -->
