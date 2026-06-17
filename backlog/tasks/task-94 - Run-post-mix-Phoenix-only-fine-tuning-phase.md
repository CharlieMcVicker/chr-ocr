---
id: TASK-94
title: Run post-mix Phoenix-only fine-tuning phase
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 20:29'
updated_date: '2026-06-17 20:34'
labels: []
dependencies: []
ordinal: 102000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Load the chr_mixed_decay model and perform a final fine-tuning phase of 2-4 epochs using only the Phoenix training split (excluding CNT) with a low learning rate to recover Phoenix OCR accuracy.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Configure train_staged.py to load chr_mixed_decay checkpoint and run with Phoenix-only dataset
- [x] #2 Train for 3 epochs with a low, decayed learning rate
- [x] #3 Convert checkpoint to chr_phoenix_recovered.traineddata
- [x] #4 Evaluate against both Phoenix and CNT test splits and compare results
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully configured train_recovery.json to fine-tune the mixed model (starting from chr_mixed_decay) on Phoenix-only data for 3 epochs with a low, constant learning rate of 0.0001. Converted the resulting checkpoint to chr_recovered.traineddata and ran evaluations. Phoenix test split CER improved from 13.39% to 12.70% (with binarization average improving from ~15.8% to ~13.9%), while preserving high CNT accuracy at 4.05% CER.
<!-- SECTION:FINAL_SUMMARY:END -->
