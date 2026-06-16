---
id: TASK-67
title: Investigate 'Error' in ftm_ocr fields
status: Done
assignee:
  - '@agent'
created_date: '2026-06-16 14:27'
updated_date: '2026-06-16 15:41'
labels: []
dependencies: []
ordinal: 66000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Some ftm_ocr fields in manifest_w_lang.json are reading 'Error' after regenerating FTM predictions with the new 12.357% BCER OCR model. We need to investigate why these errors are occurring during the enrich_manifest_with_ftm.py execution.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Identify the root cause of the 'Error' values
- [x] #2 Fix the issue and regenerate the predictions for those specific entries
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully identified the root cause of the missing FTM predictions: the image line crops for the `col_02` sequence had been left in the legacy `.agents/brain` directory by a previous run, but the `training_data_v2/line_crops` symlink was incorrectly repointed to `../training_data/line_crops` (which uses an incompatible `col_31` numbering scheme), breaking the manifest references. Fixed by running a targeted background extraction on the 35 original JP2 scans to regenerate the missing 2,758 valid line crops, resolving OpenJPEG data stream decoding issues with `Image.MAX_IMAGE_PIXELS`, and deploying a migration script to properly place the recreated crops in a new, standalone `training_data_v2/line_crops` directory. Re-ran `enrich_manifest_with_ftm.py` to regenerate the FTM predictions for the recovered images, and purged 1,920 orphaned entries from the manifest that were unrecoverable physical false-positives from the original buggy detector.
<!-- SECTION:FINAL_SUMMARY:END -->
