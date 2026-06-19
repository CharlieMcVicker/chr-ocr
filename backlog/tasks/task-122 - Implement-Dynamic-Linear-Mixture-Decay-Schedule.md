---
id: TASK-122
title: Implement Dynamic Linear Mixture Decay Schedule
status: To Do
assignee: []
created_date: '2026-06-19 13:09'
updated_date: '2026-06-19 13:55'
labels: []
dependencies: []
ordinal: 136000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a dynamic dataset mixture scheduler in train.py that linearly decays the proportion of Cherokee New Testament (CNT) lines (i.e. increases Phoenix ratio to 1.0) as training progresses through epochs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add a configurable mixture_schedule configuration parameter block (supporting linear decay) to TrainingConfig in phoenix/config.py.
- [ ] #2 Update phoenix/training/train.py to calculate the epoch-specific mixture ratio dynamically at the start of each epoch.
- [ ] #3 Ensure dynamic dataset generation split sizes are computed and constructed using the updated epoch-specific mixture ratio.
- [ ] #4 Verify that early epochs contain the specified starting fraction of CNT, while later epochs transition linearly to the target final Phoenix ratio.
- [ ] #5 Update the mathematical specification and behavior of the Dynamic Linear Mixture Decay Schedule in backlog/docs/research/mixed-training-augmentation.md
<!-- AC:END -->
