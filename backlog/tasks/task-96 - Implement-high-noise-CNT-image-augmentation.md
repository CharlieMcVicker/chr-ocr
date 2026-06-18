---
id: TASK-96
title: Implement high-noise CNT image augmentation
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 20:41'
updated_date: '2026-06-17 20:49'
labels: []
dependencies: []
ordinal: 104000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable and customize Albumentations noise pipeline for CNT images during dynamic augmentation. The noise should be high-intensity (probabilities >= 0.5 for blur, shadow, distortion, dropout) to mimic the 1828 Phoenix printing degradation while still bypassing dynamic binarization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Configure scripts/augment_dynamic.py to apply high-intensity Albumentations noise to CNT images
- [x] #2 Ensure dynamic binarization is still bypassed for CNT images
- [x] #3 Verify augmented CNT outputs contain high noise and are saved correctly
- [x] #4 Define CNT noise probabilities and intensity levels in the configuration JSON
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented high-noise CNT image augmentation pipeline using parameterized Albumentations pipeline in augment.py, parsing CLI args in augment_dynamic.py, and forwarding from train.py with a nested, hierarchical cnt_noise JSON config format in config.py and configurations.
<!-- SECTION:FINAL_SUMMARY:END -->
