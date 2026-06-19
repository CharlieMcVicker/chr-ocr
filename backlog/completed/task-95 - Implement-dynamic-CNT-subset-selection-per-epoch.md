---
id: TASK-95
title: Implement dynamic CNT subset selection per epoch
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 20:41'
updated_date: '2026-06-17 20:45'
labels: []
dependencies: []
ordinal: 103000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update dataset preparation/mixing logic to dynamically rotate or sample fresh subsets of CNT data per epoch during training, rather than using a single static 10% split, ensuring Phoenix data dominates the epoch batches.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Modify scripts or config to support dynamic epoch-by-epoch selection of CNT samples
- [x] #2 Ensure split files (.lstmf) are generated correctly for each epoch's dynamic subset
- [x] #3 Ensure all parameters like dynamic subset size are parsed from the config/JSON to avoid magic numbers
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented dynamic Cherokee New Testament (CNT) subset selection per epoch during staged training. Configured TrainingConfig and scripts/train_staged.py to parse the new configuration options without magic numbers. Added manifest generation logic to phoenix/training/train.py to dynamically sample a fresh fraction of CNT lines per epoch using epoch-specific randomized seeding, ensuring Phoenix data dominates train batches.
<!-- SECTION:FINAL_SUMMARY:END -->
