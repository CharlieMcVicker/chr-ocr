---
id: TASK-74
title: Investigate and resolve Tesseract encoding failure errors during training
status: To Do
assignee: []
created_date: '2026-06-16 20:11'
labels: []
dependencies: []
ordinal: 73000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Tesseract training logs show multiple 'Encoding of string failed!' and 'Can't encode transcription' errors, skipping lines containing characters like historic Ꮐ or specific punctuation not present in the base unicharset. Investigate the root cause, identify the failing characters, and resolve them by updating the unicharset or cleaning the input transcriptions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Identify all characters causing 'Encoding of string failed!' errors in the training logs
- [ ] #2 Determine if the unicharset needs expansion or if transcriptions need normalization
- [ ] #3 Apply the fix (e.g., expand unicharset or normalize text) and verify that training skip ratio decreases
<!-- AC:END -->
