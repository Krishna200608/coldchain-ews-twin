# Experimental Design & Protocol

This document details the experimental setup, chronological partitioning protocol, data leakage safeguards, and synthetic injection methodology.

---

## 1. Chronological Partitioning Protocol (D6)

In time-series forecasting and anomaly detection, standard randomized k-fold cross-validation introduces catastrophic **lookahead data leakage**, as future diurnal cycles and seasonal transitions leak into historical training splits.

To maintain temporal validity, the dataset is partitioned chronologically based on a fixed 70% elapsed timeline split:

$$\text{Cutoff Timestamp} = t_{\min} + 0.70 \cdot (t_{\max} - t_{\min}) = \mathbf{2018\text{-}10\text{-}29\ 11:10:48}$$

```mermaid
flowchart LR
    Start["2018-07-28<br>Series Start"] --> TrainSplit["Training Partition (70% Time Elapsed)<br>ts < 2018-10-29 11:10:48<br>80,466 total rows (82.4%)"]
    TrainSplit --> Cutoff["Cutoff Boundary<br>2018-10-29 11:10:48"]
    Cutoff --> TestSplit["Held-Out Test Partition (30% Time Elapsed)<br>ts >= 2018-10-29 11:10:48<br>17,139 total rows (17.6%)"]
    TestSplit --> End["2018-12-08<br>Series End"]
```

### 1.1. Partition Breakdown by Series

| Partition Name | Out Series Rows | Out Share | In Series Rows | In Share | Combined Rows |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Train Partition** | 63,927 rows | 82.70% | 16,539 rows | 81.45% | 80,466 rows |
| **Held-Out Test Partition** | 13,372 rows | 17.30% | 3,767 rows | 18.55% | 17,139 rows |
| **Total** | **77,299 rows** | **100.0%** | **20,306 rows** | **100.0%** | **97,605 rows** |

---

## 2. Deep Learning Train/Validation Sub-Split (D11)

For the LSTM-Autoencoder, the training partition is chronologically subdivided:
- **`train_train` (Earliest 90%):** Used for backpropagation parameter updates.
- **`val` (Latest 10%):** Used strictly for EarlyStopping callback monitoring and threshold calibration.
- **Strict Boundary Guard:** Sliding windows are generated strictly within `train_train` and `val` independently; windows are prohibited from straddling the validation boundary.

---

## 3. Data Leakage Prevention Controls

The experiment enforces four strict anti-leakage invariants:

1. **Train-Only Normalization Parameters (D10):** Normalization statistics ($\mu_{\text{temp}}, \sigma_{\text{temp}}, \mu_{\text{gap}}, \sigma_{\text{gap}}$) are computed strictly from `train_train` and serialized to JSON. Test rows are normalized using these fixed parameters.
2. **Untuned Contamination Parameter (D7):** Isolation Forest is fitted with `contamination='auto'`. Tuning contamination to match the synthetic test injection ratio ($\approx 0.005$) would leak ground-truth test labels into the model.
3. **Recomputed Trailing Features (D5, D22):** Rolling features evaluated by models are recomputed from `temp_injected` strictly using trailing causal windows, preventing pre-injection ground truth from leaking into model inputs.
4. **Demarcation of Scientific Benchmark Claims (D26):** All empirical performance claims (PR-AUC, precision, recall, lead time gains) are computed exclusively on the **6 held-out test-side injections**. Train-side injections are reserved for UI demonstrations.

---

## 4. Controlled Anomaly Injection Matrix

Using `RANDOM_SEED = 42`, 30 synthetic injections were sampled across `Out` and `In` series with an isolation buffer of at least 5 readings:
- **24 Train-Side Injections:** (12 Out, 12 In) Occurred prior to $t_{\text{cutoff}}$.
- **6 Test-Side Injections:** (3 Out, 3 In) Occurred after $t_{\text{cutoff}}$.

### 4.1. The 6 Authoritative Test-Side Benchmark Injections

| ID | Series | Type | Start Timestamp | Duration | Magnitude / Setting |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`out_step_001`** | Out | Step | 2018-11-17 13:25:00 | 17 readings | $M = +10.97 ^\circ\text{C}$ spike |
| **`out_drift_009`** | Out | Drift | 2018-10-30 01:59:00 | 18 readings | $M_{\text{final}} = +13.56 ^\circ\text{C}$ ramp |
| **`out_flatline_012`**| Out | Flatline | 2018-12-04 21:03:00 | 12 readings | Frozen at $37.00 ^\circ\text{C}$ |
| **`out_flatline_013`**| Out | Flatline | 2018-11-25 01:14:00 | 12 readings | Frozen at $41.00 ^\circ\text{C}$ |
| **`in_step_018`** | In | Step | 2018-12-07 17:14:00 | 11 readings | $M = +10.37 ^\circ\text{C}$ spike |
| **`in_drift_023`** | In | Drift | 2018-11-02 07:41:00 | 10 readings | $M_{\text{final}} = +16.03 ^\circ\text{C}$ ramp |

