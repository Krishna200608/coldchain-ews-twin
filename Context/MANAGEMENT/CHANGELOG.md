# Project Changelog

All notable technical evolutions, milestone completions, and architectural upgrades for the Cold Chain Early Warning System Digital Twin are recorded here.

---

## [2.3.0] — 2026-11-02 (Research Proposal P1: Variational LSTM-AE with Uncertainty Quantification)
### Added
- Created `src/models/vlstm_ae.py` implementing `VLSTMAutoencoder` with Monte Carlo uncertainty estimation and ELBO loss with linear KL annealing.
- Built headless GPU background training pipeline `scripts/train_vlstm_ae.py` and real-time monitor script `scripts/monitor_training.sh`.
- Exported Jupyter notebook `colab/vlstm_ae_train.ipynb`.
- Trained models in detached daemon session on NVIDIA RTX 5000 Ada GPU, saving `models/vlstm_out.pt` and `models/vlstm_in.pt`.
- Integrated `VLSTMMonitor` into `src/twin_monitors.py` with aleatoric/epistemic uncertainty decomposition and confidence classification (`HIGH_CONFIDENCE_ALARM` vs `LOW_CONFIDENCE_ALARM`).
- Added unit and monitor test suites `tests/test_vlstm_ae.py` and `tests/test_vlstm_monitor.py` (all passing).
- Evaluated test split in `scripts/evaluate_vlstm.py`:
  - `in_drift_023`: +97.0 min early warning with 3.91% uncertainty (`HIGH_CONFIDENCE_ALARM`).
  - `in_step_018`: +16.0 min early warning with 11.09% uncertainty (`HIGH_CONFIDENCE_ALARM`).
  - `out_flatline_012`: Detected +4.0 min early with 9.69% uncertainty (`HIGH_CONFIDENCE_ALARM`).
- Documented Architectural Decision **D38** in `docs/AD_LOG.md`.

---

## [2.2.0] — 2026-11-02 (Research Proposal P2: Physics-Informed LSTM-AE / PILSTM-AE)
### Added
- Created `src/models/pilstm_ae.py` implementing `PILSTMAutoencoder` with Newton's Law of Cooling thermodynamic loss regularization.
- Created GPU training pipeline `scripts/train_pilstm_ae.py` and exported Jupyter notebook `colab/pilstm_ae_train.ipynb`.
- Trained models on NVIDIA RTX 5000 Ada GPU, saving `models/pilstm_out.pt` and `models/pilstm_in.pt`.
- Integrated `PILSTMMonitor` into `src/twin_monitors.py` with physical spike categorization (`SENSOR_ARTIFACT` vs `TEMPERATURE_EXCURSION`).
- Added unit and monitor test suites `tests/test_pilstm_ae.py` and `tests/test_pilstm_monitor.py` (all tests passing).
- Evaluated test-split performance in `scripts/evaluate_pilstm.py`:
  - In series Precision rose from 13.11% to 19.15%, Recall from 69.57% to 78.26%, and FPR dropped from 2.85% to 2.03%.
  - Out series FPR dropped from 20.28% to 12.52% (38.3% relative reduction).
  - Solved LSTM sequence lag: turned `out_drift_009` from -14.0 min late to +18.0 min early, and `in_drift_023` to +178.0 min early.
- Documented Architectural Decision **D37** in `docs/AD_LOG.md`.

---

## [2.1.0] — 2026-11-02 (Research Proposal P4: Online Adaptive Thresholding via Kalman + CUSUM)
### Added
- Created `src/adaptation/adaptive_threshold.py` implementing `KalmanCUSUMAdapter` for online dynamic threshold adaptation under non-stationary sensor drift.
- Integrated adaptive threshold tracking into `src/twin_monitors.py` (`IFMonitor`, `LSTMMonitor`) and `dashboard/` components.
- Added comprehensive unit test suite in `tests/test_adaptive_threshold.py` (5/5 tests passing).
- Evaluated full 77,259-reading test-split stream in `scripts/evaluate_adaptive_threshold.py`, demonstrating a 35.5% relative reduction in Isolation Forest FPR (45.68% down to 29.45%) on the Out series.
- Preserved 100% bit-for-bit backward parity (D33) with existing benchmark models.
- Documented Architectural Decision **D36** in `docs/AD_LOG.md`.

---

