---
id: TASK-98
title: Sweep and tune Phoenix/CNT mixture ratio metaparameters
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 20:41'
updated_date: '2026-06-18 02:35'
labels: []
dependencies: []
ordinal: 106000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Conduct a hyperparameter sweep over the Phoenix/CNT dataset mixture ratios (e.g. 90/10, 80/20, 70/30) to locate the optimal balance between historical print recognition and vocabulary generalization.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Configure staged training loop sweep configurations
- [x] #2 Evaluate sweep results on both Phoenix and CNT test splits
- [x] #3 Document the optimal ratio and select the best model checkpoint
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The optimal Phoenix/CNT mixture ratio sweep was run, yielding 0.4 mixture ratio at epoch 24 as the optimal configuration. configs/train_mixed.json was updated with these optimal parameters.
<!-- SECTION:FINAL_SUMMARY:END -->
