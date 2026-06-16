---
id: TASK-62
title: Consolidate V2 data structure and remove V1 naming
status: To Do
assignee: []
created_date: '2026-06-15 23:57'
labels: []
dependencies: []
ordinal: 62000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
V1 dataset is now deprecated. We should clean up the 'v2' naming by renaming the active data directory training_data_v2 to training_data and updating all references in scripts, documentation, and web server configuration to point to training_data.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Rename training_data_v2 directory to training_data (removing the legacy V1 data)
- [ ] #2 Update all references to training_data_v2 in the codebase (scripts, server, config files) to use training_data
- [ ] #3 Verify that the web labeling server, scripts, and model training pipeline function correctly after renaming
<!-- AC:END -->
