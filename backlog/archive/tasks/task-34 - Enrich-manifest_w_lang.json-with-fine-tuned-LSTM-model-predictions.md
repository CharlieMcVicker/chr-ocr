---
id: TASK-34
title: Enrich manifest_w_lang.json with fine-tuned LSTM model predictions
status: Done
assignee:
  - '@agent'
created_date: '2026-06-11 17:03'
updated_date: '2026-06-11 17:44'
labels: []
dependencies: []
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The manifest_w_lang.json currently has a predicted_lang field populated by the old heuristic Tesseract classifier (pct_cherokee threshold on chr+eng OCR output). We now have several fine-tuned LSTM checkpoints from lstmtraining. The goal is to run the best checkpoint against every line crop in the manifest and add two new fields: (1) ftm_ocr — the raw OCR text from the fine-tuned model, and (2) ftm_confidence — a confidence score derived from the model output. This richer annotation will: (a) seed the labeling UI with better guesses to speed up hand-labeling, and (b) let us rank lines by low confidence to surface the hardest/ambiguous crops for targeted hand-labeling.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify and document the best fine-tuned checkpoint (lowest BCER) across all training output directories
- [x] #2 Write a script enrich_manifest_with_ftm.py that loads manifest_w_lang.json, runs tesseract on each line crop image using the best fine-tuned .traineddata (or checkpoint converted via combine_tessdata), and writes ftm_ocr and ftm_confidence fields back to the manifest
- [x] #3 The script is incremental: skips entries that already have ftm_ocr populated, and saves every N entries to avoid losing progress on interruption
- [x] #4 The enriched manifest is saved atomically (write to .tmp then rename) to training_data_v2/manifest_w_lang.json in-place
- [x] #5 A post-run summary is printed: total items processed, distribution of confidence scores, and the N lowest-confidence entries printed for inspection
- [x] #6 The server labeling UI is updated to display ftm_ocr and ftm_confidence alongside the existing predicted_lang field
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Enriched the entire training_data_v2/manifest_w_lang.json (8,072 entries) with Cherokee OCR predictions and average character-level confidence scores from the best fine-tuned LSTM checkpoint (chr_38.889_195_200.checkpoint). The enrichment process was completed incrementally and atomically using a newly written python script. Additionally, the Flask training UI (server/templates/training.html) was upgraded to render the fine-tuned model guesses and confidence metrics, and auto-populate the Cherokee transcription input field to speed up human annotators.
<!-- SECTION:FINAL_SUMMARY:END -->
