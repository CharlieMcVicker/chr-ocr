---
id: TASK-30
title: Evaluate minimal example training run against test datasets
status: Done
assignee: []
created_date: '2026-06-11 12:49'
updated_date: '2026-06-11 12:50'
labels: []
dependencies: []
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate .lstmf files for the test splits (base, otsu, su, sauvola, wolf) and run lstmeval against the newly trained checkpoint to summarize final accuracy on the test dataset.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Generate .lstmf test files
- [x] #2 Run lstmeval for all algorithms
- [x] #3 Summarize accuracy results
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Generated .lstmf for test split and evaluated the minimal training checkpoint. The final Character Error Rates are: Base (Grayscale): 40.5%, Otsu: 58.4%, Su: 66.8%, Sauvola: 52.1%, Wolf: 53.5%. Base grayscale performed the best.
<!-- SECTION:FINAL_SUMMARY:END -->
