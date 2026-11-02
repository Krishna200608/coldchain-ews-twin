# Architectural Decision Register (ADR)

This document is the authoritative register of all architectural, methodological, and engineering decisions (**D1 through D35**) governing the Cold Chain Early Warning System Digital Twin project.

---

## 1. Data Ingestion & Preprocessing Decisions

### D1: No Resampling or Grid Interpolation
- **Context:** IoT telemetry exhibits irregular inter-arrival intervals and sensor dropouts.
- **Decision:** Do not resample telemetry onto a uniform 1-minute grid. Retain original timestamps and compute features exclusively from real, observed readings.
- **Rationale:** Resampling with synthetic interpolation (forward-fill or splines) invents artificial observations, creates phantom autocorrelation, and masks true sensor blackout periods.
- **Files:** [`src/preprocessing.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/preprocessing.py), [`src/config.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/config.py).

### D2: Independent Series Partitioning (`Out` vs. `In`)
- **Context:** The raw dataset contains two interleaved categorical tags: `Out` (external ambient) and `In` (internal conditioned room).
- **Decision:** Treat `Out` and `In` as two completely independent time series. Compute `gap_seconds` strictly within each series.
- **Rationale:** External weather fluctuations and indoor room conditioning operate under distinct thermodynamic physics. Interleaving them distorts inter-arrival statistics.
- **Files:** [`src/preprocessing.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/preprocessing.py).

### D3: Non-Destructive Synthetic Anomaly Injection
- **Context:** Ground-truth anomaly labels are required to evaluate early warning performance.
- **Decision:** Apply synthetic perturbations exclusively to memory copies and persist them to separate labeled tables (`out_labeled.csv`, `in_labeled.csv`). Clean reference files (`out_features.csv`, `in_features.csv`) must remain immutable.
- **Rationale:** Preserves pristine ground-truth baselines for contamination-free threshold calculation.
- **Files:** [`src/anomaly_injection.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/anomaly_injection.py).

---

## 2. Baseline & Ground-Truth Formulation Decisions

### D4: Naive Baseline Threshold, Irreversibility, & Bounded Search Horizon
- **Context:** Need an empirical baseline representing standard industrial excursion alarms.
- **Decision:**
  - Baseline threshold $\tau = \mu_{\text{clean}} + 2\sigma_{\text{clean}}$, computed strictly from clean feature files.
  - Alarm trips at the first single reading exceeding $\tau$.
  - Proxy irreversibility ($t_{\text{irrev}}$) defined as the start of the first continuous 10-minute streak above $\tau$.
  - Lead time search horizon is bounded to $[t_{\text{onset}}, t_{\text{end}} + 60.0\text{ minutes}]$.
- **Rationale:** Bounding search prevents unrelated future heatwaves (weeks later) from being falsely attributed to injected faults.
- **Files:** [`src/baseline_and_labels.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/baseline_and_labels.py).

### D5 / D22: Recomputed Trailing Rolling Features on Injected Telemetry
- **Context:** When anomalies are injected, pre-computed rolling features become stale.
- **Decision:** Recompute `rolling_mean_if` and `rolling_std_if` over trailing 10-reading windows directly from `temp_injected`.
- **Rationale:** Prevents data leakage where models detect discrepancies between injected temperatures and stale unperturbed rolling averages.
- **Files:** [`src/isolation_forest_model.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/isolation_forest_model.py), [`src/twin_monitors.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/twin_monitors.py).

---

## 3. Machine Learning & Splitting Decisions

### D6: Chronological Train/Test Partitioning
- **Context:** Random train/test splits leak future seasonal cycles into past observations.
- **Decision:** Split dataset chronologically at 70% elapsed timeline: $t_{\text{cutoff}} = \text{2018-10-29 11:10:48}$. Fit models strictly on rows where $t < t_{\text{cutoff}}$.
- **Rationale:** Enforces realistic temporal causality and evaluates true out-of-sample generalization.
- **Files:** [`src/split_utils.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/split_utils.py), [`src/config.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/config.py).

### D7: Untuned Contamination Parameter (`contamination='auto'`)
- **Context:** Isolation Forest requires a contamination parameter defining expected anomaly prevalence.
- **Decision:** Use scikit-learn's default `contamination='auto'`.
- **Rationale:** Tuning contamination to match synthetic injection proportions ($\approx 0.005$) would leak ground-truth test labels into model hyperparameters.
- **Files:** [`src/isolation_forest_model.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/isolation_forest_model.py).

