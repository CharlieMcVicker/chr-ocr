---
id: TASK-121
title: Implement CNT Pixel-Level Coarse Dropout Noise
status: To Do
assignee: []
created_date: '2026-06-19 13:09'
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
- [ ] #1 Update get_albumentations_pipeline in phoenix/training/augment.py to support high-frequency micro-coarse dropout (low hole size, higher frequency/hole count).
- [ ] #2 Expose micro-dropout parameters under the cnt_noise config dictionary in phoenix/config.py.
- [ ] #3 Pass and verify these parameters in train.py and scripts/augment_dynamic.py to generate print-fade effects on CNT samples.
- [ ] #4 Verify that augmented CNT images contain the fine-grained pixel dropout.
<!-- AC:END -->
