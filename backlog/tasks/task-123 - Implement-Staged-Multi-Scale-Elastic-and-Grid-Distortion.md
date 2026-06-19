---
id: TASK-123
title: Implement Staged Multi-Scale Elastic and Grid Distortion
status: To Do
assignee: []
created_date: '2026-06-19 13:13'
labels: []
dependencies: []
ordinal: 137000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add support for multi-scale geometric distortions by combining local high-frequency elastic transforms with wide-range grid distortions, and explore multi-pass configurations to simulate complex paper warps.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Update get_albumentations_pipeline in phoenix/training/augment.py to support combining ElasticTransform and GridDistortion in a multi-scale configuration.
- [ ] #2 Expose parameters for multi-pass configuration or customizable alpha/sigma scales in the cnt_noise config.
- [ ] #3 Forward the geometric distortion arguments from train.py to scripts/augment_dynamic.py.
- [ ] #4 Verify that augmented images contain compounding wavy page distortions without breaking character readability.
<!-- AC:END -->
