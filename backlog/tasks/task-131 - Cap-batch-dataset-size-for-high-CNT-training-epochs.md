---
id: TASK-131
title: Cap batch/dataset size for high % CNT training epochs
status: In Progress
assignee:
  - '@subagent'
created_date: '2026-06-19 16:20'
updated_date: '2026-06-19 16:21'
labels: []
dependencies: []
modified_files:
  - phoenix/config.py
  - phoenix/training/sweep.py
  - phoenix/training/train.py
ordinal: 149000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Introduce a configurable limit on the number of Cherokee New Testament (CNT) lines sampled per epoch during training and sweeps, ensuring that epochs with high CNT fractions (low mixture ratios) do not excessively inflate the epoch dataset size.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add max_cnt_samples to TrainingConfig in phoenix/config.py
- [x] #2 Update SweepSampler.sample_to_list to support and respect max_cnt_samples
- [x] #3 Update run_staged_training to respect max_cnt_samples in both shared pool and non-shared pool branches
- [x] #4 Create unit/verification test to verify max_cnt_samples works under extreme mixture ratios
<!-- AC:END -->



## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add max_cnt_samples: Optional[int] = None to TrainingConfig in phoenix/config.py.\n2. Update SweepSampler.sample_to_list in phoenix/training/sweep.py to support and respect max_cnt_samples when sampling.\n3. Update run_staged_training in phoenix/training/train.py to respect max_cnt_samples in both branches (shared pool and non-shared pool).\n4. Create verification script scratch/verify_cap.py and execute it with uv run.\n5. Complete the checklist and commit changes.
<!-- SECTION:PLAN:END -->
