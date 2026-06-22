---
id: doc-17
title: Recent Training Sweeps and Optimal Model Findings
type: other
created_date: '2026-06-20 00:52'
updated_date: '2026-06-22 19:45'
---
# Cherokee OCR Training Sweeps and Optimal Model Findings

This document summarizes the methodology, findings, and trends from our recent hyperparameter and mixture-decay sweeps on Cherokee Tesseract OCR training. These sweeps successfully drove Phoenix Character Error Rate (CER) down from over **10.8%** to a record-breaking **5.80%** (in the baseline unicharset configuration) and verified optimal parameters under our updated, corrected unicharset.

---

## 🚀 1. The Core Breakthroughs

Through systematic, multi-stage training sweeps, we identified and refined critical dimensions of our training configuration:

```mermaid
graph TD
    A["Historical Baseline (10.86% CER)"] --> B["Dynamic Mixture Schedule (7.05% CER)"]
    B --> C["Optimal Early Decay (5.96% CER)"]
    C --> D["Slightly Higher Learning Rate (5.80% CER)"]
    D --> E["Corrected Unicharset & 3k Cap (8.44% CER)"]
    E --> F["Lower Learning Rates + Decay (6.82% CER)"]
    style F fill:#4CAF50,stroke:#388E3C,stroke-width:2px,color:#fff
```

1. **Auxiliary Regularization via CNT Dataset**: Training solely on Phoenix scans led to severe overfitting and flatlining. Introducing Cherokee New Testament (CNT) synthetic line crops as a regularizer was crucial.
2. **Early Mixture Decay**: Slowly decaying the CNT regularizing noise so the model transitions primarily to Phoenix scans near the end of training yielded massive gains. 
3. **The Power of Higher Learning Rates (Legacy Unicharset)**: Tweaking the fine-tuning learning rate up from `0.002` to `0.003` unlocked the best-performing checkpoints on the historic unicharset.
4. **Corrected Unicharset & Low LR with Decay**: Moving to the corrected unicharset (with 'Ꮐ' and target brackets) and capping CNT samples at 3k initially raised CER. Applying lower learning rates (`0.001` - `0.0025`) paired with step decay successfully drove CER down to a new optimal **6.82%**.

---

## 📈 2. Summary of Sweep Phases & Findings

### Phase 1: Dynamic Mixture Decay Schedule
- **Objective**: Test the decay of CNT synthetic data from 30% down to different final levels (retaining between 0% and 5% noise) versus a flat baseline.
- **Key Findings**:
  - **Overfitting with 0% noise**: Retaining exactly 0% CNT noise (`end_ratio = 1.00`) resulted in early saturation and flatlining at **10.86% Phoenix CER**, demonstrating that a minor regularizing signal is required throughout.
  - **Retention of 2% Noise**: Keeping exactly 2% CNT noise (`end_ratio = 0.98`) yielded a substantial improvement down to **7.05% Phoenix CER**.

---

### Phase 2: Optimal Early Decay Sweeps
- **Objective**: Investigate whether ending the mixture decay early (Epoch 5, 6, or 7) to provide a longer runway of pure fine-tuning iterations improves accuracy.
- **Key Findings**:
  - **Epoch 5 Decay (1000 Iterations)** with **1%** final noise (`ratio_0.99`) broke the 6% barrier, reaching a then-record **5.96% Phoenix CER** at iteration 2400.
  - **Epoch 7 Decay (1400 Iterations)** with **1%** final noise reached **6.59% Phoenix CER**.
  - **Conclusion**: Releasing the regularizer earlier (around iteration 1000) provides the model with the necessary runway to maximize its adaptation to Phoenix scan layouts.

---