## [2.0.0] — 2026-11-02 (Milestone 7: Centralized SSOT Architecture)
### Added
- Created centralized `/Context` Single Source of Truth (SSOT) documentation repository comprising 44 structured markdown modules.
- Established rigorous architectural decision mapping (**D1 through D35**) with cross-references to authoritative source code.
- Added explicit reconciliation of documentation discrepancies (duration constants, LSTM hidden units, and heading numbering gaps).
- Documented verified point-wise confusion matrix numbers and lead-time benchmarks.

---

## [1.5.0] — 2026-10-28 (Milestone 6.3: Presentation Dashboard & Viva Tour)
### Added
- Integrated modular Streamlit dashboard application in `dashboard/` with dual operating modes (Guided Tour and Free Explore).
- Implemented **D33 Buffer Pre-Warming Protocol** eliminating cold-start transients during localized window replays.
- Implemented interactive Altair telemetry chart with dynamic playhead rule and collapsible anomaly score trajectories.
- Added animated Play/Pause controls with configurable display-only playback speed factors (`1x` to `Instant`).
- Added automated unit test suite in `tests/test_d33_prewarm.py`.

---

## [1.4.0] — 2026-09-20 (Milestone 5b: Streaming Monitors & Parity Audit)
### Added
- Implemented stateful streaming monitors in `src/twin_monitors.py` (`BaselineMonitor`, `IFMonitor`, `LSTMMonitor`) with continuous rolling deques (D23).
- Implemented Milestone 5b Cross-Check Verification Audit (`src/twin_crosscheck.py`).
- Proved 100% mathematical parity across all 42 valid test and baseline comparisons ($0.0\text{ seconds}$ temporal drift).

---

## [1.3.0] — 2026-09-19 (Milestone 5a: SimPy Digital Twin Replay Engine)
### Added
- Built discrete-event simulation engine in `src/digital_twin.py` using SimPy.
- Modeled 3-stage data pipeline topology: Source $\to$ Transit $\to$ Destination (D17).
- Advanced virtual clock by real inter-arrival gaps (`gap_seconds`), achieving $>1.9\text{M}\times$ acceleration over physical wall-clock time.

---

## [1.2.0] — 2026-09-19 (Milestone 4b: Causal Evaluation & Three-Way Scorecard)
### Added
- Implemented causal single-window-per-row scoring (`src/lstm_evaluation.py`) using MSE at the last timestep ($t=29$).
- Calibrated anomaly threshold $\tau_{\text{recon}}$ from train causal scores ($2\sigma$ heuristic).
- Compiled master three-way comparison scorecard (`data/processed/three_way_comparison.csv`).

---

## [1.1.0] — 2026-09-18 (Milestone 4a: LSTM Windowing & Cloud Training)
### Added
- Implemented sliding window extraction in `src/lstm_prep.py` ($L=30, S=5$).
- Serialized train-only normalization statistics to JSON (`lstm_norm_stats_*.json`).
- Executed cloud GPU training on Google Colab (`colab/lstm_train.ipynb`) with early stopping, exporting `models/lstm_out.h5` and `models/lstm_in.h5`.

---

## [1.0.0] — 2026-09-18 (Milestone 3: Isolation Forest Model)
### Added
- Implemented chronological train/test splitting at $t_{\text{cutoff}} = \text{2018-10-29 11:10:48}$ (`src/split_utils.py`).
- Trained Isolation Forest models with `contamination='auto'` on recomputed trailing features (`src/isolation_forest_model.py`).
- Evaluated point-wise metrics, precision-recall curves, and lead-time runways (`src/if_evaluation.py`).

---

## [0.2.0] — 2026-09-17 (Milestone 2: Preprocessing, Features & Anomaly Injection)
### Added
- Parsed raw timestamps with mandatory `dayfirst=True` guard and eliminated duplicate row (`src/preprocessing.py`).
- Partitioned dataset into independent `Out` (77,299 rows) and `In` (20,306 rows) feature tables.
- Engineered within-series `gap_seconds`, count-based rolling statistics, and cross-channel `in_out_diff`.
- Generated 30 synthetic injections (step, drift, flatline) with `RANDOM_SEED = 42` onto data copies (`src/anomaly_injection.py`).
- Computed clean baseline thresholds and proxy irreversibility ($D_{\text{irrev}} = 10\text{ min}$) within a 60-minute bounded horizon (`src/baseline_and_labels.py`).

---

## [0.1.0] — 2026-09-16 (Milestone 1: Problem Framing & Data Acquisition)
### Added
- Automated Kaggle dataset acquisition script using `kagglehub` / `KaggleApi` (`src/data_acquisition.py`).
- Completed exploratory data analysis and generated initial data profile (`docs/data_profile.md`).
- Established the structural proxy notice governing research claims.

