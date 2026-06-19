---
id: TASK-121
title: Implement CNT Pixel-Level Coarse Dropout Noise
status: Done
assignee:
  - '@agent'
created_date: '2026-06-19 13:09'
updated_date: '2026-06-19 13:51'
labels: []
dependencies: []
ordinal: 135000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement fine-grained, high-frequency coarse dropout (pixel-level micro-erasures) on Cherokee New Testament images to mimic physical dry-type ink starvation and print-fade.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update get_albumentations_pipeline in phoenix/training/augment.py to support high-frequency micro-coarse dropout (low hole size, higher frequency/hole count).
- [x] #2 Expose micro-dropout parameters under the cnt_noise config dictionary in phoenix/config.py.
- [x] #3 Pass and verify these parameters in train.py and scripts/augment_dynamic.py to generate print-fade effects on CNT samples.
- [x] #4 Verify that augmented CNT images contain the fine-grained pixel dropout.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Expose micro-dropout parameters under cnt_noise in phoenix/config.py\n2. Add secondary A.CoarseDropout step in get_albumentations_pipeline in phoenix/training/augment.py\n3. Register and pass micro-dropout CLI args in scripts/augment_dynamic.py\n4. Pass the parameters in phoenix/training/train.py subprocess command\n5. Verify that augmented CNT images contain the fine-grained pixel dropout.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented CNT Pixel-Level Coarse Dropout Noise (high-frequency, low-size CoarseDropout) under get_albumentations_pipeline in phoenix/training/augment.py. Exposed the parameters under cnt_noise config dictionary in phoenix/config.py. Passed and verified these parameters in scripts/augment_dynamic.py and phoenix/training/train.py. Verified that augmented images generate correctly.
<!-- SECTION:FINAL_SUMMARY:END -->
