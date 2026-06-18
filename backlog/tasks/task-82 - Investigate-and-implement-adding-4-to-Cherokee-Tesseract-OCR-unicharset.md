---
id: TASK-82
title: Investigate and implement adding '4' to Cherokee Tesseract OCR unicharset
status: To Do
assignee: []
created_date: '2026-06-17 12:49'
updated_date: '2026-06-18 02:52'
labels: []
dependencies: []
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refine Cherokee Tesseract OCR unicharset to support numeric '4' and square brackets '[', ']', and implement a centralized ground-truth normalization module to prevent all character encoding mismatch errors in the training and evaluation pipelines.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 All training/evaluation ground-truth text passes through a centralized normalization utility
- [ ] #2 Unicharset files in the repository contain '4', '[', and ']'
- [ ] #3 Model fine-tuning converges successfully on the updated unicharset
<!-- AC:END -->
