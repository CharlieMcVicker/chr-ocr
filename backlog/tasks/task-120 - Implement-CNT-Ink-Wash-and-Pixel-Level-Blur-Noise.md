---
id: TASK-120
title: Implement CNT Ink Wash and Pixel-Level Blur Noise
status: To Do
assignee: []
created_date: '2026-06-19 13:09'
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
- [ ] #1 Implement a configurable ink-wash/smudging utility in phoenix/training/augment.py that applies pixel-level salt-and-pepper noise combined with blur.
- [ ] #2 Expose smudging parameters (probability and intensity) in the cnt_noise section of the training configuration and config.py.
- [ ] #3 Forward the new arguments from train.py to scripts/augment_dynamic.py and apply the augmentation to CNT images.
- [ ] #4 Verify that augmented CNT images contain the new noise style and are saved correctly.
<!-- AC:END -->
