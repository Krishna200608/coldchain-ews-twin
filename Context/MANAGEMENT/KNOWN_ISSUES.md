# Known Issues & Technical Inconsistencies

This document catalogs known documentation discrepancies, numbering anomalies, and technical constraints identified across the codebase and historical reports.

---

## 1. Documentation Discrepancies & Resolutions

### 1.1. `AD_LOG.md` Heading Numbering Gap
- **Discrepancy:** In [`docs/AD_LOG.md`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/docs/AD_LOG.md), markdown section headings transition directly from `## 2026-09-18 — D19` to `## 2026-09-19 — D23`. Headings for **D20**, **D21**, and **D22** are absent.
- **Root Cause & Resolution:** Decisions D20 (Destination logging process), D21 (Milestone 5b cross-check verification audit), and D22 (recomputing trailing rolling statistics from `temp_injected`) were implemented and referenced extensively in source code docstrings and commit notes, but their explicit heading anchors were skipped during markdown drafting.
- **Authoritative Resolution:** All three decisions are formally reinstated and detailed in [`Context/MANAGEMENT/ARCHITECTURAL_DECISIONS.md`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/Context/MANAGEMENT/ARCHITECTURAL_DECISIONS.md).

### 1.2. Anomaly Injection Durations (Code vs. Early README Draft)
- **Discrepancy:** Early README text stated that synthetic anomalies had variable duration ranges depending on typology (e.g., 10–50 readings for step, 30–120 readings for drift, 20–80 readings for flatline).
- **Authoritative Resolution:** The actual implemented and frozen source code in [`src/anomaly_injection.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/anomaly_injection.py) explicitly enforces:
  ```python
  DUR_MIN: int = 5
  DUR_MAX: int = 30
  ```
  All 30 synthetic injections were sampled with $D \in [5, 30]$ readings. The source code constants represent ground truth.

### 1.3. LSTM-Autoencoder Hidden Units (Code vs. LaTeX Progress Report)
- **Discrepancy:** A TikZ schematic diagram in [`docs/Progress_Report/main.tex`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/docs/Progress_Report/main.tex) labels the encoder and decoder LSTM layers with "64 hidden units".
- **Authoritative Resolution:** The training notebook [`colab/lstm_train.ipynb`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/colab/lstm_train.ipynb), runtime monitor [`src/twin_monitors.py`](file:///d:/Lab/Managing%20Corporate%20Entrepreneurship/coldchain-ews-twin/src/twin_monitors.py), and saved weights (`models/lstm_*.h5`) define the layers with **32 hidden units** (`LSTM(32)`). The serialized models and code are authoritative.

---

## 2. Technical Limitations & Algorithmic Constraints

### 2.1. Isolation Forest False Positive Burden
- **Issue:** Point-wise false positive rate on the outdoor series (`Out`) is 45.59%, yielding a point-wise precision of 0.85%.
- **Context:** An expected theoretical property of applying scikit-learn's default `contamination='auto'` against extreme class imbalance ($\approx 0.5\%$ injected anomalies).
- **Mitigation:** Operators must evaluate early-warning lead times on disruption events rather than treating individual point flags as isolated physical alarms.

### 2.2. LSTM Initial Causal Blind Spot
- **Issue:** The LSTM-Autoencoder cannot score the first 29 observations of an isolated stream.
- **Context:** Strict adherence to causal single-window-per-row scoring ($L = 30$) prohibits forward lookahead or cross-region context.
- **Mitigation:** The **D33 Pre-Warming Protocol** primes monitor buffers with 30 preceding historical observations before replaying localized windows.

