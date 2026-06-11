---
id: TASK-28
title: Add Python calling rule to .agents
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-11 03:21'
updated_date: '2026-06-11 03:25'
labels: []
dependencies: []
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a rule to the .agents/ directory that specifies instructions for writing or modifying Python code in the project. The rule must explicitly state that all Python commands and scripts should be run using the virtual environment located at .venv/.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Test results: Running `python --version` directly fails with 'command not found'. However, `.venv/bin/python --version` successfully returns 'Python 3.14.3'. This means any agent trying to run python code must explicitly use the `.venv/bin/python` executable path or activate the virtual environment first (e.g. `source .venv/bin/activate && ...`). The rule should clearly instruct agents to use `.venv/bin/python` for all python invocations, as well as using `.venv/bin/pip` for any package management to ensure dependencies are installed in the right place.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added .agents/rules/python-venv-usage.md rule specifying to use .venv/bin/python and .venv/bin/pip for all Python operations.
<!-- SECTION:FINAL_SUMMARY:END -->
