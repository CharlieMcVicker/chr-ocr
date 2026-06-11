---
id: TASK-32
title: Fine-tune Tesseract with historic Ꮐ character
status: To Do
assignee: []
created_date: '2026-06-11 14:57'
labels:
  - fine-tuning
  - OCR
dependencies: []
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
We are failing to transcribe lines with the historic 'Ꮐ' character. Need to fine-tune Tesseract with this one extra character, following the same approach used for the +/- symbol fine-tuning.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Prepare training data containing the historic Ꮐ character
- [ ] #2 Fine-tune Tesseract model with the new character
- [ ] #3 Verify transcription accuracy on lines containing the historic Ꮐ character
<!-- AC:END -->
