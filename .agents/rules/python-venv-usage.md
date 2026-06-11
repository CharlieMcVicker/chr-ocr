---
trigger: model_decision
description: Use this rule when writing or executing python code
---

# Python Virtual Environment Usage

When working with Python in this project, you MUST always use the local virtual environment located at `.venv`. 

The global `python` and `pip` commands are not available and will fail.

For all Python invocations and package management, you must either:
1. Use the full path to the executable: `.venv/bin/python` or `.venv/bin/pip`
2. Or activate the virtual environment first in your command: `source .venv/bin/activate && python ...`

Failure to follow this rule will result in 'command not found' errors or installing dependencies in the wrong location.
