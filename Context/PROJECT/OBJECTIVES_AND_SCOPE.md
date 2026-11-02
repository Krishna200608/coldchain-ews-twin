# Objectives and Scope

> **Single Source of Truth:** `Context/PROJECT/OBJECTIVES_AND_SCOPE.md`  
> **Related Documents:**  
> - [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md)  
> - [`PROBLEM_STATEMENT.md`](PROBLEM_STATEMENT.md)  
> - [`RESEARCH_CONTRIBUTIONS.md`](RESEARCH_CONTRIBUTIONS.md)  
> - [`../RESEARCH/METHODOLOGY.md`](../RESEARCH/METHODOLOGY.md)  
> - [`../RESEARCH/LIMITATIONS.md`](../RESEARCH/LIMITATIONS.md)

---

## 1. Core Engineering Objectives

The project is structured around four foundational engineering objectives:

1. **Causal Digital Twin Architecture:** Build a 3-stage discrete-event simulation engine in Python using `SimPy` (`Source` $\rightarrow$ `Transit` $\rightarrow$ `Destination`) that models asynchronous, irregular IoT telemetry arrival dynamics without resampling or synthetic interpolation (D1, D17, D18).
2. **Embedded Model Comparison:** Embed both a classical unsupervised tree ensemble (**Isolation Forest**) and a deep sequence reconstruction neural network (**LSTM-Autoencoder**) into the destination sink of the digital twin to run real-time inference on streaming telemetry (D7, D12, D27).
3. **Empirical Lead-Time Quantification:** Formally quantify the operational early-warning runway:
   $$\Delta t_{\text{lead}} = t_{\text{irreversibility}} - t_{\text{alarm}}$$
   across three canonical disruption failure modes (step spikes, linear drifts, and sensor flatlines) relative to a static naive threshold baseline (D4, D8).
4. **Simulation Parity Verification:** Empirically prove that live streaming evaluation inside the digital twin loop reproduces offline batch evaluation bit-for-bit (zero mismatches), completely eliminating cold-start artifacts through silent buffer pre-warming (D23, D33).

---

## 2. The Three Research Questions

The empirical investigation is guided by three specific research questions:

### RQ1: Early-Warning Lead Time Runway
> *Can an anomaly detection model embedded in a digital twin flag disruptions before thermal failure becomes irreversible, and how early?*

* **Hypothesis:** Multi-feature anomaly detectors sensitive to variance and rolling trajectory will detect subtle degradation slopes (e.g., compressor leaks) substantially earlier than static upper-bound limits.
* **Resolution:** **Confirmed for Drift.** Isolation Forest delivers **+64.0 minutes** of advance warning on ambient drift (`out_drift_009`) and **+11.0 minutes** on enclosure drift (`in_drift_023`). For step spikes, models trigger synchronously at $0.0\text{ min}$ (no ML advantage for acute breaches). For flatlines, threshold alarms fail completely, while Isolation Forest catches both test-set stiction events.

### RQ2: Classical vs. Deep Learning Trade-Offs
> *How do classical tree-based ensembles (Isolation Forest) compare against deep sequential autoencoders (LSTM) on highly irregular sensor telemetry?*

* **Hypothesis:** Deep recurrent neural networks will outperform classical tree models by learning temporal dependencies and autocorrelation across consecutive timestamps.
* **Resolution:** **Nuanced / Rejected on Edge Drift.** Isolation Forest outperformed the LSTM on edge drift early-warning runway (+64 min vs. -14 min). The LSTM suffered from temporal memory inertia: because the drift was linear and gradual, the recurrent cells partially adapted to the error, delaying alarm generation until after irreversibility. However, on clean enclosure data (`In`), the LSTM demonstrated exceptional precision ($13.11\%$) and suppressed false alarms ($\text{FPR} = 2.85\%$), establishing its role as a conservative secondary verifier.

### RQ3: Digital Twin Simulation Fidelity
> *Does embedding machine-learning anomaly detectors into an event-driven discrete simulation loop introduce silent divergence, clock drift, or state lag compared to batch evaluation?*

