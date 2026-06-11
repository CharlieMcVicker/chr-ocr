---
id: TASK-40
title: Implement sorting by low confidence in frontend /training page
status: Done
assignee: []
created_date: '2026-06-11 17:55'
updated_date: '2026-06-11 17:57'
labels: []
dependencies: []
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Update the labeling training page to allow users to sort items by low confidence score.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Sort toggle or dropdown exists for sorting by low confidence
- [x] #2 Low confidence items are sorted first when enabled
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added a checkbox in the sidebar to sort items by lowest ftm_confidence, falling back to 999 for items without confidence.
<!-- SECTION:FINAL_SUMMARY:END -->
