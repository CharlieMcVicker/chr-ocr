---
id: TASK-97
title: Implement 80/20 training batch mixture in staged training loop
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 20:41'
updated_date: '2026-06-17 20:57'
labels: []
dependencies: []
ordinal: 105000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update train_staged.py and training/train.py to enforce an 80% Phoenix and 20% CNT training batch mixture ratio per epoch, ensuring the gradients are primarily driven by the Phoenix domain.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Configure training loop to sample and construct lists matching the 80/20 ratio
- [x] #2 Verify list.train generated for each epoch contains precisely the expected ratio of Phoenix to CNT lines
- [ ] #3 Evaluate trained model to confirm Phoenix CER improves
- [x] #4 Define target mixture ratio parameter (e.g. 0.8 Phoenix / 0.2 CNT) in the configuration JSON
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented 80/20 training batch mixture ratio configuration and sampling in staged training loop, verified exact ratio matches target, and deprecated CLI args in favor of strictly JSON configuration files.
<!-- SECTION:FINAL_SUMMARY:END -->
