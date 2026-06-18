---
id: TASK-98
title: Sweep and tune Phoenix/CNT mixture ratio metaparameters
status: In Progress
assignee:
  - '@antigravity'
created_date: '2026-06-17 20:41'
updated_date: '2026-06-17 20:58'
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
- [ ] #1 Configure staged training loop sweep configurations
- [ ] #2 Evaluate sweep results on both Phoenix and CNT test splits
- [ ] #3 Document the optimal ratio and select the best model checkpoint
<!-- AC:END -->
