---
id: TASK-152
title: Cap CNT pre-training dataset size to accelerate pre-training phase
status: Done
assignee: []
created_date: '2026-06-22 13:51'
updated_date: '2026-06-22 16:18'
labels: []
dependencies: []
priority: medium
ordinal: 173000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Dynamic pre-training on Cherokee New Testament (CNT) uses the entire dataset which is very large. We should try capping the number of CNT samples generated per epoch during pre-training to see if we can get similar results significantly faster.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add a config parameter to cap the number of CNT samples used during the 100% CNT pre-training phase.
- [x] #2 Verify that pre-training epoch duration is reduced proportionally.
- [x] #3 Compare pre-trained foundation checkpoint quality against the uncapped baseline.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add pretrain_cnt_cap (Optional[int]) to TrainingConfig in config.py.\n2. Handle mixture_ratio == 0.0 in train.py and cap sampled lines to pretrain_cnt_cap.\n3. Add unit tests in phoenix/training/.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented pretrain_cnt_cap inside TrainingConfig and integrated it into master pool and batch-epoch sampling logic to enforce dataset size capping during pure CNT pre-training epochs.
<!-- SECTION:FINAL_SUMMARY:END -->
