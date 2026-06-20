---
id: TASK-141
title: Reduce destructive Phoenix noise parameters while retaining elastic warping
status: Done
assignee:
  - '@myself'
created_date: '2026-06-19 18:55'
updated_date: '2026-06-19 18:56'
labels: []
dependencies: []
priority: high
ordinal: 159000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Based on user feedback, keep spatial/elastic warping (distortion_prob=0.4) active for Phoenix, but reduce destructive augmentations (blur, shadow, coarse dropout, and bleedthrough) to mild levels (0.1) for general Phoenix data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Set blur_prob, shadow_prob, dropout_prob, and bleedthrough_prob to 0.1 in phoenix/config.py
- [x] #2 Retain distortion_prob at 0.4 in phoenix/config.py
- [x] #3 Verify configuration initialization
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Retained elastic warping/distortion (distortion_prob=0.4) for Phoenix training data while reducing destructive effects (blur_prob, shadow_prob, dropout_prob, bleedthrough_prob) to a mild 0.1 probability default in phoenix/config.py.
<!-- SECTION:FINAL_SUMMARY:END -->
