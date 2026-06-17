---
id: TASK-84
title: Handle hyphenated word splits in Cherokee New Testament alignment
status: To Do
assignee: []
created_date: '2026-06-17 13:38'
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
- [ ] #1 Detect hyphenated words at the end of line OCR predictions
- [ ] #2 Reconstruct split words when computing word-to-line alignments
- [ ] #3 Verify that reconstructed word splits do not cause false CER or alignment mismatches in the viewer
<!-- AC:END -->
