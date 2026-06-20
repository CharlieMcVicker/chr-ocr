---
id: TASK-148
title: 'Kick off and monitor variations, noise, and learning rate sweep run'
status: In Progress
assignee:
  - '@myself'
created_date: '2026-06-20 00:16'
updated_date: '2026-06-20 00:16'
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
- [ ] #1 Start the sweep run using uv run python scripts/tune_meta_parameters.py --sweep-config configs/sweep_variations_noise_lr.json
- [ ] #2 Ensure the sweep runs successfully in the background
<!-- AC:END -->
