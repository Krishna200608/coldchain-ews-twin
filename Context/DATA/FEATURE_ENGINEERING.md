# Feature Engineering

The feature engineering subsystem computes mathematical representations that capture temporal dynamics, local thermal velocity, and cross-channel thermal gradients from raw IoT telemetry.

---

## 1. Feature Philosophy: Real Readings & Causal Boundaries

In accordance with Design Decisions **D1** (no resampling) and **D6** (chronological integrity):
- **Count-Based vs. Time-Based Windows:** Rolling statistics are computed over fixed counts of consecutive real observations ($N = 10$), rather than arbitrary time intervals (e.g., "last 10 minutes"). This maintains constant sample complexity and avoids artificial interpolation artifacts in sparse telemetry regions.
- **Strict Causality:** All rolling statistics use right-aligned, trailing windows. A feature at timestamp $t_i$ incorporates observations only from $\{t_k \mid k \le i\}$, guaranteeing zero forward lookahead leakage.
- **Normalization Causal Boundary (D10):** Normalization parameters (mean, standard deviation) for deep learning models are computed strictly from the chronological training partition ($t < t_{\text{cutoff}}$).

---

## 2. Feature Inventory & Formulations

### 2.1. Within-Series Inter-Arrival Gap (`gap_seconds`)
Measures the elapsed physical time since the preceding reading of the **same sensor channel** (D2):

$$\text{gap\_seconds}_i = t_i - t_{i-1} \quad (\text{seconds})$$

- **First Observation:** NaN (no preceding observation within series).
- **Physical Meaning:** Reflects sensor polling health, battery-saving throttles, or network dropouts.
- **Distribution:**
  - **Out Series:** Median = $60\text{ s}$, Mean = $148.6\text{ s}$, Max = $83,160\text{ s}$ (~23.1 hours).
  - **In Series:** Median = $120\text{ s}$, Mean = $566.2\text{ s}$, Max = $83,400\text{ s}$ (~23.2 hours).

### 2.2. Count-Based Trailing Rolling Statistics
Computed over the trailing $W = 10$ consecutive observations (`ROLLING_WINDOW = 10`):

$$\text{rolling\_mean}_i = \frac{1}{\min(i, W)} \sum_{k=0}^{\min(i, W)-1} T_{i-k}$$

$$\text{rolling\_std}_i = \sqrt{\frac{1}{\min(i, W) - 1} \sum_{k=0}^{\min(i, W)-1} \left( T_{i-k} - \text{rolling\_mean}_i \right)^2}$$

- **`min_periods` Parameter:** `min_periods=1` for mean; `min_periods=2` for standard deviation (index 0 is NaN).
- **Physical Meaning:** Smooths high-frequency sensor quantization noise while tracking short-term thermal trajectories.

### 2.3. Cross-Series Thermal Gradient (`in_out_diff`)
Measures the instantaneous temperature differential across the building/container thermal boundary:

$$\text{in\_out\_diff}_i = T_{\text{target}, i} - T_{\text{other}, \text{nearest}}$$

- **Matching Methodology:** Computed using `pd.merge_asof(direction='nearest')`.
- **Temporal Tolerance (`MAX_MATCH_MINUTES = 15`):** If the nearest observation in the opposing series is more than 15 minutes away, `in_out_diff` is set to NaN.
- **Coverage:**
  - Out $\to$ In: 94.70% valid (73,204 rows), 5.30% NaN (4,095 rows).
  - In $\to$ Out: 97.82% valid (19,864 rows), 2.18% NaN (442 rows).
- **Status (D5):** Excluded from the active Isolation Forest and LSTM input vectors to avoid cross-series recomputation complexity during streaming anomaly injection. Retained in clean reference tables for exploratory analysis.

### 2.4. Trailing Recomputed Features (`rolling_mean_if`, `rolling_std_if`) (D5, D22)
> [!IMPORTANT]
> When synthetic anomalies are injected into `temp_injected`, pre-computed rolling features become stale. If a model evaluated `temp_injected` alongside a pre-computed `rolling_mean` derived from clean `temp`, it would detect a trivial discrepancy caused by data leakage.
> 
> Therefore, `src/isolation_forest_model.py` and `src/twin_monitors.py` explicitly **recompute** trailing rolling statistics directly from `temp_injected`:
> - `rolling_mean_if`: Trailing 10-reading mean of `temp_injected`.
> - `rolling_std_if`: Trailing 10-reading standard deviation of `temp_injected`.

---

## 3. Model Feature Vectors

| Detector Model | Input Vector Dimensionality | Features Included | Preprocessing / Scaling Applied |
| :--- | :--- | :--- | :--- |
| **Naive Baseline** | 1 (Scalar) | `temp_injected` | Unscaled temperature (°C) compared to fixed static threshold |
| **Isolation Forest** | 4 (Vector) | `[temp_injected, gap_seconds, rolling_mean_if, rolling_std_if]` | Unscaled tree features; missing values imputed via trailing forward-fill |
| **LSTM-Autoencoder** | $30 \times 2$ (Matrix Window) | Timestep $t$: `[temp_injected_norm, log_gap_seconds_norm]` | Z-score normalization derived strictly from train split; $\ln(1 + \text{gap\_seconds})$ |

### 3.1. LSTM Input Normalization Parameters (D10)

Derived strictly from the training partition ($t < \text{cutoff\_ts}$):

```json
// lstm_norm_stats_out.json
{
  "temp_mean": 36.3312,
  "temp_std": 5.4871,
  "log_gap_mean": 4.1956,
  "log_gap_std": 0.8124
}

// lstm_norm_stats_in.json
{
  "temp_mean": 27.4208,
  "temp_std": 1.8315,
  "log_gap_mean": 4.8621,
  "log_gap_std": 1.1042
}
```
*(Values recorded from `data/processed/lstm_norm_stats_*.json`)*

