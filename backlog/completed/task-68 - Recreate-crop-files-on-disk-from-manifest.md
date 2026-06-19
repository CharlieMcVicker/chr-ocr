---
id: TASK-68
title: Recreate crop files on disk from manifest
status: Done
assignee:
  - '@agent'
created_date: '2026-06-16 16:59'
updated_date: '2026-06-16 17:11'
labels: []
dependencies: []
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Recreate crop files on disk for labeled and unlabeled data using bounding box data from manifest. Ignore not_cherokee and bad_crop entries.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Crop files exist on disk for all valid entries
- [x] #2 Crop files correspond to bounding box data in manifest
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Recreated all 895 missing crop files on disk for labeled and unlabeled dataset entries by loading raw scan images, performing column detection via Surya layout models, cropping lines according to manifest bboxes, reconstructing height normalization ratios, and saving to disk. All valid entries in the manifests now exist.
<!-- SECTION:FINAL_SUMMARY:END -->
