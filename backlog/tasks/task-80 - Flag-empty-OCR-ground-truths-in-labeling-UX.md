---
id: TASK-80
title: Flag empty OCR ground truths in labeling UX
status: To Do
assignee: []
created_date: '2026-06-17 12:41'
labels: []
dependencies: []
priority: medium
ordinal: 79000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In the Flask labeling web interface, there is currently no warning or validation when a transcription/label is empty or contains only whitespace. Empty ground truths cause Tesseract's lstmeval evaluation tool to throw encoding errors and skip lines, skewing performance metrics. This task adds validation and visual feedback to highlight empty ground truths in the labeling UI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Labeling UI displays a visual flag or warning next to items that have empty/whitespace-only ground truth transcriptions
- [ ] #2 Web interface warns the user or prevents saving when they attempt to submit an empty transcription
- [ ] #3 Filter/toggle option added to the labeling UI to easily view all items with empty ground truths
<!-- AC:END -->
