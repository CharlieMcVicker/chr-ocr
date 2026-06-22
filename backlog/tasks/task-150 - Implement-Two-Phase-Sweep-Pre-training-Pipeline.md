---
id: TASK-150
title: Implement Two-Phase Sweep Pre-training Pipeline
status: Done
assignee: []
created_date: '2026-06-22 12:58'
updated_date: '2026-06-22 13:06'
labels: []
dependencies: []
priority: high
ordinal: 168000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modify the sweep configuration and orchestration to support a pre_training_phase where we can pre-train a model on CNT once, save it to disk, and then run multiple Phoenix fine-tuning sweeps starting from that checkpoint.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Define PreTrainingPhaseConfig in phoenix/config.py and integrate it into SweepConfig
- [x] #2 Update run_meta_parameter_sweep in phoenix/training/sweep.py to process pre_training_phase
- [x] #3 Skip pre-training if the checkpoint already exists at pre_training_phase.checkpoint_path
- [x] #4 Run pre-training using scripts/train_staged.py if the checkpoint is missing, copying the best/latest checkpoint to checkpoint_path upon completion
- [x] #5 Ensure all main sweep experiments continue_from the pre-trained checkpoint
- [x] #6 Create configs/sweep_two_stage_example.json demonstrating the new pre-training phase
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
## Proposed Approach

1. **Update config.py**:
   - Add `PreTrainingPhaseConfig` dataclass containing `config` (TrainingConfig), `output_dir`, and `checkpoint_path`.
   - Update `SweepConfig` to contain an optional `pre_training_phase: Optional[PreTrainingPhaseConfig]`. Ensure it is serialized/deserialized properly in `to_dict` and `from_dict`.

2. **Update sweep.py**:
   - In `run_meta_parameter_sweep`, check if `pre_training_phase` is present.
   - If `pre_training_phase.checkpoint_path` exists on disk, print a message and skip pre-training.
   - If not, serialize `pre_training_phase.config` to `config.json` inside its `output_dir`, and run `scripts/train_staged.py` on it.
   - Find the final checkpoint from that run and copy/rename it to `pre_training_phase.checkpoint_path`.
   - For all subsequent experiments, override their `exp_config.continue_from` to point to the `pre_training_phase.checkpoint_path`.

3. **Create Demo Config**:
   - Create `configs/sweep_two_stage_example.json` with a pretraining block and simple Phoenix fine-tuning experiments.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented Two-Phase Pre-training and Fine-tuning Sweep Pipeline. Defined PreTrainingPhaseConfig in config.py, integrated into SweepConfig with full serialization support, updated run_meta_parameter_sweep in sweep.py to handle pre-training, skip pre-training if checkpoint exists, copy the latest checkpoint, and override continue_from for experiments. Created configs/sweep_two_stage_example.json.
<!-- SECTION:FINAL_SUMMARY:END -->