* **Hypothesis:** Online continuous state accumulation in streaming deques can match offline vector evaluation if memory buffers are properly managed.
* **Resolution:** **Confirmed with 100% Bit-for-Bit Parity.** The SimPy twin replayed 97,603 readings in 6.03 seconds of CPU time ($>1.9\text{ million}\times$ speedup) with exactly $0.00\text{ s}$ of virtual clock drift. Across 30 injections $\times$ 3 monitors, all **42 applicable evaluations matched offline batch outputs identically (0 mismatches)**, guaranteed via buffer pre-warming (D33).

---

## 3. Scope Boundaries: What Is Included

The project scope encompasses a complete, production-grade deliverable portfolio:

| Scope Component | Implementation Details |
| :--- | :--- |
| **Data Acquisition** | Authenticated Kaggle API client (`src/data_acquisition.py`) downloading `IOT-temp.csv` (97,606 raw rows). |
| **Causal Preprocessing** | Deduplication, day-first timestamp parsing, independent series splitting (`Out`: 77,260 rows, `In`: 20,345 rows), within-series `gap_seconds`, and count-based rolling features (`src/preprocessing.py`). |
| **Synthetic Anomaly Protocol** | Controlled injection of 30 synthetic perturbations (10 step spikes, 10 linear drifts, 10 sensor flatlines) under `RANDOM_SEED = 42` (`src/anomaly_injection.py`). |
| **Chronological Partitioning** | 70% Train / 30% Test split at `cutoff_ts = 2018-10-29 11:10:48`, strictly reserving the 6 test-side injections for out-of-sample claims (`src/split_utils.py`). |
| **Model Implementations** | Naive $2\sigma$ baseline (`src/baseline_and_labels.py`), scikit-learn Isolation Forest (`src/isolation_forest_model.py`), and Keras bivariate LSTM-Autoencoder (`colab/lstm_train.ipynb`, `src/lstm_evaluation.py`). |
| **Digital Twin Simulation** | SimPy 3-stage data pipeline with virtual clock advancement (`src/digital_twin.py`, `src/twin_monitors.py`). |
| **Verification & Auditing** | Automated cross-check audit table (`src/twin_crosscheck.py`) and pre-warming unit tests (`tests/test_d33_prewarm.py`). |
| **Presentation Layer** | Multi-mode Streamlit dashboard with Guided Tour, Free Explore, and Altair interactive telemetry visualization (`dashboard/app.py`). |
| **Academic Documentation** | Complete 12-chapter IEEE LaTeX report (`docs/Report/`), Progress Report (`docs/Progress_Report/`), and Architectural Decision Log (`docs/AD_LOG.md`). |

---

## 4. Explicit Non-Goals & Out-of-Scope Items

To preserve methodological rigor and prevent scope creep, the following areas are **explicitly out of scope**:

1. **No Physical Thermodynamic CFD Modeling:** The project does not model Computational Fluid Dynamics (CFD), heat transfer coefficients ($U$-values), or compressor thermodynamic phase changes. The digital twin models a **telemetry data pipeline**, not container thermodynamics (D17).
2. **No Proprietary Clinical Claims:** All telemetry derives from an administrative office proxy dataset (`"Room Admin"`). The project makes no claims regarding actual pharmaceutical shelf-life or FDA 21 CFR Part 11 regulatory compliance (D31).
3. **No Geographic Spatial Routing:** The dataset lacks GPS coordinates, route maps, or transit stops. The 3-stage pipeline (`Source` $\rightarrow$ `Transit` $\rightarrow$ `Destination`) represents data transmission and processing stages, not physical locations (D17).
4. **No Automated Actuator Control / Closed-Loop Feedback:** The EWS produces alarms and decision support for human dispatchers; it does not issue automated control signals to adjust container refrigeration compressors or backup diesel generators.
5. **No Test-Set Threshold Tuning:** The decision threshold for Isolation Forest is frozen at `contamination='auto'`, and the LSTM threshold is fixed at train-period $\mu + 2\sigma$. Tuning thresholds against ground-truth test labels was strictly prohibited to prevent data leakage (D7, D13).

