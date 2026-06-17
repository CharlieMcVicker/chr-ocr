---
id: TASK-92
title: Run mixed CNT/Phoenix OCR training with learning rate decay
status: To Do
assignee: []
created_date: '2026-06-17 19:34'
labels: []
dependencies: []
ordinal: 100000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Execute staged training loop using optimal run_22 settings (step decay schedule, 5 variations per image) on the mixed manifest to improve Phoenix OCR accuracy while retaining CNT gains.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create configs/train_mixed_decay.json with step decay (0.5 rate, 4 decay epochs) and 5 variations per image
- [ ] #2 Run train_staged.py with the mixed decay configuration for 16 epochs
- [ ] #3 Convert the best checkpoint to chr_mixed_decay.traineddata
- [ ] #4 Evaluate chr_mixed_decay against Phoenix and CNT test sets and report comparative metrics
<!-- AC:END -->
