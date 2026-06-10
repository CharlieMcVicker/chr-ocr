---
id: TASK-2
title: Implement Line-Height Normalization to Improve Tesseract OCR Accuracy
status: To Do
assignee: []
created_date: '2026-06-10 14:31'
labels: []
dependencies: []
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Resize individual line crops extracted during preprocessing to a target height of ~30 pixels while maintaining aspect ratio, to align with Tesseract's preferred font size and improve transcription quality.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Define a TARGET_LINE_HEIGHT of 30 pixels (configurable) for crops
- [ ] #2 Update line crop extraction logic to resize images proportionally to TARGET_LINE_HEIGHT using high-quality resampling
- [ ] #3 Ensure aspect ratio is strictly preserved during scaling
- [ ] #4 Add optional tolerance range or thresholding to avoid scaling extremely small/large artifacts
- [ ] #5 Update line_bbox coordinates in the manifest to match the new image dimensions if needed
<!-- AC:END -->
