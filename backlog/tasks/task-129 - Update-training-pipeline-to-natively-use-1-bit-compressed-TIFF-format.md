---
id: TASK-129
title: Update training pipeline to natively use 1-bit compressed TIFF format
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 15:00'
updated_date: '2026-06-19 15:33'
labels:
  - optimization
  - training
dependencies:
  - TASK-128
priority: medium
ordinal: 147000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Once the feasibility and inference performance of the 1-bit compressed TIFF format have been verified in TASK-128 and approved, update the main training and augmentation pipeline to natively use 1-bit compressed TIFF instead of PNG to permanently accelerate training setup and compilation times.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Integrate 1-bit compressed TIFF output natively into train.py and augment_dynamic.py
- [x] #2 Ensure all automated and manual tests pass with the new TIFF pipeline
- [x] #3 Update documentation regarding the pipeline format changes
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully migrated the training pipeline to natively use 1-bit compressed TIFF (CCITT Group 4) format. Updated augment_dynamic.py to output TIFF via Pillow, train.py to compile *.tiff to .lstmf, and sweep.py to backward-compatibly check for both PNG and TIFF. Verified end-to-end staged training run generates 0 PNGs and successfully compiles 1,577 TIFFs to .lstmf. Documented format changes in mixed-training-augmentation.md.
<!-- SECTION:FINAL_SUMMARY:END -->
