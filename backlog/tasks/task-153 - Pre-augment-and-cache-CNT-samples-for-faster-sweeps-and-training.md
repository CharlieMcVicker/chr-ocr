---
id: TASK-153
title: Pre-augment and cache CNT samples for faster sweeps and training
status: Done
assignee: []
created_date: '2026-06-22 13:51'
updated_date: '2026-06-22 16:18'
labels: []
dependencies: []
priority: medium
ordinal: 174000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Since we only use a fraction of CNT samples regularly, we can pre-augment the CNT dataset and cache the augmented images. This avoids running expensive dynamic augmentation on CPU during training and sweeps, drastically speeding up runtimes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create a script to pre-augment the CNT dataset with target heavy noise parameters.
- [x] #2 Implement caching and loading of pre-augmented CNT samples in the training pipeline.
- [x] #3 Verify identical model performance and significantly faster training speed.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create scripts/pre_augment_cnt.py to pre-generate and cache augmented CNT crops.\n2. Add use_cached_cnt and cnt_cache_dir to TrainingConfig.\n3. Integrate cached sample loading in train.py and bypass dynamic augmentation.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created pre_augment_cnt.py script to pre-generate and cache CNT crops with target heavy noise. Integrated use_cached_cnt and cnt_cache_dir configuration options inside training pipeline to load pre-augmented samples, bypassing CPU-heavy dynamic augmentation during sweeps/training.
<!-- SECTION:FINAL_SUMMARY:END -->
