---
id: TASK-51
title: Add overwrite/force flag to FTM enrichment script
status: Done
assignee:
  - '@agent'
created_date: '2026-06-15 16:42'
updated_date: '2026-06-15 16:43'
labels: []
dependencies: []
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add an argparse flag (e.g. --force or --overwrite) to scripts/enrich_manifest_with_ftm.py to force recalculation of all predictions. Update doc-12 with the new flag.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add argparse to scripts/enrich_manifest_with_ftm.py with --force/--overwrite option
- [x] #2 Update doc-12 with the new flag
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added --force flag to scripts/enrich_manifest_with_ftm.py using argparse to allow force recalculation/overwrite of existing predictions. Updated doc-12 to guide users on using --force instead of the manual jq deletion command.
<!-- SECTION:FINAL_SUMMARY:END -->
