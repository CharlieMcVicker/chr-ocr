---
id: TASK-54
title: Why do we get these errors during augmentation?
status: To Do
assignee: []
created_date: '2026-06-15 18:01'
updated_date: '2026-06-15 19:53'
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
- [ ] #1 Replace 'num_shadows_upper' with 'num_shadows_limit' in RandomShadow initialization in scripts/augment_dynamic.py
- [ ] #2 Remove 'alpha_affine' parameter from ElasticTransform initialization in scripts/augment_dynamic.py
- [ ] #3 Run scripts/augment_dynamic.py and verify that the warnings are completely resolved
<!-- AC:END -->
