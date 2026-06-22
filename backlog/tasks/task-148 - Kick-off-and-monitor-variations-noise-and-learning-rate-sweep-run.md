---
id: TASK-148
title: 'Kick off and monitor variations, noise, and learning rate sweep run'
status: Done
assignee:
  - '@myself'
created_date: '2026-06-20 00:16'
updated_date: '2026-06-20 00:50'
labels: []
dependencies: []
ordinal: 166000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Kick off the newly proposed sweep run exploring variations_per_image, noise levels, and learning rate based on the optimal early decay schedule.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Start the sweep run using uv run python scripts/tune_meta_parameters.py --sweep-config configs/sweep_variations_noise_lr.json
- [x] #2 Ensure the sweep runs successfully in the background
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
The variations, noise, and learning rate sweep completed successfully. It found a new absolute record-holder: 'learning_rate_high_0.003' at iteration 2400, which reached an outstanding 5.80% Phoenix CER (and 5.73% CNT CER).
<!-- SECTION:FINAL_SUMMARY:END -->
