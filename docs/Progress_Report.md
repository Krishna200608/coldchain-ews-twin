# Project Progress & Final Technical Report

**Course:** Managing Corporate Entrepreneurship (B.Tech 7th Semester, 2026)  
**Institution:** Indian Institute of Information Technology, Allahabad (IIITA)  
**Instructor / Supervisor:** Dr. Netranand Pathak  
**Project Topic:** Topic 21 — Digital Twin-Based Early Warning System for Cold Chain Disruption Detection Using Anomaly Detection  
**Student Name:** Krishna Sikheriya  
**Roll Number:** IIT2023139  
**Submission Date:** October 27, 2026  
**Repository:** [https://github.com/Krishna200608/coldchain-ews-twin](https://github.com/Krishna200608/coldchain-ews-twin)  
**Live Deployed Dashboard:** [https://coldchain-ews-twin.streamlit.app/](https://coldchain-ews-twin.streamlit.app/)  

---

## 1. Executive Summary

Cold-chain logistics for pharmaceuticals, biologics, and perishable foods require strict thermal adherence. Existing commercial solutions rely on **static threshold alarms** that fire only after a critical temperature boundary has been breached for a sustained period, by which time cumulative thermal damage is often irreversible. 

This project designs, evaluates, and deploys a **Digital Twin-Integrated Early Warning System (EWS)** that embeds real-time anomaly detection algorithms inside a discrete-event simulation of the cold-chain distribution process. Using 97,606 physical IoT sensor readings as a structural proxy, an unsupervised Isolation Forest and a deep sequential LSTM-Autoencoder were developed, trained, and integrated into a three-stage SimPy digital twin simulation loop (`Source -> Transit -> Destination`).

The project is **100% technically complete**. All models, simulation pipelines, batch-to-live cross-checks, automated test suites, and interactive public dashboard layers have been implemented, verified, and pushed to GitHub.

---

## 2. Research Gap, Objectives, and Core Research Questions

### The Academic Gap
Cold-chain literature predominantly focuses on **post-hoc shelf-life / spoilage prediction** (calculating quality degradation after damage has occurred) or basic static threshold exceedance. Embedding proactive anomaly detection into an event-driven digital twin to provide quantifiable **early warning runway ($\Delta t_{\text{lead}}$)** before irreversibility occurs remains underexplored.

### Project Objectives
1. Develop an event-driven digital twin modeling the asynchronous streaming dynamics of cold-chain transit.
2. Embed classical unsupervised (Isolation Forest) and deep sequential (LSTM-Autoencoder) anomaly detectors into the digital twin loop.
3. Quantify and benchmark detection lead time against traditional static threshold alarms across diverse disruption categories.

### Resolution of Research Questions (At a Glance)

| Research Question | Empirical Findings | Status |
|---|---|---|
| **RQ1: Early-Warning Lead Time**<br>*Can an anomaly model embedded in a digital twin flag disruptions before irreversibility, and how early?* | **Category-Specific Early Warning:**<br>• **Drift Disruptions:** Isolation Forest achieved substantial early warnings of **+64.0 minutes** (`Out`) and **+11.0 minutes** (`In`) before irreversible failure.<br>• **Step Disruptions:** All detectors alarmed concurrently ($0.0$ min lead time); ML provides zero lead-time advantage for sudden spikes.<br>• **Flatlines:** The naive threshold baseline completely missed frozen signals; Isolation Forest detected both variance collapses.<br>• **LSTM Lag:** The LSTM was late by **14.0 minutes** on `out_drift_009` due to gradual error adaptation. | **Resolved** (Table 1) |
| **RQ2: Classical vs. Deep Learning**<br>*How do classical tree ensembles compare against deep sequential autoencoders on irregular telemetry?* | **Precision vs. Recall Trade-off:**<br>• **Isolation Forest:** High sensitivity tripwire (Recall: 80.0% Out, 91.3% In; FPR: 45.6% Out, 27.0% In).<br>• **LSTM-Autoencoder:** Highly conservative and precision-favoring on `In` series (Precision: 13.11%, FPR: 2.85%, AUC-PR: 0.3852), but near-chance on `Out` series (AUC-PR: 0.0049). | **Resolved** (Table 2) |
| **RQ3: Digital Twin Simulation Fidelity**<br>*Does embedding models into a live event loop cause silent divergence from offline batch evaluation?* | **100% Exact Live/Batch Parity:**<br>SimPy 3-stage simulation replayed 97,603 readings in 6.03 s CPU time ($>1.9$M$\times$ real time) with **$0.00 \times 10^0$ s timing discrepancy**. Across 30 injections $\times$ 3 monitors, all 42 applicable test evaluations matched batch results bit-for-bit (0 mismatches), verified via buffer pre-warming (D33). | **Resolved** (`twin_crosscheck_report.csv`) |

---

## 3. Data Strategy and Structural Proxy Notice

- **Dataset Source:** Kaggle `atulanandjha/temperature-readings-iot-devices` (`IOT-temp.csv`, 6.63 MB, 97,606 raw readings).
- **Timeframe:** July 28, 2018 to December 8, 2018 (133 continuous days, 27,920 unique minute timestamps).
- **Sampling Dynamics:** Highly irregular inter-arrival gaps (Mean: 117.82 s, Median: 0.0 s, Std: 5,446.3 s, Coefficient of Variation $\text{CoV} = 46.23$, Maximum outage gap: 11.57 days).
- **Structural Proxy Framing:** In keeping with strict scientific integrity, this dataset is recognized as a generic IoT office installation (`room_id/id = "Room Admin"`), not operational refrigerated fleet cargo. It is used exclusively as a **structural proxy** to evaluate streaming pipelines, irregular sampling, and integration architecture without making unverified food-safety claims (AD Log D5, D6, D10).

---

## 4. Methodology and System Architecture

1. **Ingestion & Causal Preprocessing (`src/preprocessing.py`):**
   - Corrected critical day-first timestamp parsing (`dayfirst=True`, preventing 48.8% silent parse failures).
   - Separated ambient (`Out`, 77,260 rows) and enclosure (`In`, 20,345 rows) streams.
   - Derived causal temporal features (arrival gap $\Delta t_k$, trailing rolling means and standard deviations, verified free of look-ahead leakage in D22).

2. **Controlled Synthetic Anomaly Protocol (`src/anomaly_injection.py`):**
   - Seeded 30 controlled perturbations (`RANDOM_SEED = 42`): 10 Step spikes, 10 Linear drifts, and 10 Frozen flatlines (15 Out / 15 In).
   - Applied a strict chronological 70% Train / 30% Test split (`cutoff_ts = 2018-10-29 11:10:48`).
   - 24 injections fall on the train split (used only for demonstrations); **all formal evaluation is restricted strictly to the 6 out-of-sample test injections** (D26).

3. **Detection Models:**
   - **Fixed Baseline (`src/baseline_and_labels.py`):** Static upper-bound threshold at train-period $\mu + 2.0\sigma$. Irreversibility timestamp ($t_{\text{irr}}$) defined as a sustained 10-minute exceedance.
   - **Isolation Forest (`src/isolation_forest_model.py`):** Classical unsupervised tree partition ensemble fit on train-only data with `contamination='auto'`.
   - **LSTM-Autoencoder (`src/lstm_prep.py`, `colab/lstm_train.ipynb`, `src/lstm_evaluation.py`):** Bivariate sequential reconstruction architecture (window $L=30$, step $S=5$), trained on Google Colab T4 GPU, with causal last-timestep MSE scoring against a train-only $2.0\sigma$ threshold.

4. **SimPy Discrete-Event Digital Twin (`src/digital_twin.py`, `src/twin_monitors.py`):**
   - Three-stage pipeline (`Source -> Transit -> Destination`) driving simulation progress using real inter-arrival gaps.
   - Streaming monitors (`BaselineMonitor`, `IFMonitor`, `LSTMMonitor`) embedded into the Destination sink.
   - Silent buffer pre-warming (D33) primes sliding buffers prior to visible replay windows, guaranteeing zero cold-start latency.

---

## 5. Experimental Results and Performance Benchmark

### Table 1: Early-Warning Lead Time Comparison (Test Split Injections)
$$\Delta t_{\text{lead}} = t_{\text{irreversibility}} - t_{\text{alarm}} \quad (\text{positive = early warning; negative = late})$$

| Injection ID | Series | Fault Type | Baseline Alarm | IF Alarm | LSTM Alarm | Baseline Lead Time | IF Lead Time | LSTM Lead Time |
|---|---|---|---|---|---|---|---|---|
| `out_step_001` | Out | Step | `13:25` | `13:25` | `13:25` | 0.0 min | 0.0 min | 0.0 min |
| `out_drift_009` | Out | Drift | `03:03` | `01:59` | `03:17` | 0.0 min | **+64.0 min** | **-14.0 min (Late)** |
| `out_flatline_012` | Out | Flatline | None | `21:09` | `21:03` | Undefined | Alarm (No Irrev) | Alarm (No Irrev) |
| `out_flatline_013` | Out | Flatline | None | `01:22` | None | Undefined | Alarm (No Irrev) | Missed |
| `in_step_018` | In | Step | `17:14` | `17:14` | `17:14` | 0.0 min | 0.0 min | 0.0 min |
| `in_drift_023` | In | Drift | `08:07` | `07:56` | `08:07` | 0.0 min | **+11.0 min** | 0.0 min |

### Table 2: Point-Wise Classification Metrics (Single Source of Truth, D35)
*Guarded by automated regression assertion:* `assert tp + fn == int(y_true.sum())`

| Metric | IF — Out | LSTM — Out | IF — In | LSTM — In |
|---|---|---|---|---|
| **Test Rows (Valid / Total)** | 13,372 / 13,372 | 13,343 / 13,372 | 3,767 / 3,767 | 3,738 / 3,767 |
| **Excluded (NaN Blind Spot)** | 0 | 29 | 0 | 29 |
| **True Anomaly Rows** | 65 | 65 | 23 | 23 |
| **True Positives (TP)** | 52 | 13 | 21 | 16 |
| **False Positives (FP)** | 6,067 | 2,722 | 1,010 | 106 |
| **True Negatives (TN)** | 7,240 | 10,556 | 2,734 | 3,609 |
| **False Negatives (FN)** | 13 | 52 | 2 | 7 |
| **Precision** | **0.85%** | **0.48%** | **2.04%** | **13.11%** |
| **Recall** | **80.00%** | **20.00%** | **91.30%** | **69.57%** |
| **F1 Score** | **0.0168** | **0.0093** | **0.0398** | **0.2207** |
| **False Positive Rate (FPR)** | **45.59%** | **20.50%** | **26.98%** | **2.85%** |
| **AUC-PR** | **0.0676** | **0.0049** | **0.2371** | **0.3852** |

---

## 6. Technical Deliverables Completed

| Deliverable | Location in Repository | Description | Status |
|---|---|---|---|
| **Pipeline Source Code** | `src/*.py` | Modular scripts for ingestion, preprocessing, injections, ML training, evaluation, and SimPy simulation. | **Complete & Tracked** |
| **Pre-Trained Weights** | `models/lstm_{out,in}.h5` | Trained LSTM-Autoencoder weights exported from Colab GPU. | **Complete & Tracked** |
| **Evaluation Artifacts** | `data/processed/*.json`, `*.csv` | Serialized point-wise metrics, PR curves, and 3-way lead-time benchmarks. | **Complete & Tracked** |
| **Interactive Dashboard** | `dashboard/app.py`, `dashboard/components/` | Modular Streamlit web application with Guided Tour and Free Explore modes. | **Live on Web** |
| **Academic Report** | `docs/Report/Krishna_Sikheriya_ColdChain_Report.pdf` | 12-chapter comprehensive LaTeX technical report formatted to IEEE / Springer standards. | **Complete (2.2 MB)** |
| **Architectural Decision Log** | `docs/AD_LOG.md` | 35 formal entries documenting every architectural pivot, bug fix, and design decision. | **Complete (D1–D35)** |
| **Dataset Submission** | `Krishna_Sikheriya_IIT2023139_Topic21_Dataset.zip` | 1.04 MB packaged archive containing `IOT-temp.csv` and detailed README. | **Ready for Portal** |
| **Regression Test Suite** | `tests/test_d33_prewarm.py` | Automated tests verifying pre-flight checks and buffer pre-warming (passing in 15.58 s). | **Passing** |

---

## 7. Technical Readiness Assessment

**Is the project complete technically?**  
**Yes, 100% complete.** There are zero unfinished code files, broken imports, missing weights, or failing tests. The entire pipeline reproduces from a clean state via standard terminal commands, and the interactive digital twin is deployed and publicly accessible online.

---

## 8. Presentation Readiness

For tomorrow's classroom presentation, the technical findings have been distilled into a crisp, 10-slide presentation deck documented in [`docs/Presentation.md`](Presentation.md), complete with slide structures, bullet points, and spoken cues.
