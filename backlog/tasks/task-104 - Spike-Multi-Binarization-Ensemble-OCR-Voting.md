---
id: TASK-104
title: 'Spike: Multi-Binarization Ensemble OCR Voting'
status: Done
assignee:
  - '@agent'
created_date: '2026-06-18 15:05'
updated_date: '2026-06-18 15:44'
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
- [x] #1 Create scripts/spike_ensemble_ocr.py
- [x] #2 Load 100 random test crops and their ground truths
- [x] #3 Generate 3 image variations and run PyTesseract inference
- [x] #4 Implement character-level majority voting via sequence alignment
- [x] #5 Print CER evaluation comparing Ensemble vs Grayscale baseline
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created spike_ensemble_ocr.py to test a 3-way multi-binarization character-level majority vote OCR ensemble. \n\nResults (using pure unaugmented test/base images):\n- Base Grayscale CER: 6.628%\n- Ensemble Voting CER: 8.489%\n\nConclusion: The ensemble voting underperformed the base grayscale baseline. This indicates that the binarizations (Sauvola and Wolf) reduce OCR accuracy sufficiently to drag down the majority vote. Therefore, a pure voting ensemble using these specific binarizations is not recommended for inference at this time.
<!-- SECTION:FINAL_SUMMARY:END -->
