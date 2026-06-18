---
id: TASK-109
title: >-
  Create active learning pipeline to extract low-confidence newspaper line crops
  for targeted hand-labeling
status: Done
assignee: []
created_date: '2026-06-18 18:14'
updated_date: '2026-06-18 18:18'
labels: []
dependencies: []
ordinal: 123000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Scan the existing pre-computed fields (ftm_ocr and ftm_confidence) in the training manifest (training_data/manifest_w_lang.json) for lines containing predicted rare/confused characters (4, ?, [, ], Ꮐ). Extract these existing low-confidence line crops and their metadata to a dedicated folder for quick human verification/labeling, with ZERO new model inference required.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Develop scripts/extract_low_confidence_rare_crops.py to parse the pre-existing 'ftm_ocr' and 'ftm_confidence' fields from training_data/manifest_w_lang.json (with zero new inference required)
- [x] #2 Ensure the script supports configurable confidence thresholds, character filters, and max results limit
- [x] #3 Verify the script successfully copies the corresponding real crop images to a dedicated extraction folder for human verification and generates an easy-to-read metadata summary
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented 'scripts/extract_low_confidence_rare_crops.py' to extract low-confidence crops with rare/confused characters from manifest_w_lang.json predictions. Added CLI parameters for filtering and limit settings. Copied the crops and generated a beautiful standalone HTML visual dashboard ('index.html'), JSON summary ('summary.json'), and markdown summary ('summary.md').
<!-- SECTION:FINAL_SUMMARY:END -->
