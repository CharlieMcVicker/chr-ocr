---
id: TASK-138
title: Consolidate sweep_mixture_ratios onto tune_meta_parameters
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-19 18:23'
updated_date: '2026-06-19 18:28'
labels: []
dependencies: []
priority: high
ordinal: 156000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Remove the adhoc sweep_mixture_ratios.py script and consolidate its functionality into tune_meta_parameters.py and the core run_meta_parameter_sweep module.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Support evaluation mode choice (lstmeval vs mixed model weighted CER) in run_meta_parameter_sweep
- [x] #2 Expose dataset-dir, results-file, and evaluation-mode options in tune_meta_parameters.py
- [x] #3 Implement cleanup of old master pools and custom master_pool_prefix if configured
- [x] #4 Remove scripts/sweep_mixture_ratios.py
- [x] #5 Verify core consolidation and correctness of the new unified script
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Consolidated the adhoc sweep_mixture_ratios.py script onto the unified and general tune_meta_parameters.py/run_meta_parameter_sweep core driver. Support was added for both fast 'bcer' (lstmeval) and robust 'mixed' (evaluate_mixed_model.py) evaluation modes. Carried over recent improvements such as master pool cleanup, custom master_pool_prefix setting, prominent evaluation epoch headers, correct unicharset paths, and setting optimal epochs before saving configs. Verified the implementation successfully using dry-runs.
<!-- SECTION:FINAL_SUMMARY:END -->
