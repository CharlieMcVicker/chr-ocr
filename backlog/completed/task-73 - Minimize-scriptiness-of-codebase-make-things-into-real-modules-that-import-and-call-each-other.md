---
id: TASK-73
title: >-
  Minimize "scriptiness" of codebase - make things into real modules that import
  and call each other
status: Done
assignee:
  - '@agent'
created_date: '2026-06-16 19:53'
updated_date: '2026-06-16 21:30'
labels:
  - needs-scoping
  - debt
dependencies: []
ordinal: 72000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Refactor the codebase to transition from standalone Python utility scripts to a structured, modular Python package. This refactoring will organize duplicate and scripty logic into distinct, imported modules to improve reusability, testability, and clean code boundaries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create a structured phoenix python package at the project root with clear submodules: phoenix.config, phoenix.manifest, phoenix.training, and phoenix.layout.
- [x] #2 Consolidate config classes (TrainingConfig, SweepConfig) from scripts/config.py into phoenix.config.
- [x] #3 Consolidate dataset/manifest operations (such as splitting, filtering, label reconsolidation, and crop/manifest utility functions) into phoenix.manifest.
- [x] #4 Consolidate ML & augmentation logic (staged epoch loop, training utils, hyperparameter sweeps, elastic/morphological augmentations) into phoenix.training.
- [x] #5 Consolidate column processing, line extraction, and layout classifications (using Tesseract and Surya) into phoenix.layout.
- [x] #6 Update existing scripts in scripts/ and server files in server/ to import logic from the new phoenix package, reducing scripts to thin CLI entry point wrappers.
- [x] #7 Run the Flask server and verify that local web UI workflows (uploads, binarization, layout processing, labeling updates) function properly without regressions.
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Create phoenix package and config module\n2. Consolidate manifest/crop operations under phoenix/manifest\n3. Consolidate training & ML under phoenix/training\n4. Consolidate layout & segmentation under phoenix/layout\n5. Refactor scripts/ and server/ to use the package\n6. Verify and update docs
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Refactored scripts and server/app.py to use phoenix package instead of scripts/ and local server/ modules directly
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Refactored the codebase to transition utility scripts and duplicate logic into a structured phoenix package, comprising config, manifest, training, and layout submodules. Updated scripts to import logic from the package as thin CLI wrappers, and verified system-wide import compatibility.
<!-- SECTION:FINAL_SUMMARY:END -->

## Definition of Done
<!-- DOD:BEGIN -->
- [x] #1 Verify linting and check that existing tests/scripts run successfully under the new package layout.
- [x] #2 Update documentation (like Operations Guide) to reflect the new package structure and imports.
<!-- DOD:END -->
