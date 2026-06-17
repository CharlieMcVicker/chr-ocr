---
id: TASK-92
title: Run mixed CNT/Phoenix OCR training with learning rate decay
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-17 19:34'
updated_date: '2026-06-17 19:56'
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
- [x] #1 Create configs/train_mixed_decay.json with step decay (0.5 rate, 4 decay epochs) and 5 variations per image
- [x] #2 Run train_staged.py with the mixed decay configuration for 16 epochs
- [x] #3 Convert the best checkpoint to chr_mixed_decay.traineddata
- [x] #4 Evaluate chr_mixed_decay against Phoenix and CNT test sets and report comparative metrics
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully completed optimal mixed training run using learning rate decay. Packaged the final model as chr_mixed_decay.traineddata and evaluated it against base and CNT test splits. The new model achieves 13.39% CER and 42.45% WER on Phoenix Test, and 3.66% CER and 11.21% WER on CNT, compared to chr_mixed_best's 11.88% CER / 40.91% WER on Phoenix and 3.23% CER / 9.68% WER on CNT.
<!-- SECTION:FINAL_SUMMARY:END -->
