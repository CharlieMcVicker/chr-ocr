---
id: TASK-83.3
title: Align Cherokee text transcriptions with extracted line images
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 12:55'
updated_date: '2026-06-17 13:15'
labels:
  - cnt-ocr
dependencies: []
parent_task_id: TASK-83
ordinal: 85000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Map the verse text onto the individual extracted line crops (handling multi-line verses and potential transcription matching difficulties). Note that we will need to prepend verse numbers to the front of lines.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement alignment heuristics to assign text to segmented lines
- [x] #2 Provide verification method or logs to identify misalignment errors
- [x] #3 Prepend verse numbers to the front of corresponding lines
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented Tesseract-assisted dynamic programming search to align full verse transcriptions with individual line crop images. Added an HTML verification page showing side-by-side comparisons of crops, noisy OCRs, and aligned ground-truth segments. Verified using both stock and fine-tuned models, and prepended the verse numbers with no dots to the first lines.
<!-- SECTION:FINAL_SUMMARY:END -->
