---
id: TASK-129
title: Update training pipeline to natively use 1-bit compressed TIFF format
status: To Do
assignee: []
created_date: '2026-06-19 15:00'
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
- [ ] #1 Integrate 1-bit compressed TIFF output natively into train.py and augment_dynamic.py
- [ ] #2 Ensure all automated and manual tests pass with the new TIFF pipeline
- [ ] #3 Update documentation regarding the pipeline format changes
<!-- AC:END -->
