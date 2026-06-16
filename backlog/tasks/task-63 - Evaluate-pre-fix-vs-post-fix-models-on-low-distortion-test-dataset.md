---
id: TASK-63
title: Evaluate pre-fix vs post-fix models on low-distortion test dataset
status: To Do
assignee: []
created_date: '2026-06-16 00:24'
labels: []
dependencies: []
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
With the Albumentations augmentation bugs resolved, the model training set is significantly more challenging, which increased the reported error rate. Create an evaluation run to compare the pre-fix model checkpoint (from doc-9, e.g. June 12 best run 10) and the post-fix model checkpoint (June 16 best run 10) on a low-distortion (clean/base grayscale) test dataset to isolate whether generalization improved or if the model simply experienced performance degradation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Locate June 12 pre-fix best model checkpoint and June 16 post-fix best model checkpoint
- [ ] #2 Define a test set containing clean/low-distortion images
- [ ] #3 Evaluate both model checkpoints using lstmeval on the low-distortion test set
- [ ] #4 Document and compare the resulting BCER/BWER scores in a new research backlog document
<!-- AC:END -->
