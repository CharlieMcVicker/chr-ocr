---
id: TASK-201
title: Configure pytest testpaths in pyproject.toml to scope tests to phoenix/
status: Done
assignee:
  - '@agent'
created_date: '2026-07-21 21:36'
updated_date: '2026-07-21 21:37'
labels: []
dependencies: []
ordinal: 207000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure pytest testpaths in pyproject.toml so pytest only discovers test files in the phoenix module and ignores temporary scratch scripts.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add [tool.pytest.ini_options] testpaths = ['phoenix'] to pyproject.toml
- [x] #2 Verify that uv run pytest passes cleanly with 0 failures
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add testpaths = ['phoenix'] under [tool.pytest.ini_options] in pyproject.toml.\n2. Run uv run pytest to verify all 17 tests pass with 0 failures.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Configured [tool.pytest.ini_options] testpaths = ['phoenix'] in pyproject.toml so pytest correctly scopes test discovery to the active phoenix/ module and ignores legacy scratch scripts.
<!-- SECTION:FINAL_SUMMARY:END -->
