---
id: TASK-65
title: Parallelize .lstmf compilation in Staged Epoch Loop
status: Done
assignee:
  - '@agent'
created_date: '2026-06-16 12:44'
updated_date: '2026-06-16 12:46'
labels: []
dependencies: []
ordinal: 64000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Compiling dynamically augmented PNGs to .lstmf files sequentially is a significant bottleneck in the staged training epoch loop. We must parallelize this step using a thread pool to compile multiple images concurrently and speed up epoch transitions.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Implement parallel execution for .lstmf compilation in scripts/train_staged.py
- [x] #2 Expose a --max-workers parameter to control concurrency
- [x] #3 Verify that a 1-epoch training run executes successfully with parallel compilation enabled
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Expose --max-workers in argument parser.\n2. Import ThreadPoolExecutor from concurrent.futures.\n3. Parallelize Step C (PNG compilation to .lstmf files using ThreadPoolExecutor).\n4. Verify the changes by executing a quick 1-epoch test: .venv/bin/python scripts/train_staged.py --total-epochs 1 --iterations-per-epoch 10 --train-output-dir training_data_v2/test_run_output
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented parallel .lstmf compilation using ThreadPoolExecutor, added the --max-workers CLI argument, and successfully verified with a 1-epoch test run.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Parallelized .lstmf compilation under Step C in scripts/train_staged.py. A ThreadPoolExecutor handles the spawned tesseract processes concurrently. Added a new '--max-workers' command-line parameter to allow customizing thread count. Verified successfully using a 1-epoch test run with --max-workers 4.
<!-- SECTION:FINAL_SUMMARY:END -->
