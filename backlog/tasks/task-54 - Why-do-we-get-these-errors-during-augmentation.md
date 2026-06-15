---
id: TASK-54
title: Why do we get these errors during augmentation?
status: To Do
assignee: []
created_date: '2026-06-15 18:01'
updated_date: '2026-06-15 18:05'
labels:
  - needs-scoping
dependencies: []
ordinal: 56000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
[Dynamic Augmentation] Total: 276. Train (only to be augmented): 166
/Users/charlesmcvicker/code/phoenix/scripts/augment_dynamic.py:115: UserWarning: Argument(s) 'num_shadows_upper' are not valid for transform RandomShadow
  A.RandomShadow(num_shadows_upper=2, shadow_dimension=5, p=0.3),
/Users/charlesmcvicker/code/phoenix/scripts/augment_dynamic.py:120: UserWarning: Argument(s) 'alpha_affine' are not valid for transform ElasticTransform
  A.ElasticTransform(alpha=1, sigma=15, alpha_affine=15, border_mode=cv2.BORDER_REPLICATE, p=1.0),
Dynamic augmentation complete. Generated variations in training_data_v2/dataset_epoch
<!-- SECTION:DESCRIPTION:END -->
