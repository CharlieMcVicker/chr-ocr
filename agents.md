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

## Python Environment Management (`uv`)

To run Python files, manage dependencies, or execute scripts, agents **MUST** use `uv`:
- **Never** invoke bare `python` or `pip` commands, and do **not** manually run `source .venv/bin/activate`.
- **Always** use `uv run <command>` for executing Python scripts, Flask servers, or other CLI tools (e.g., `uv run scripts/train_staged.py`).
- **Always** use `uv add <package>` (or `uv remove <package>`) for installing/managing dependencies.
- **Always** run `uv sync` to ensure the project virtual environment matches the lockfile.

*If you are an AI agent reading this, please ensure you review and strictly adhere to the guidelines provided in the `.agents/rules/` directory.*

## Code structure

Most code is inside the `phoenix` module, with the following structure

```
phoenix
├── __init__.py
├── config.py
├── layout
│   ├── __init__.py
│   ├── classification.py
│   ├── classify_layout.py
│   ├── extract_lines.py
│   ├── extract_low_confidence_rare_crops.py
│   ├── find_line_class_params.py
│   ├── ocr.py
│   ├── segmentation.py
│   └── test_layout_migration.py
├── manifest
│   ├── __init__.py
│   ├── add_predicted_lang_to_manifest.py
│   ├── build_frontend_index.py
│   ├── crops.py
│   ├── enrich_manifest_with_ftm.py
│   ├── filter_manifest.py
│   ├── operations.py
│   └── test_manifest_migration.py
├── text
│   ├── __init__.py
│   ├── align_verses.py
│   ├── normalization.py
│   ├── segment_verses.py
│   ├── test_normalization.py
│   ├── test_text_migration.py
│   └── update_unicharsets.py
├── tools
│   ├── __init__.py
│   ├── analyze_dataset_character_frequencies.py
│   ├── analyze_ocr_discrepancies.py
│   ├── apply_space_corrections.py
│   ├── download_scans.py
│   ├── evaluate_lang_classification.py
│   ├── find_missing_spaces.py
│   ├── integrate_cnt.py
│   ├── package_cnt_test_data.py
│   ├── prepare_training_data.py
│   ├── prepare_v2_training_data.py
│   ├── process_all_cnt.py
│   ├── process_all_scans.py
│   ├── scrape_all_cnt.py
│   ├── test_tools_migration.py
│   └── test_training_routes.py
├── training
│   ├── __init__.py
│   ├── augment.py
│   ├── augment_dataset.py
│   ├── augment_dynamic.py
│   ├── charset.py
│   ├── eval.py
│   ├── evaluate_checkpoints.py
│   ├── evaluate_mixed_model.py
│   ├── mix_datasets.py
│   ├── pre_augment_cnt.py
│   ├── sweep.py
│   ├── test_mixture_schedule.py
│   ├── test_pretraining_config.py
│   ├── test_sweep_checkpoint.py
│   ├── train.py
│   ├── train_staged.py
│   └── tune_meta_parameters.py
└── visualization
    ├── __init__.py
    ├── diagnose_columns.py
    ├── generate_binarization_graphs.py
    ├── generate_cnt_viewer.py
    ├── generate_column_confidence_histogram.py
    ├── generate_confidence_heatmaps.py
    ├── generate_confusion_matrix.py
    ├── generate_metric_plots.py
    ├── generate_performance_graphs.py
    ├── metrics_dashboard.py
    ├── plot_layout.py
    ├── preview_bounding_boxes.py
    ├── test_visualization_migration.py
    └── visualize_confusion.py
```