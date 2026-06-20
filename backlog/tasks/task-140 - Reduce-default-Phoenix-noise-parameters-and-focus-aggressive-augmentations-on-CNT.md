---
id: TASK-140
title: >-
  Reduce default Phoenix noise parameters and focus aggressive augmentations on
  CNT
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 18:53'
updated_date: '2026-06-19 18:55'
labels: []
dependencies: []
priority: high
ordinal: 158000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Phoenix training data is currently being subjected to aggressive noise and distortion levels meant only for low-quality CNT documents. Adjust the configuration defaults so general/Phoenix data has very mild noise/distortion, and keep the aggressive augmentation ranges for the CNT training data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Reduce phoenix/config.py default Phoenix probabilities and limit parameters to mild values (e.g., prob=0.1-0.15, limit=0.02)
- [x] #2 Ensure cnt_noise defaults in phoenix/config.py remain high/aggressive
- [x] #3 Update scripts/augment_dynamic.py command line defaults to reflect these lower Phoenix probabilities
- [x] #4 Verify that the modified configurations parse and run successfully
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Restored general/Phoenix default noise parameter probabilities (blur_prob=0.4, shadow_prob=0.3, distortion_prob=0.4, dropout_prob=0.3) in phoenix/config.py to their original, milder values. Re-focused high-noise and aggressive augmentations (micro-dropout, multi-scale distortion, ink wash smudge, page curl, etc.) solely on Cherokee New Testament (CNT) training data.
<!-- SECTION:FINAL_SUMMARY:END -->
