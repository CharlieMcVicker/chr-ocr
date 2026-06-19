---
id: TASK-123
title: Implement Staged Multi-Scale Elastic and Grid Distortion
status: Done
assignee: []
created_date: '2026-06-19 13:13'
updated_date: '2026-06-19 14:11'
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
- [x] #1 Update get_albumentations_pipeline in phoenix/training/augment.py to support combining ElasticTransform and GridDistortion in a multi-scale configuration.
- [x] #2 Expose parameters for multi-pass configuration or customizable alpha/sigma scales in the cnt_noise config.
- [x] #3 Forward the geometric distortion arguments from train.py to scripts/augment_dynamic.py.
- [x] #4 Verify that augmented images contain compounding wavy page distortions without breaking character readability.
- [x] #5 Update the mathematical specification of Staged Multi-Scale Elastic and Grid Distortion in backlog/docs/research/mixed-training-augmentation.md
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented staged multi-scale elastic and grid distortion by combining local high-frequency elastic transforms with wide-range grid distortions in phoenix/training/augment.py, exposing parameters, forwarding arguments from train.py to augment_dynamic.py, and updating the specification in mixed-training-augmentation.md.
<!-- SECTION:FINAL_SUMMARY:END -->
