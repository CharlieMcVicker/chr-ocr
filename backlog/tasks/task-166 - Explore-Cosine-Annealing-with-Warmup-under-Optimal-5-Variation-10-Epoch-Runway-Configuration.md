---
id: TASK-166
title: >-
  Explore Cosine Annealing with Warmup under Optimal 5-Variation 10-Epoch Runway
  Configuration
status: To Do
assignee: []
created_date: '2026-06-23 01:41'
labels: []
dependencies: []
priority: medium
ordinal: 187000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Evaluate a Cosine Annealing with Warmup learning rate scheduler on a multi-experiment sweep under our current best training parameters (16 epochs, 5 variations per image, and an early mixture decay ending by Epoch 6, leaving a 10-epoch runway). This will test if the smoother learning rate transitions of cosine annealing can outperform the current best 5.81% Phoenix CER reached via exponential decay.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Create a new sweep config file configs/sweep_task_166_cosine_warmup_opt.json mimicking sweep_advance_from_optimal.json but using cosine_warmup schedule.
- [ ] #2 Sweep baseline learning rates (0.001, 0.0015, 0.002) with lr_warmup_epochs=4 and lr_eta_min=1e-5.
- [ ] #3 Execute the sweep and analyze results to see if it beats the 5.81% CER record.
<!-- AC:END -->
