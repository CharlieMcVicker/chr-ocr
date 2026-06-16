---
id: TASK-54
title: Why do we get these errors during augmentation?
status: Done
assignee:
  - '@myself'
created_date: '2026-06-15 18:01'
updated_date: '2026-06-15 23:18'
labels: []
dependencies: []
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Address UserWarnings raised during dynamic data augmentation (scripts/augment_dynamic.py). Albumentations has deprecated/renamed certain arguments in the version we use (2.0.8). Specifically: 1. Argument(s) 'num_shadows_upper' are not valid for transform RandomShadow (use 'num_shadows_limit') 2. Argument(s) 'alpha_affine' are not valid for transform ElasticTransform (removed in newer versions of ElasticTransform)
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Replace 'num_shadows_upper' with 'num_shadows_limit' in RandomShadow initialization in scripts/augment_dynamic.py
- [x] #2 Remove 'alpha_affine' parameter from ElasticTransform initialization in scripts/augment_dynamic.py
- [x] #3 Run scripts/augment_dynamic.py and verify that the warnings are completely resolved
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Resolved Albumentations deprecated/invalid arguments in RandomShadow (replaced 'num_shadows_upper' with 'num_shadows_limit') and ElasticTransform (removed 'alpha_affine'). Verified warning resolution by building the pipeline using the local virtual environment.
<!-- SECTION:FINAL_SUMMARY:END -->
