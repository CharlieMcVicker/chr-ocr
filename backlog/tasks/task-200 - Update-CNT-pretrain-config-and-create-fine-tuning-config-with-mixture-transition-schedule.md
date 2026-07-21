---
id: TASK-200
title: >-
  Update CNT pretrain config and create fine-tuning config with mixture
  transition schedule
status: Done
assignee:
  - '@agent'
created_date: '2026-07-21 21:31'
updated_date: '2026-07-21 21:31'
labels: []
dependencies: []
ordinal: 206000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update configs/cnt-pretrain/cnt-pretrain.json with cosine warmup LR schedule. Create configs/fine-tuning/phoenix-finetune.json configured for fine-tuning with a mixture_schedule transitioning from CNT-heavy to pure Phoenix.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Update configs/cnt-pretrain/cnt-pretrain.json to use lr_schedule='cosine_warmup' and lr_warmup_epochs=2
- [x] #2 Create directory configs/fine-tuning/ and configs/fine-tuning/phoenix-finetune.json
- [x] #3 Configure mixture_schedule in phoenix-finetune.json to transition from 0.2 (80% CNT) to 1.0 (100% Phoenix) across epochs
- [x] #4 Verify both configs load cleanly via TrainingConfig.load_from_json()
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Update configs/cnt-pretrain/cnt-pretrain.json to use lr_schedule='cosine_warmup', lr_warmup_epochs=2, learning_rate=0.001.
2. Create directory configs/fine-tuning/.
3. Instantiate TrainingConfig for fine-tuning with mixture_schedule transitioning start_ratio=0.2 (mostly CNT) to end_ratio=1.0 (pure Phoenix), lr_schedule='step' (or cosine_warmup with step decay), and save to configs/fine-tuning/phoenix-finetune.json.
4. Validate both configs with TrainingConfig.load_from_json().
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Updated configs/cnt-pretrain/cnt-pretrain.json to use cosine warmup LR schedule. Created directory configs/fine-tuning/ and sample config configs/fine-tuning/phoenix-finetune.json with mixture_schedule transitioning from 0.2 (mostly CNT) to 1.0 (pure Phoenix) over 8 epochs, allowing Phoenix-specific characters like historic Ꮐ (nah) to activate.
<!-- SECTION:FINAL_SUMMARY:END -->
