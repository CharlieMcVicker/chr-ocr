---
id: TASK-152
title: Cap CNT pre-training dataset size to accelerate pre-training phase
status: To Do
assignee: []
created_date: '2026-06-22 13:51'
labels: []
dependencies: []
priority: medium
ordinal: 173000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Dynamic pre-training on Cherokee New Testament (CNT) uses the entire dataset which is very large. We should try capping the number of CNT samples generated per epoch during pre-training to see if we can get similar results significantly faster.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Add a config parameter to cap the number of CNT samples used during the 100% CNT pre-training phase.
- [ ] #2 Verify that pre-training epoch duration is reduced proportionally.
- [ ] #3 Compare pre-trained foundation checkpoint quality against the uncapped baseline.
<!-- AC:END -->
