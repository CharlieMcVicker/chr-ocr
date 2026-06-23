---
id: TASK-159
title: Create Sweep Config with Heavier Phoenix Distortions and 5/7 Variations
status: Done
assignee:
  - '@agent'
created_date: '2026-06-22 21:50'
updated_date: '2026-06-22 22:43'
labels: []
dependencies: []
priority: high
ordinal: 180000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a new two-stage training sweep configuration based on the 3k CNT pre-trained foundation, testing 5 and 7 variations per image and heavier Phoenix distortions (blur, bleedthrough) without stroke thinning.
<!-- SECTION:DESCRIPTION:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Created sweep config with 5/7 variations and heavier Phoenix distortions. Successfully ran the 10-experiment sweep in the background. The best run was two_stage_var_5_heavy_combined_lr_002_3k at iteration 400 (evaluating checkpoint 650) achieving Phoenix CER: 8.47%, CNT CER: 4.30%, Weighted CER: 4.59%.
<!-- SECTION:FINAL_SUMMARY:END -->
