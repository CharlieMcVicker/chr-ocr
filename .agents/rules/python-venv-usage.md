---
trigger: model_decision
description: Use this rule when writing or executing python code
---

# Python Environment Management with `uv`

When working with Python in this project, you MUST always use `uv`.

For all Python invocations and package management, you must:
1. Run Python scripts and tools using: `uv run <command>` (e.g., `uv run python scripts/my_script.py` or `uv run my_script.py`).
2. Manage dependencies using `uv add <package>` or `uv remove <package>`.
3. Keep the environment synchronized using `uv sync`.

Failure to follow this rule and using raw `pip` or activating standard `.venv` scripts will bypass lockfile tracking.
