---
id: TASK-192
title: Audit backlog/docs for staleness
status: Done
assignee:
  - '@agent-k'
created_date: '2026-07-21 17:02'
updated_date: '2026-07-21 17:03'
labels: []
dependencies: []
ordinal: 200000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Check each document under backlog/docs against the current codebase implementation and flag stale documents for deletion.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Review all docs in backlog/docs subdirectories
- [x] #2 Identify stale or inaccurate documentation
- [x] #3 Flag stale docs for deletion or delete them as per review outcome
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Audited all 20 documents under backlog/docs/. Identified active guides needing script path updates (scripts/ -> phoenix/) and removed 5 obsolete archived documents that describe outdated architectures or superseded initial specs.
<!-- SECTION:FINAL_SUMMARY:END -->
