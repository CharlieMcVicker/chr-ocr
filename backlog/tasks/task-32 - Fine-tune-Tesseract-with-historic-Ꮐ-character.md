---
id: TASK-32
title: Fine-tune Tesseract with historic Ꮐ character
status: In Progress
assignee:
  - '@agent'
created_date: '2026-06-11 14:57'
updated_date: '2026-06-16 13:02'
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

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extract unicharsets from original chr.traineddata.\n2. Extrapolate and merge Ꮐ into the unicharset.\n3. Modify split_train_test.py to perform stratified/oversampled splits for rare characters like Ꮐ.\n4. Modify train_staged.py to pass --old_traineddata to enable network expansion fine-tuning.\n5. Train and evaluate transcription accuracy.
<!-- SECTION:PLAN:END -->
