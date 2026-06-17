# AI Agents in Cherokee Phoenix OCR

This project utilizes advanced AI agent workflows (like Antigravity) to automate tasks, track project state, manage technical debt, and search the codebase efficiently.

## Agent Architecture

This repository uses a **Supervisor/Task Implementor** pattern for autonomous work:
1. **Supervisor Planner**: Evaluates requests, researches the codebase, breaks complex work into smaller discrete tasks, and creates Backlog Tasks.
2. **Task Implementor**: A specialized subagent that executes the scoped Backlog Tasks strictly according to its acceptance criteria.

## Backlog CLI Tool (`backlog`)

The `backlog` CLI tool is the central source of truth for project management. 
- Agents **MUST** use the `backlog` CLI to manage all task statuses, assignments, and updates.
- **Rule of Thumb**: No work should be performed without an associated Backlog task. If a task doesn't exist for the work requested by the user, agents must create and scope a new task before beginning work.
- **Never edit `.md` task files directly**. All task creation and modification must be executed via the `backlog` CLI (e.g., `backlog task edit 42 --check-ac 1`).
- You can find more details in `.agents/rules/backlog-task-management.md`.

## Ember Semantic Search (`ember`)

To minimize token context overhead and improve the signal-to-noise ratio, agents are instructed to prefer the `ember` CLI over traditional grep tools.
- **Search**: `ember find <query>` locates implementations using semantic embeddings rather than syntax-matching alone.
- **Read**: `ember cat <chunk>` retrieves exact code chunks.
- You can find more details in `.agents/rules/file-searching-and-reading.md`.

## Agent Rules Directory

Agent behavior is deeply customized using Markdown rule files located in `.agents/rules/`. These rule files act as conditional prompt inclusions to guide the agent based on context:

- **`backlog-task-creator.md`**: Guidelines for creating and scoping new tasks.
- **`backlog-task-implementor.md`**: Guidelines for executing tasks and completing the Definition of Done.
- **`backlog-task-management.md`**: Strict instructions on how to use the `backlog` CLI tool.
- **`file-searching-and-reading.md`**: Strict instructions on how to use `ember` for semantic search.
- **`python-venv-usage.md`**: Ensures agents execute Python code and shell scripts within the project's virtual environment.
- **`supervisor-planner.md`**: Guidelines for the Supervisor Planner agent when breaking down complex work.
- **`task-implementation-subagent.md`**: Guidelines for Task Implementor subagents.

## Python Virtual Environment (`.venv`)

To run Python files or execute scripts, agents **MUST** use the local virtual environment:
- **Never** invoke bare `python` or `pip` commands as they will run against the system Python or fail.
- **Explicit Executable Paths**: Use `.venv/bin/python` for executing scripts and `.venv/bin/pip` for package management.
- **Activation Alternative**: Or run `source .venv/bin/activate && python ...` inside a shell invocation.
- **Dependency Missing Issues**: New worktrees or checkouts may sometimes have incomplete dependency sets. If imports like `cv2` or `PIL` fail, explicitly install them using `.venv/bin/pip install`.

*If you are an AI agent reading this, please ensure you review and strictly adhere to the guidelines provided in the `.agents/rules/` directory.*
