---
id: TASK-157
title: Run Higher CNT Phoenix Ratio Sweep with Regularization and Low LR
status: Done
assignee:
  - '@antigravity'
created_date: '2026-06-22 19:56'
updated_date: '2026-06-22 20:29'
labels:
  - training
  - sweep
dependencies: []
priority: high
ordinal: 178000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Configure and execute a single-run training sweep starting from the 3k pre-trained CNT checkpoint. The sweep will decay the CNT/Phoenix ratio from 0.5 down to 0.9 (90% Phoenix) with higher regularization and a smaller learning rate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Create configs/sweep_high_cnt_ratio.json with a single experiment configured with lower learning rate, higher regularization, and mixture decay starting from 0.5 to 0.9.
- [x] #2 Execute the single-run sweep in the background.
- [x] #3 Analyze the evaluation metrics and report outcomes.
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully configured and executed a new fine-tuning sweep on top of the 3k pre-trained CNT foundation checkpoint. The sweep used a mixture ratio schedule decaying from 0.5 (50% Phoenix) to 0.9 (90% Phoenix) with higher regularization and a smaller learning rate of 0.001. The experiment reached iteration 869. The best evaluation checkpoint was captured at iteration 355 with a Phoenix CER of 9.99% and CNT CER of 3.42%. After iteration 355, the Phoenix CER slightly degraded to 10.14% and 11.73%, suggesting that the combined high regularization and lower learning rate slowed down target adaptation compared to previous runs (e.g. 6.82% in Task 155).
<!-- SECTION:FINAL_SUMMARY:END -->
