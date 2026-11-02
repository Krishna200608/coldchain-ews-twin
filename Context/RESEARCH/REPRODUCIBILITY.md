# Reproducibility Protocol & Verification

This document specifies the exact environment specifications, deterministic random seeds, execution sequence, and expected artifact checksums required to replicate all empirical results.

---

## 1. Deterministic Execution Invariants

All stochastic and pseudo-random operations in the pipeline are governed by fixed seeds:

| Subsystem | Seed Constant | Target Scope |
| :--- | :--- | :--- |
| **Synthetic Anomaly Injection** | `RANDOM_SEED = 42` | Sampling start indices, durations, magnitudes in `src/anomaly_injection.py` |
| **Isolation Forest Partitioning**| `IF_RANDOM_STATE = 42` | Random split features and thresholds in `sklearn.ensemble.IsolationForest` |
| **LSTM Weight Initialization** | `PYTHONHASHSEED = 0`, `tf.random.set_seed(42)` | Random weight matrices and dropout masks in TensorFlow/Keras |
| **SimPy Event Ordering** | Stable sort on `['ts', 'gap_seconds']` | Deterministic tie-breaking for readings sharing identical timestamps |

---

## 2. Environment Specifications

- **Python Version:** 3.11.x (strictly required for package compatibility).
- **Core Library Dependencies:**
  - `pandas >= 2.1.0`
  - `numpy >= 1.24.0`
  - `scikit-learn >= 1.4.0`
  - `tensorflow >= 2.15.0`
  - `simpy >= 4.1.0`
  - `altair >= 5.2.0`
  - `streamlit >= 1.32.0`

---

## 3. End-to-End Pipeline Reproduction Sequence

Executing the following sequential commands from the repository root reproduces the entire experimental pipeline from scratch:

```bash
# 1. Acquire raw data (requires ~/.kaggle/kaggle.json)
python src/data_acquisition.py

# 2. Preprocess, deduplicate, and engineer features (M2)
python src/preprocessing.py

# 3. Inject synthetic step, drift, and flatline anomalies (M2)
python src/anomaly_injection.py

# 4. Compute clean baseline thresholds and evaluate irreversibility (M2)
python src/baseline_and_labels.py

# 5. Train Isolation Forest and evaluate point-wise & lead-time metrics (M3)
python src/isolation_forest_model.py
python src/if_evaluation.py

# 6. Prepare LSTM windows and evaluate on pre-trained weights (M4a/M4b)
python src/lstm_prep.py
python src/lstm_evaluation.py

# 7. Compile master three-way comparison scorecard
python src/three_way_comparison.py

# 8. Execute streaming digital twin monitors and cross-check audit (M5a/M5b)
python src/twin_monitors.py
python src/twin_crosscheck.py

# 9. Run automated regression unit tests
python -m unittest tests/test_d33_prewarm.py
```

---

## 4. Verification Checksums & Ground-Truth Invariants

Following execution, verify that generated artifacts match the following ground-truth properties:

| File Artifact Path | Expected Row Count | Ground-Truth Invariant |
| :--- | :--- | :--- |
| `data/processed/out_features.csv` | 77,299 | `is_injected_anomaly` column **must not exist** |
| `data/processed/in_features.csv` | 20,306 | `is_injected_anomaly` column **must not exist** |
| `data/processed/injection_log.csv` | 30 | Exactly 5 step, 5 drift, 5 flatline per series |
| `data/processed/injection_train_test_status.csv` | 30 | Exactly 24 train and 6 test injections |
| `data/processed/three_way_comparison.csv` | 30 | `out_drift_009` IF lead time must equal **64.0 min** |
| `data/processed/twin_crosscheck_report.csv` | 90 | Exactly **42 True, 48 not_applicable, 0 False** |

