---
id: TASK-110
title: Add filter view for low-confidence rare character crops to labeling interface
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-18 18:21'
updated_date: '2026-06-18 18:29'
labels: []
dependencies: []
ordinal: 124000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate a filter view into the main server labeling interface to allow users to specifically review and label low-confidence line crops containing rare/confused characters ('[', ']', '4', 'Ꮞ', '?', 'Ꭾ'). This should display crops extracted by the active learning script.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add a filter dropdown or checkbox in the labeling interface UI to show only rare/confused character crops
- [x] #2 Implement backend support to query/serve these filtered crops from the manifest
- [x] #3 Ensure the user can save/commit updated labels for these crops
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Modify server/app.py /training endpoint to support filter=rare query parameter.\n2. Modify server/templates/training.html to add a checkbox for low-confidence rare/confused characters ('[', ']', '4', 'Ꮞ', '?', 'Ꭾ') and filter list dynamically client-side.\n3. Verify saving/updating labels works perfectly with the filter.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Integrated a comprehensive filter view for low-confidence rare/confused character crops into the Cherokee OCR training/labeling interface. This includes backend parameter filtering support via '/training?filter=rare' on the Flask route and a dynamic checkbox on the frontend to filter crops client-side instantaneously.
<!-- SECTION:FINAL_SUMMARY:END -->
