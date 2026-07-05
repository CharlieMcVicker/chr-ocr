---
id: TASK-171
title: Render line crop images instead of text on scan viewer
status: Done
assignee:
  - '@antigravity'
created_date: '2026-07-05 20:34'
updated_date: '2026-07-05 20:34'
labels: []
dependencies: []
priority: high
ordinal: 192000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
On the left scan viewer, replace the rendered text with the actual line crop images loaded from . Position the images absolutely inside the bounding boxes to reconstruct the original column appearance, and overlay interactive bounding box highlights on hover and search match.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create a symlink for line crops to public/line_crops (done)
- [x] #2 Remove text rendering from scan viewer
- [x] #3 Render corresponding line crop image inside each absolute-positioned bounding box container
- [x] #4 Ensure overlay highlights (hover, active, match) display correctly on top of the images
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Replaced rendered text with the actual line crop images loaded dynamically from public/line_crops (using a symlink to training_data/line_crops). The images are absolute-positioned to perfectly reconstruct the original newspaper layout on the left column viewer. Added an overlay highlight div to maintain hover, active search match, and search match state highlights seamlessly.
<!-- SECTION:FINAL_SUMMARY:END -->
