---
id: TASK-132
title: Create a sweep configuration for new CNT augmentation and capping parameters
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 16:23'
updated_date: '2026-06-19 16:39'
labels: []
dependencies: []
ordinal: 150000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Set up a comprehensive sweep configuration file to test the performance impacts of the newly introduced Cherokee New Testament (CNT) augmentation and capping parameters (such as micro-dropout, ink wash smudging, and max_cnt_samples ceilings) across a series of training runs.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Design and create a new sweep configuration JSON under configs/
- [x] #2 Include search space variations for micro_dropout, smudge, and max_cnt_samples parameters
- [x] #3 Verify sweep config parses successfully with SweepConfig
- [x] #4 Execute the training sweep or dry-run and document initial results
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully created configs/sweep_cnt_aug_and_capping.json to test the performance impact of micro-dropout, ink smudging (smudge), and max_cnt_samples dataset capping parameters. Executed a dry-run to verify SweepConfig parsed successfully and deep merged all new parameters.
<!-- SECTION:FINAL_SUMMARY:END -->
