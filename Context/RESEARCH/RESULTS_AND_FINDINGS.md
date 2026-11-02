# Empirical Results & Research Findings

This document compiles the verified empirical findings, comparative performance tables, and benchmark evaluations across the Cold Chain Early Warning System Digital Twin project.

---

## 1. Primary Empirical Findings

1. **Isolation Forest Provides Significant Early Warning on Thermal Drifts:**
   On test drift injection `out_drift_009`, Isolation Forest detected the incipient trajectory shift at `01:59:00`, while the naive baseline threshold did not trip until `03:03:00`. This achieved an early warning lead time of **+64.0 minutes** prior to irreversible threshold excursion. Similarly, on `in_drift_023`, it achieved **+11.0 minutes** of advance notice.
2. **Deep Sequence Models Exhibit Temporal Memory Inertia:**
   The LSTM-Autoencoder required multiple consecutive out-of-distribution observations to populate its 30-timestep sliding window before reconstruction error exceeded the detection threshold. On `out_drift_009`, this caused a **14-minute lag** behind the baseline threshold ($t_{\text{alarm}} = \text{03:17:00}$).
3. **Static Thresholds Fail Completely on In-Range Sensor Faults:**
   On sensor flatlines occurring within normal operating ranges (`out_flatline_012`), the baseline detector generated **0 alarms**. In contrast, structural models detected the loss of natural thermal variance.
4. **Environment Entropy Dictates Model Precision:**
   In high-entropy outdoor ambient environments (`Out`), temperature swings generated high false positive rates for both ML models ($\text{FPR} = 45.6\%$ for IF, $20.5\%$ for LSTM). In conditioned indoor environments (`In`), the LSTM-Autoencoder achieved an **FPR of only 2.85%** and a superior **PR-AUC of 0.3852**.

---

## 2. Master Early Warning Scorecard (Test Injections)

Evaluated across the 6 held-out test-side synthetic injections (`data/processed/three_way_comparison.csv`):

| Injection ID | Series | Fault Type | Irreversibility Timestamp | Baseline Lead Time | Isolation Forest Lead Time | LSTM-Autoencoder Lead Time | IF Delta vs. Baseline | LSTM Delta vs. Baseline | Empirical Finding |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`out_step_001`** | Out | Step | 2018-11-17 13:25:00 | 0.0 min | 0.0 min | 0.0 min | 0.0 min | 0.0 min | Synchronous detection on large jump |
| **`out_drift_009`** | Out | Drift | 2018-10-30 03:03:00 | 0.0 min | **64.0 min** | -14.0 min | **+64.0 min** | -14.0 min | Decisive early warning by IF; sequence lag by LSTM |
| **`out_flatline_012`**| Out | Flatline | None (Below $\tau$) | None | Alert at 21:09 | Alert at 21:03 | **Advantage** | **Advantage** | Baseline blind spot; detected by IF and LSTM |
| **`out_flatline_013`**| Out | Flatline | None (Below $\tau$) | None | Alert at 01:22 | None | **Advantage** | None | Detected by IF; subtle shift missed by LSTM |
| **`in_step_018`** | In | Step | 2018-12-07 17:14:00 | 0.0 min | 0.0 min | 0.0 min | 0.0 min | 0.0 min | Synchronous trip at step onset |
| **`in_drift_023`** | In | Drift | 2018-11-02 08:07:00 | 0.0 min | **11.0 min** | 0.0 min | **+11.0 min** | 0.0 min | Proactive early warning runway by IF |

---

## 3. Point-Wise Statistical Performance (D35 Ground Truth)

Evaluated across 17,139 held-out test rows (13,372 Out rows, 3,767 In rows):

| Metric | Out: Isolation Forest | Out: LSTM-Autoencoder* | In: Isolation Forest | In: LSTM-Autoencoder* |
| :--- | :--- | :--- | :--- | :--- |
| **True Positives (TP)** | 52 | 13 | 21 | 16 |
| **False Positives (FP)** | 6,067 | 2,722 | 1,010 | 106 |
| **True Negatives (TN)** | 7,240 | 10,556 | 2,734 | 3,609 |
| **False Negatives (FN)** | 13 | 52 | 2 | 7 |
| **Point-Wise Recall** | **80.00%** | 20.00% | **91.30%** | 69.57% |
| **Point-Wise Precision**| 0.85% | 0.48% | 2.04% | **13.11%** |
| **F1-Score** | 0.0168 | 0.0093 | 0.0398 | **0.2207** |
| **False Positive Rate** | 45.59% | 20.50% | 26.98% | **2.85%** |
| **PR-AUC (Continuous)** | **0.0676** | 0.0049 | 0.2371 | **0.3852** |

*\*Note: LSTM metrics exclude the 29 initial causal blind-spot rows.*

---

## 4. Academic Literature Benchmark Comparison

| Dimension | Standard Industrial Practice | Academic Literature Benchmark (2023–2025) | Cold Chain EWS Digital Twin (This Work) |
| :--- | :--- | :--- | :--- |
| **Detection Paradigm** | Static scalar thresholds (e.g., HACCP $4^\circ\text{C}$ / $8^\circ\text{C}$ limits) | Offline deep learning autoencoders (e.g., Zhang et al., 2024) | **Tri-model comparative suite:** Naive Baseline vs. Isolation Forest vs. LSTM-Autoencoder |
| **Early Warning Runway** | Post-hoc excursion alarms ($0.0\text{ min}$ advance notice) | Theoretical point-wise F1 reported; lead times unquantified | **Quantified lead-time runways:** Demonstrated **+64.0 minutes** of proactive advance notice |
| **Streaming Simulation** | Replay via static batch CSV scripts or real-time lab benches | Synthetic Poisson queues; wall-clock hardware-in-the-loop | **Discrete-event SimPy digital twin:** $>1.9\text{M}\times$ accelerated virtual clock with real inter-arrival gaps |
| **Verification & Parity**| Unverified transfer from offline Python to edge firmware | Discrepancies between offline and online inference ignored | **Milestone 5b Parity Audit:** Verified **42 / 42 (100%) parity match** ($0.0\text{s}$ drift) between batch and twin |
| **Governance & Notice** | Assumed perfect sensor fidelity; claims extrapolated | Structural limitations and food-safety proxy status omitted | **Rigorous proxy governance (D31):** Persistent disclaimers and dynamic runtime metadata interpolation |

