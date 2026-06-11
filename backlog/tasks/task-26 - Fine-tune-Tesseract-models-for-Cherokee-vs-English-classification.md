---
id: TASK-26
title: Fine-tune Tesseract models for Cherokee vs English classification
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-11 02:21'
updated_date: '2026-06-11 02:22'
labels: []
dependencies: []
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Use images in chr_lines and eng_lines folders to fine-tune parameters for classifying English and Cherokee lines using the existing Tesseract models.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create evaluation script
- [x] #2 Evaluate baseline accuracy
- [x] #3 Tune parameters to maximize classification accuracy
- [x] #4 Update implementation with tuned parameters
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created scripts/evaluate_lang_classification.py to evaluate Tesseract models on chr_lines and eng_lines folders. Running it now to find optimal thresholds.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created evaluation script evaluating Tesseract on 818 test lines. Best accuracy was 99.14% using new thresholds. Updated filter_manifest.py and classify_layout.py to use pct_cherokee > 0.45 for Cherokee and < 0.40 for English.
<!-- SECTION:FINAL_SUMMARY:END -->
