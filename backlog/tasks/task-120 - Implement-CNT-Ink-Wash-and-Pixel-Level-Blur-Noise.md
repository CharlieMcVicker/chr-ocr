---
id: TASK-120
title: Implement CNT Ink Wash and Pixel-Level Blur Noise
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 13:09'
updated_date: '2026-06-19 13:42'
labels: []
dependencies: []
ordinal: 134000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add pixel-level ink smudging and spot-mold/noise effects combined with subtle blur to simulate wet ink bleed and deterioration on Cherokee New Testament images.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement a configurable ink-wash/smudging utility in phoenix/training/augment.py that applies pixel-level salt-and-pepper noise combined with blur.
- [x] #2 Expose smudging parameters (probability and intensity) in the cnt_noise section of the training configuration and config.py.
- [x] #3 Forward the new arguments from train.py to scripts/augment_dynamic.py and apply the augmentation to CNT images.
- [x] #4 Verify that augmented CNT images contain the new noise style and are saved correctly.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented ink wash and smudge noise augmentation for CNT data
<!-- SECTION:FINAL_SUMMARY:END -->
