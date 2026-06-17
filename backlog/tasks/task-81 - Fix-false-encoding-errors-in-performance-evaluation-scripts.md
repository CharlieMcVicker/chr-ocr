---
id: TASK-81
title: Fix false encoding errors in performance evaluation scripts
status: To Do
assignee: []
created_date: '2026-06-17 12:42'
labels: []
dependencies: []
priority: high
ordinal: 80000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The performance evaluation scripts (generate_performance_graphs.py and generate_binarization_graphs.py) parse lstmeval stderr for Truth/OCR pairs. Because lstmeval only prints a sample of lines, the scripts flag valid evaluated lines as 'encoding_error' and set their CER to 100%. We need to refactor the scripts to get per-line OCR text directly (e.g. by running Tesseract in recognition mode) to calculate accurate per-line error rates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Fix false encoding errors in generate_performance_graphs.py by obtaining individual line OCR transcriptions directly (e.g. running Tesseract recognition or parsing lstmeval correctly)
- [ ] #2 Fix false encoding errors in generate_binarization_graphs.py
- [ ] #3 Correctly identify and log the true encoding errors (e.g. missing unicharset characters like '4' or brackets)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify scripts to obtain per-line OCR transcriptions directly using Tesseract recognition.\n2. Identify true encoding failures by parsing explicit Tesseract encoding errors.\n3. Regenerate and verify performance reports and graphs.
<!-- SECTION:PLAN:END -->
