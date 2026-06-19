---
id: TASK-144
title: Create a script to generate and save metric plots to disk
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-19 21:57'
updated_date: '2026-06-19 22:28'
labels: []
dependencies: []
ordinal: 162000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A Python script to generate training and validation metrics graphs (loss, BCER, BWER, Phoenix CER, CNT CER, and weighted CER) and save them to disk for evaluation.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Reads training logs/metrics CSVs from training run directories
- [x] #2 Generates clear, beautiful plots for loss, BCER, BWER, and CER metrics
- [x] #3 Saves plots directly to the run's directory on disk (e.g. as PNG files)
- [x] #4 Supports evaluating and comparing multiple runs or a single run
- [x] #5 Runs easily from the terminal
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented a robust, high-resolution Python plotting utility generate_metric_plots.py using matplotlib under scripts/. The script parses training and evaluation CSV telemetry logs, producing beautiful, dark-themed plots for individual runs (saving to run directories) and multi-run overlays (comparison mode).
<!-- SECTION:FINAL_SUMMARY:END -->