### Phase 3: Variations, Noise Levels, and Learning Rates
- **Objective**: Explore the impact of dataset variations (`variations_per_image: 3 vs 5`), Phoenix noise probabilities, and learning rates (`0.001 vs 0.002 vs 0.003`).
- **Key Findings**:
  - **Learning Rate dominates fine-tuning**:
    - Raising learning rate to **`0.003`** resulted in our legacy **absolute best performance: 5.80% Phoenix CER** (and **5.73% CNT CER**).
    - Lowering learning rate to **`0.001`** severely limited adaptation, stalling Phoenix CER at **10.61%**.
  - **High Stability on Noise and Variations**: Changing dataset size variations to 5, or modifying Phoenix scan noise probabilities up/down, made zero difference in final convergence (all reaching exactly **5.94% Phoenix CER** at 1600 iterations).

---

### Phase 4: Two-Phase Learning Rate and Punctuation Sweep (Task 151)
- **Objective**: Transition to a corrected unicharset (retaining brackets and 'Ꮐ') and cap CNT at 3,000 samples to accelerate sweeps. Test higher learning rates (`0.004` - `0.005`) and targeted punctuation retention (3% residual noise with bracket-heavy samples).
- **Key Findings**:
  - **Adaptation Limit**: High learning rates of `0.004` and `0.005` were too aggressive for adaptation in this corrected space, leading to suboptimal convergence (e.g. `two_stage_lr_004_3k` reaching only **7.64% Phoenix CER**).
  - **Baseline**: The `0.003` baseline learning rate under the new unicharset and 3k cap produced **7.73% Phoenix CER** at 1600 iterations.

---

### Phase 5: Two-Stage Lower Learning Rate Sweep with Decay (Task 155)
- **Objective**: Test lower fine-tuning learning rates (`0.001` to `0.0025`) paired with step decay (`0.6` decay rate every `3` epochs) on the corrected unicharset.
- **Key Findings**:
  - **Dramatic Improvements**: Lower learning rates with step decay successfully stabilized fine-tuning and adaptation.
  - **Top Champion**: **`two_stage_punc_heavy_lr_002_decay`** achieved a stellar **6.82% Phoenix CER** at iteration 1200, while maintaining healthy CNT CER of **3.75%**.
  - **Consistency**: Even at the extremely low base rate of `0.0015` with heavy punctuation, the model achieved **7.37% Phoenix CER**, proving the efficacy of step decay.

---

## 📋 3. Trend Summarization Matrix

| Parameter Group | Tested Range | Impact on Phoenix CER | Trend / Actionable Insight |
| :--- | :--- | :--- | :--- |
| **Final CNT Ratio** | `0.95` to `1.00` | **Critical** (5.96% vs 10.86%) | Retaining **1% to 3%** residual noise prevents early saturation; removing it entirely triggers severe overfitting. |
| **Decay End-Point** | Epoch 5 (1000 iter) to Epoch 7 (1400 iter) | **High** (5.96% vs 6.59%) | Ending linear decay early (**1000 iterations**) gives the model more pure training iterations to adapt. |
| **Learning Rate** | `0.001` to `0.005` | **Critical** (6.82% vs 10.61%) | Under the new unicharset, lower fine-tuning rates (`0.0015` - `0.002`) with step decay dominate adaptation, while higher rates (`0.004` - `0.005`) are too aggressive. |
| **Step LR Decay** | Enabled (0.6 / 3 epochs) vs Flat | **High** (6.82% vs 7.73%) | Step decay prevents adaptation saturation and allows lower learning rates to converge more accurately. |
| **Variations Per Image**| `3` to `5` | **None** (identical results) | Variation size of **3** is fully sufficient. |

---

## 🏆 4. Champion Configuration and Best Model

The reigning champion configuration under the **corrected unicharset** and **3k CNT cap** is saved to **[`best_config.json`](file:///Users/charlesmcvicker/code/phoenix/best_config.json)** and its checkpoint to **[`best_checkpoint.checkpoint`](file:///Users/charlesmcvicker/code/phoenix/best_checkpoint.checkpoint)**:

- **Decay Endpoint**: Epoch 5 (1000 iterations)
- **Final Mixture Ratio**: 0.97 (3% CNT regularizing noise with bracket-heavy samples)
- **Base Learning Rate**: `0.002` with Step Decay (`0.6` factor / `3` epochs)
- **Phoenix Validation CER**: **6.82%** 🌟
- **CNT Validation CER**: **3.75%**