### D8: Reusing Baseline Irreversibility Timestamps
- **Context:** Comparing lead times across models requires an identical anchor event.
- **Decision:** Reuse $t_{\text{irrev}}$ computed in Milestone 2 for all model lead time comparisons.
- **Rationale:** Ensures lead time differences ($\Delta \text{Lead Time}$) reflect detector sensitivity differences rather than floating reference targets.
- **Files:** [`src/if_evaluation.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/if_evaluation.py), [`src/three_way_comparison.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/three_way_comparison.py).

---

## 4. Deep Learning Sequence Modeling Decisions

### D9: Count-Based Sliding Windowing for LSTM
- **Context:** LSTM models require fixed-size temporal matrices.
- **Decision:** Extract count-based sliding windows ($L = 30$ readings, stride $S = 5$ for training).
- **Rationale:** Matches D1 principles; avoids artificial time interpolation.
- **Files:** [`src/lstm_prep.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/lstm_prep.py).

### D10: Train-Only Normalization Statistics
- **Context:** Neural networks require standardized inputs ($Z$-score scaling).
- **Decision:** Compute $\mu$ and $\sigma$ for `temp_injected` and $\ln(1 + \text{gap\_seconds})$ strictly from the training partition and serialize to JSON.
- **Rationale:** Eliminates forward lookahead leakage into test-set normalization.
- **Files:** [`src/lstm_prep.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/lstm_prep.py).

### D11: Chronological Train/Validation Carving
- **Context:** Model training requires a validation split for early stopping.
- **Decision:** Carve the latest 10% of the training period as `val`; generate sliding windows strictly within `train_train` and `val` without crossing boundaries.
- **Files:** [`src/lstm_prep.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/lstm_prep.py).

### D12: LSTM-Autoencoder Architecture Specification
- **Context:** Need an architecture capable of learning healthy temporal manifolds.
- **Decision:** `LSTM(32)` $\to$ `RepeatVector(30)` $\to$ `LSTM(32, return_sequences=True)` $\to$ `TimeDistributed(Dense(2))`. Total parameters: 12,866.
- **Files:** [`colab/lstm_train.ipynb`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/colab/lstm_train.ipynb), [`src/twin_monitors.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/twin_monitors.py).

### D13: Anomaly Threshold Calibration from Train Causal Scores
- **Context:** Establishing an objective threshold for reconstruction MSE.
- **Decision:** Calibrate threshold $\tau_{\text{recon}} = \mu_{\text{train\_causal}} + 2\sigma_{\text{train\_causal}}$ using causal scores from uncorrupted training partitions.
- **Files:** [`src/lstm_evaluation.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/lstm_evaluation.py).

### D16: Causal Single-Window-per-Row Scoring
- **Context:** Online streaming cannot aggregate future window timesteps.
- **Decision:** At row $i$, evaluate window $[i-29, i]$ and compute anomaly score strictly from the MSE at the final timestep ($t = 29$).
- **Files:** [`src/lstm_evaluation.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/lstm_evaluation.py), [`src/twin_monitors.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/twin_monitors.py).

---

## 5. Digital Twin Simulation Decisions

### D17: Three-Stage Data Pipeline Topology
- **Context:** Structuring discrete-event simulation stages.
- **Decision:** Model Source $\to$ Transit $\to$ Destination as a software/telemetry data pipeline, not a physical multi-location cold-chain route.
- **Rationale:** Dataset carries a single constant location invariant (`room_id = 'Room Admin'`).
- **Files:** [`src/digital_twin.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/digital_twin.py).

### D18: SimPy Virtual Clock Advanced by Real Inter-Arrival Gaps
- **Context:** Advancing the simulation environment clock.
- **Decision:** Advance `env.now` by `env.timeout(gap_seconds)` for each reading. Replay uses `temp_injected`.
- **Files:** [`src/digital_twin.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/digital_twin.py).

### D19: Transit Latency Disabled by Default
- **Context:** Simulating network latency.
- **Decision:** Set `TRANSIT_LATENCY_SECONDS = 0.0`.
- **Rationale:** Eliminates synthetic transmission delay to allow exact row-by-row parity verification against batch evaluation.
- **Files:** [`src/config.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/config.py), [`src/digital_twin.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/digital_twin.py).

### D21: Milestone 5b Parity Audit
- **Context:** Proving digital twin streaming monitors match batch evaluations.
- **Decision:** Implement automated cross-check comparing batch vs. live alarm timestamps across all 30 injections and 3 detectors.
- **Files:** [`src/twin_crosscheck.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/twin_crosscheck.py).

