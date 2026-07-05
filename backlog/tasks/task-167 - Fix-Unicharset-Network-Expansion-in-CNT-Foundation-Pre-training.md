---
id: TASK-167
title: Fix Unicharset Network Expansion in CNT Foundation Pre-training
status: To Do
assignee: []
created_date: '2026-06-24 14:38'
labels: []
dependencies: []
ordinal: 188000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The 3k CNT pre-training phase (pretrain_cnt_foundation_3k) does not pass old_traineddata to lstmtraining, preventing network expansion. This locks downstream fine-tuning sweeps continuing from cnt_foundation.checkpoint to the old unicharset, causing high line skip rates (e.g. 37.4%) and string encoding errors on Ꮐ, [, ], 4, and ? characters.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Ensure old_traineddata is correctly supplied during the pre-training phase
- [ ] #2 Verify that network expansion occurs properly and successfully adds new characters to the pre-trained checkpoint
- [ ] #3 Re-generate a pristine cnt_foundation.checkpoint with the corrected unicharset
- [ ] #4 Verify that downstream sweeps continuing from the new foundation do not throw encoding failures on updated characters
<!-- AC:END -->
