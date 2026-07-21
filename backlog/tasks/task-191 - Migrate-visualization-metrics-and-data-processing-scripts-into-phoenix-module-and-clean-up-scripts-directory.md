---
id: TASK-191
title: >-
  Migrate visualization, metrics, and data processing scripts into phoenix
  module and clean up scripts directory
status: Done
assignee:
  - '@agent'
created_date: '2026-07-21 16:13'
updated_date: '2026-07-21 16:46'
labels: []
dependencies: []
ordinal: 199000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move visualization and dashboard scripts (generate_binarization_graphs.py, generate_cnt_viewer.py, generate_column_confidence_histogram.py, generate_confidence_heatmaps.py, generate_confusion_matrix.py, generate_metric_plots.py, generate_performance_graphs.py, metrics_dashboard.py, visualize_confusion.py, diagnose_columns.py, plot_layout.py, preview_bounding_boxes.py, download_scans.py, integrate_cnt.py, package_cnt_test_data.py, process_all_cnt.py, process_all_scans.py, scrape_all_cnt.py, apply_space_corrections.py, find_missing_spaces.py, analyze_dataset_character_frequencies.py, analyze_ocr_discrepancies.py, test_training_routes.py) into phoenix modules or tools, and remove the scripts directory.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Move remaining scripts into phoenix package
- [x] #2 Remove scripts/ directory completely once empty
- [x] #3 Verify repository passes tests and linting
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully migrated all remaining visualization, metrics, diagnostic, and data processing scripts from scripts/ into phoenix/visualization/ and phoenix/tools/, updated internal import paths, deleted the scripts/ directory, added migration tests, and verified that pytest passes cleanly (17 passed).
<!-- SECTION:FINAL_SUMMARY:END -->
