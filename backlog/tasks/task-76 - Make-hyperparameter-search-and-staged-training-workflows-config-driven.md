---
id: TASK-76
title: Make hyperparameter search and staged training workflows config-driven
status: Done
assignee:
  - '@myself'
created_date: '2026-06-16 21:17'
updated_date: '2026-06-16 21:19'
labels: []
dependencies: []
priority: medium
ordinal: 75000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor the hyperparameter search and staged training data generation workflows to read parameters from structured configuration files mapped to Python dataclasses, enabling transparency on disk and saving of a standardized best_config.json.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define Python dataclass representing hyperparameter sweep and staged training parameters
- [x] #2 Support loading and saving configurations from/to JSON files
- [x] #3 Refactor training and sweep scripts to accept a --config command-line argument pointing to a config JSON
- [x] #4 Save the best-performing configuration from a sweep to best_config.json on disk
- [x] #5 Verify the config-driven training workflow runs successfully with a sample JSON configuration
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored hyperparameter sweep and staged training workflows to load configuration parameters via structured JSON configurations mapped to Python dataclasses. Created scripts/config.py defining configuration dataclasses, extracted the hardcoded search matrix to scripts/sweep_config.json, refactored train_staged.py to accept JSON configurations via --config, updated tune_meta_parameters.py to serialize/pass configurations and output the best config to best_config.json, and verified correct execution.
<!-- SECTION:FINAL_SUMMARY:END -->
