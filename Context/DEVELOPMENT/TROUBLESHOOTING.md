# Troubleshooting & Common Issues

This guide provides targeted diagnoses and remediation steps for known edge cases, environment setup problems, and runtime exceptions.

---

## 1. Data Ingestion & Preprocessing Issues

### 1.1. Timestamp Parse Failure Producing ~48% `NaT` Rows
- **Symptom:** In `data/processed/out_features.csv` or `in_features.csv`, approximately 47,662 rows show `NaT` (Not-a-Time) in the timestamp column, causing downstream sorting crashes.
- **Root Cause:** Raw timestamps in `IOT-temp.csv` follow the European day-first convention (`DD-MM-YYYY HH:MM`). Standard pandas `pd.to_datetime()` defaults to month-first parsing (`MM-DD-YYYY`) and fails whenever the day integer exceeds 12.
- **Remediation:**
  Ensure `dayfirst=True` is explicitly specified when parsing dates:
  ```python
  df["ts"] = pd.to_datetime(df["noted_date"], dayfirst=True, errors="coerce")
  ```

### 1.2. Kaggle 401 Unauthorized Error
- **Symptom:** Running `python src/data_acquisition.py` fails with:
  `kaggle.rest.ApiException: (401) Reason: Unauthorized`.
- **Root Cause:** The system cannot locate a valid `kaggle.json` token in the active user profile.
- **Remediation:**
  1. Go to [Kaggle Account Settings](https://www.kaggle.com/settings).
  2. Click **"Create New Token"** to download `kaggle.json`.
  3. Move the file to:
     - **Windows:** `C:\Users\<username>\.kaggle\kaggle.json`
     - **Linux / macOS:** `~/.kaggle/kaggle.json`
  4. On Unix, set file permissions: `chmod 600 ~/.kaggle/kaggle.json`.

---

## 2. Dashboard & Model Runtime Issues

### 2.1. D32 Startup Artifact Verification Failure
- **Symptom:** The Streamlit dashboard halts immediately upon launch with a red banner:
  *"Startup Artifact Verification Failed (D32) - The following required model or data artifacts were not found..."*
- **Root Cause:** The dashboard requires pre-generated model weights and audit reports before rendering.
- **Remediation:**
  Generate missing evaluation reports using the frozen pipeline scripts:
  ```bash
  python src/twin_monitors.py
  python src/twin_crosscheck.py
  ```

### 2.2. TensorFlow oneDNN / CUDA Verbosity on Startup
- **Symptom:** Terminal fills with informational logs:
  `2026-11-02 ... This TensorFlow binary is optimized to use available CPU instructions...`
- **Root Cause:** Default TensorFlow C++ logging verbosity on local CPU execution.
- **Remediation:**
  Ensure environment variables are set before importing TensorFlow:
  ```python
  import os
  os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
  os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
  ```

### 2.3. Streamlit `use_container_width` Deprecation Warning
- **Symptom:** Terminal displays deprecation warnings regarding `use_container_width` in button or column layouts.
- **Root Cause:** Streamlit 1.35+ transitioned button layout APIs from `use_container_width=True` to `width="stretch"` or `width="auto"`.
- **Remediation:**
  Update UI component calls in `dashboard/` to use:
  ```python
  st.button("Play", width="stretch")
  ```

---

## 3. Digital Twin Simulation Issues

### 3.1. Out-of-Order Timestamp Tie-Breaking in SimPy Replay
- **Symptom:** During SimPy event generation, the virtual clock jumps unexpectedly or inter-arrival intervals evaluated at the same minute arrive out of sequence.
- **Root Cause:** In the raw dataset, multiple sensor transactions share the exact same minute timestamp. An unstable sort can scramble the causal allocation of `gap_seconds`.
- **Remediation:**
  Always apply stable multi-key sorting:
  ```python
  df = df.sort_values(
      ["ts", "gap_seconds"],
      ascending=[True, False],
      kind="stable"
  ).reset_index(drop=True)
  ```

