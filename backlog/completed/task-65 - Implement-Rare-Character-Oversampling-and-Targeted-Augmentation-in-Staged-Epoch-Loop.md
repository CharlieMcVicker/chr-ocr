---
id: TASK-65
title: >-
  Implement Rare Character Oversampling and Targeted Augmentation in Staged
  Epoch Loop
status: To Do
assignee: []
created_date: '2026-06-16 13:03'
labels: []
dependencies: []
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
To address class imbalance for rare characters (such as the historic Ꮐ character and others), implement targeted oversampling and heavier/more numerous augmentations specifically for training line crops containing these low-frequency characters during the staged training loop.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Identify low-frequency characters or support a configurable list of rare target characters
- [ ] #2 Oversample or generate more augmented variations per epoch for line crops containing target characters
- [ ] #3 Integrate logic into scripts/train_staged.py or scripts/augment_dynamic.py
- [ ] #4 Validate that rare character representation in epoch training sets is significantly increased
<!-- AC:END -->
