---
id: TASK-104
title: 'Spike: Multi-Binarization Ensemble OCR Voting'
status: To Do
assignee: []
created_date: '2026-06-18 15:05'
labels: []
dependencies: []
ordinal: 118000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a throwaway script (scripts/spike_ensemble_ocr.py) to test if we can lower the OCR inference error rate using ensemble voting without retraining. The script should: 1) Load a subset of 100 line crops from the test_20 split. 2) Generate 3 image variations per crop (Base Grayscale, Sauvola, and Wolf/Textcleaner). 3) Run PyTesseract with chr_best_finetuned on all variations. 4) Use sequence alignment to align the 3 resulting transcription strings and take a majority vote per character. 5) Compare the CER of the Ensemble Output vs the Base Grayscale alone. If successful, this proves we can increase inference accuracy dynamically.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create scripts/spike_ensemble_ocr.py
- [ ] #2 Load 100 random test crops and their ground truths
- [ ] #3 Generate 3 image variations and run PyTesseract inference
- [ ] #4 Implement character-level majority voting via sequence alignment
- [ ] #5 Print CER evaluation comparing Ensemble vs Grayscale baseline
<!-- AC:END -->
