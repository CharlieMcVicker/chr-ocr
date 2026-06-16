---
id: TASK-75
title: Run high-resolution hyperparameter sweep around local optimum
status: To Do
assignee: []
created_date: '2026-06-16 21:14'
updated_date: '2026-06-16 21:19'
labels: []
dependencies: []
ordinal: 74000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Perform a targeted, high-resolution hyperparameter sweep around the newly discovered local optimum. We will evaluate gentle decay rates (decay of 0.7 every 4 epochs), intermediate augmentation levels (0.75x), and extended stepped-decay training runs up to 20 epochs to optimize the expanded charset model for both character (BCER) and word (BWER) accuracy.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Execute the high-resolution tuning sweep
- [ ] #2 Evaluate the resulting checkpoints on the test split
- [ ] #3 Document final findings and optimal parameters in doc-9 and doc-11
- [ ] #4 Define the high-resolution parameter grid (runs 23 to 26) in a JSON sweep configuration file
<!-- AC:END -->