### D23: Continuous Monitor State Buffers
- **Context:** Maintaining stateful sliding deques across replay boundaries.
- **Decision:** Retain continuous rolling deques throughout the simulation stream without flushing at train/test boundaries.
- **Files:** [`src/twin_monitors.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/twin_monitors.py).

### D24: Whole-Series Baseline vs. Train-Only ML Thresholds
- **Context:** Documenting differing operating regimes.
- **Decision:** Baseline computes threshold across whole clean series (matching M2); ML models calibrate strictly on train split.
- **Files:** [`src/twin_monitors.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/twin_monitors.py).

### D26: Demarcation of Scientific Benchmark vs. Deployment Demo
- **Context:** Evaluating train-side vs test-side synthetic injections.
- **Decision:** The 6 test-side injections form the only valid scientific benchmark. The 24 train-side injections are labeled as demo-only.
- **Files:** [`src/twin_crosscheck.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/twin_crosscheck.py), [`dashboard/components/banners.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/components/banners.py).

---

## 6. Dashboard & Presentation Architecture Decisions

### D27: Modular Dashboard Structure
- **Context:** Integrating models into Streamlit.
- **Decision:** Import verified monitors directly from `src/twin_monitors.py` rather than reimplementing detection logic.
- **Files:** [`dashboard/app.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/app.py).

### D28: Display-Only Replay Acceleration
- **Context:** Controlling playback speed in the UI.
- **Decision:** Speed sliders alter only client-side `time.sleep` intervals. Telemetry timestamps and values are mathematically unchanged.
- **Files:** [`dashboard/app.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/app.py).

### D29: Dual Operating Modes (Guided Tour & Free Explore)
- **Context:** Balancing executive presentation with scientific auditability.
- **Decision:** Implement Mode 1: Guided Tour (4 curated showcase steps) and Mode 2: Free Explore (all 30 injections).
- **Files:** [`dashboard/app.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/app.py), [`dashboard/constants.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/constants.py).

### D31: Persistent Structural Proxy Disclaimers
- **Context:** Ensuring academic integrity and transparency.
- **Decision:** Render persistent disclaimer banners stating the dataset is a structural proxy with no food-safety significance.
- **Files:** [`dashboard/components/banners.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/components/banners.py).

### D32: Fail-Fast Startup Integrity Verification Check
- **Context:** Preventing broken UI states caused by missing files.
- **Decision:** Execute `run_d32_startup_check()` to verify 8 required model and CSV artifacts before rendering.
- **Files:** [`dashboard/data_loader.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/data_loader.py).

### D33: Mandatory Silent Buffer Pre-Warming Protocol
- **Context:** Isolated replay windows cause cold-start calculation transients.
- **Decision:** Silently pre-warm monitor buffers with 10 (IF) and 30 (LSTM) historical readings immediately preceding window onset.
- **Files:** [`dashboard/replay_engine.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/replay_engine.py), [`tests/test_d33_prewarm.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/tests/test_d33_prewarm.py).

### D34: Dynamic Runtime Interpolation of Metadata
- **Context:** Displaying lead times and showcase narratives.
- **Decision:** Dynamically pull numbers from `three_way_comparison.csv` and `twin_crosscheck_report.csv` rather than hardcoding.
- **Files:** [`dashboard/components/showcase.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/dashboard/components/showcase.py).

### D35: Master Point-Wise Confusion Metrics Ground Truth
- **Context:** Resolving conflicting metric figures across drafts.
- **Decision:** Establish exact point-wise confusion matrix numbers (TP, FP, TN, FN) recorded in `if_pointwise_metrics.json` and `lstm_pointwise_metrics.json` as authoritative ground truth.
- **Files:** [`src/if_evaluation.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/if_evaluation.py), [`src/lstm_evaluation.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/lstm_evaluation.py).

