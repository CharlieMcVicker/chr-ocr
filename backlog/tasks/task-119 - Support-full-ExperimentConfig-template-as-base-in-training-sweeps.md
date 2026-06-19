---
id: TASK-119
title: Support full ExperimentConfig template as base in training sweeps
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 13:02'
updated_date: '2026-06-19 13:03'
labels: []
dependencies: []
priority: medium
ordinal: 133000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the sweep 'base' config feature to allow specifying a full ExperimentConfig structure (containing both 'config' and default 'eval_epochs') in the 'base' block, allowing individual experiments to inherit 'eval_epochs' and deep-merge their nested config overrides.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Support 'base' block formatted as an ExperimentConfig dict (with nested 'config' and optionally 'eval_epochs')
- [x] #2 Inherit 'eval_epochs' from base if not specified in individual experiments
- [x] #3 Deep merge experiment config overrides with base 'config'
- [x] #4 Maintain backward compatibility for flat 'base' configs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated SweepConfig to expect 'base' as a nested ExperimentConfig-like structure with 'config' and optionally 'eval_epochs' as suggested. Verified via scratch tests.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented support for a nested 'base' configuration containing 'config' and default 'eval_epochs'. In individual experiments, if 'eval_epochs' is not specified, it is inherited from 'base'; and experiment-level 'config' overrides are deep-merged onto the base config dictionary. Confirmed with a clean test suite passing.
<!-- SECTION:FINAL_SUMMARY:END -->
