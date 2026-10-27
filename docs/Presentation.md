# Presentation Deck: Digital Twin-Based Early Warning System for Cold Chain Disruption Detection

**Topic 21:** Digital Twin-Based Early Warning System for Cold Chain Disruption Detection Using Anomaly Detection  
**Course:** Managing Corporate Entrepreneurship (B.Tech 7th Semester, 2026)  
**Presenter:** Krishna Sikheriya (Roll No: IIT2023139)  
**Supervisor / Instructor:** Dr. Netranand Pathak  
**Institution:** Indian Institute of Information Technology, Allahabad (IIITA)  
**Live Application:** [https://coldchain-ews-twin.streamlit.app/](https://coldchain-ews-twin.streamlit.app/)  
**GitHub Repository:** [https://github.com/Krishna200608/coldchain-ews-twin](https://github.com/Krishna200608/coldchain-ews-twin)  

---

## Slide 1: Title & Project Identity

### Slide Content
- **Project Title:** Digital Twin-Based Early Warning System for Cold Chain Disruption Detection
- **Topic Code:** Topic 21
- **Presenter:** Krishna Sikheriya (IIT2023139) — 7th Sem B.Tech (IT)
- **Course & Department:** Managing Corporate Entrepreneurship, IIIT Allahabad
- **Supervisor:** Dr. Netranand Pathak
- **Deliverables:** Complete Open-Source Repository, Verified SimPy Engine, Live Web App

### Spoken Presenter Cue (What to say)
> "Good morning, Professor and peers. Today I am presenting our project on Topic 21: A Digital Twin-Based Early Warning System for Cold Chain Disruption Detection. We set out to investigate whether embedding streaming machine learning detectors directly inside a digital twin can flag dangerous temperature breaches *before* irreversible spoilage occurs, rather than waiting for reactive alarms after the damage is already done."

---

## Slide 2: The Problem & Research Gap

### Slide Content
- **The Cold-Chain Dilemma:** Vaccines, pharmaceuticals, and fresh produce require strict continuous temperature bands (e.g., 2°C to 8°C). A single excursion destroys cargo value.
- **The Traditional Failure Mode:** Standard industrial systems rely on **static threshold alarms** (e.g., alarm after temperature stays above limit for prolonged minutes).
- **The Post-Hoc Problem:** By the time a static threshold sounds, cumulative thermal exposure has already spoiled the goods.
- **The Research Gap:** Literature focuses heavily on post-hoc spoilage modeling. Embedding real-time anomaly detection into an event-driven digital twin for proactive early warning is underexplored.

### Spoken Presenter Cue (What to say)
> "In cold-chain logistics, waiting for an alarm to breach a fixed temperature ceiling is fundamentally reactive. By the time an operator is notified, the vaccine or cargo has often already suffered irreversible thermal degradation. Our research addresses this gap by asking: can we catch the *precursor symptoms*—like compressor drift or variance loss—before the critical boundary is crossed?"

---

## Slide 3: Research Questions & Core Objectives

### Slide Content
- **Primary Objective:** Build an event-driven digital twin that streams real IoT telemetry and raises early alarms before irreversible failure.
- **RQ1 (Lead Time):** How early (in minutes) can an embedded anomaly detector flag disruptions relative to when spoilage becomes irreversible?
- **RQ2 (Model Comparison):** How does classical unsupervised learning (Isolation Forest) compare against deep sequential learning (LSTM-Autoencoder)?
- **RQ3 (Simulation Fidelity):** Does embedding models in a live simulation loop introduce latency or silent divergence compared to offline batch evaluation?

### Spoken Presenter Cue (What to say)
> "We structured our project around three specific, falsifiable research questions: First, how many minutes of actionable early warning lead time do we actually gain? Second, how does a lightweight, tree-based Isolation Forest compare to a deep sequential LSTM-Autoencoder? And third, can a digital twin run these models live without drifting from offline batch results?"

---

## Slide 4: Data Strategy & Structural Proxy Framing

### Slide Content
- **Dataset:** Kaggle `atulanandjha/temperature-readings-iot-devices` (`IOT-temp.csv`, 97,606 readings, 133 days).
- **Realistic Irregularity:** Inter-arrival gaps have a Coefficient of Variation $\text{CoV} = 46.23$ (Mean: 117.8 s, Median: 0 s, Dropouts up to 11.5 days).
- **Dual Streams:** Separated into ambient (`Out`, 77,260 rows) and internal enclosure (`In`, 20,345 rows).
- **Academic Rigor (Structural Proxy Notice):**
  - This is generic IoT telemetry, not real reefer truck sensors.
  - We use it strictly as an experimental **structural proxy** to test streaming integration and irregular arrival dynamics without making ungrounded food-safety claims.

### Spoken Presenter Cue (What to say)
> "We used a 97,000-reading real IoT dataset covering over 4 months. In real supply chains, sensor packets arrive irregularly due to network jitter and dropouts—our data reflects this with a high variance coefficient of 46.2. Importantly, we maintain complete academic honesty: we explicitly treat this as a structural proxy for sensor streaming, rather than fabricating claims of live pharmaceutical field testing."

---

## Slide 5: System Architecture & The Digital Twin

### Slide Content
- **Ingestion & Feature Engineering:** Causal timestamp parsing (`dayfirst=True`) and trailing rolling features (zero look-ahead leakage).
- **SimPy Discrete-Event Simulation:** 
  - 3-Stage Supply Chain Pipeline: `Source` $\rightarrow$ `Transit` $\rightarrow$ `Destination`.
  - Driven by historical arrival gaps on an event-driven virtual clock.
- **Embedded Streaming Monitors:**
  - `BaselineMonitor` (Static $2\sigma$ upper bound)
  - `IFMonitor` (Classical Isolation Forest)
  - `LSTMMonitor` (Deep LSTM-Autoencoder reconstruction error)
- **Buffer Pre-Warming (D33):** Eliminates cold-start false negatives during windowed replay.

### Spoken Presenter Cue (What to say)
> "Our architecture consists of three stages: data ingestion, machine learning detectors, and an event-driven SimPy digital twin modeling Source, Transit, and Destination. When a telemetry event reaches Destination, our three monitors score it in real time. We implemented silent buffer pre-warming so the rolling buffers have history, eliminating cold-start errors."

---

## Slide 6: Experimental Setup & Anomaly Protocol

### Slide Content
- **Controlled Perturbation Injection (30 Events, Seed 42):**
  - *Step Spikes (10):* Abrupt $+5^\circ\text{C}$ to $+15^\circ\text{C}$ jumps (e.g., door left wide open).
  - *Linear Drifts (10):* Gradual ramp-up (e.g., compressor refrigerant leak).
  - *Sensor Flatlines (10):* Variance collapses to zero (e.g., sensor stiction / freezing).
- **Strict Chronological Split (70% Train / 30% Test):**
  - 24 injections on the train partition (used for training / preview).
  - **All headline claims restricted strictly to the 6 out-of-sample test injections.**
- **Lead Time Metric:** $\Delta t_{\text{lead}} = t_{\text{irreversibility}} - t_{\text{alarm}}$ (where irreversibility = sustained 10-min breach).

### Spoken Presenter Cue (What to say)
> "To test the system rigorously, we injected 30 controlled synthetic disruptions representing real failure modes: abrupt steps, gradual drifts, and flatlines. We enforced a strict chronological 70/30 train/test split. To ensure scientific validity, all our performance benchmarks are evaluated solely on the 6 untouched test-set injections."

---

## Slide 7: Core Result 1 — Early-Warning Lead Times

### Slide Content
**Lead Time on Out-of-Sample Test Injections ($\Delta t = t_{\text{irr}} - t_{\text{alarm}}$):**

| Injection | Type | Baseline Lead Time | Isolation Forest Lead Time | LSTM-Autoencoder Lead Time |
|---|---|---|---|---|
| `out_step_001` | Step | 0.0 min | 0.0 min | 0.0 min |
| `out_drift_009` | Drift | 0.0 min | **+64.0 min (Early Warning)** | **-14.0 min (Late)** |
| `out_flatline_012` | Flatline | Undefined (Missed) | **Alarm (Variance Collapse)** | **Alarm (Variance Collapse)** |
| `out_flatline_013` | Flatline | Undefined (Missed) | **Alarm (Variance Collapse)** | Missed |
| `in_step_018` | Step | 0.0 min | 0.0 min | 0.0 min |
| `in_drift_023` | Drift | 0.0 min | **+11.0 min (Early Warning)** | 0.0 min |

### Key Observations
- **Drift Success:** Isolation Forest provides massive lead time (**+64 min Out**, **+11 min In**).
- **Step Synchrony:** For sudden jumps, all detectors fire at the same minute ($0.0$ min lead time).
- **LSTM Lag:** LSTM was late by 14 minutes on Out drift due to gradual reconstruction adaptation.

### Spoken Presenter Cue (What to say)
> "Here is our primary research finding: On gradual drift disruptions—which represent slow compressor failures—Isolation Forest wins decisively, providing an early warning 64 minutes ahead on Out and 11 minutes ahead on In. On abrupt step breaches, all detectors trigger concurrently at 0 minutes. And for sensor flatlines, the traditional threshold completely fails to fire, while Isolation Forest catches both."

---

## Slide 8: Core Result 2 — Classification Trade-offs

### Slide Content
**Point-Wise Classification Metrics on Test Split (D35 Single Source of Truth):**

- **Isolation Forest:**
  - High Recall: **80.0%** (`Out`), **91.3%** (`In`)
  - Trade-off: High False Positive Rate (**45.6%** `Out`, **27.0%** `In`)
  - Operational Role: Aggressive, high-sensitivity early tripwire.
- **LSTM-Autoencoder:**
  - Precision-Favoring on `In`: **13.11%** Precision, **2.85%** False Positive Rate, **0.3852** AUC-PR
  - Trade-off: Lower recall on `Out` (20.0%, AUC-PR 0.0049)
  - Operational Role: Conservative secondary verifier.
- **Prevalence Context:** With true anomalies representing only ~0.5% of rows, lower absolute F1 scores are mathematically expected under class imbalance, not a model defect.

### Spoken Presenter Cue (What to say)
> "When looking at point-wise metrics, we see a classic engineering trade-off: Isolation Forest acts as an aggressive tripwire with high recall over 80–90%, but at the cost of a higher false-alarm rate. In contrast, the LSTM is highly conservative on the In series with a 2.85% false-positive rate and higher precision. Neither detector universally dominates, showing why hybrid architectures are valuable."

---

## Slide 9: Digital Twin Parity & Live Interactive Dashboard

### Slide Content
- **100% Live / Batch Cross-Check Parity:**
  - SimPy digital twin replayed 97,603 readings in 6.03 seconds of CPU execution.
  - Across 30 injections $\times$ 3 monitors, all **42 applicable test evaluations matched bit-for-bit** with offline batch evaluation (0 mismatches).
- **Live Streamlit Cloud Deployment:**
  - **Public Link:** `https://coldchain-ews-twin.streamlit.app/`
  - **Guided Tour Mode:** 4-step sequence curated for viva demonstrations.
  - **Free Explore Mode:** Interactive inspection of all 30 injections with clear `[TEST]` vs `[TRAIN DEMO]` tagging.
  - **Zero Duplication:** Directly imports verified detection logic from `src/twin_monitors.py`.

### Spoken Presenter Cue (What to say)
> "To prove that embedding these models in a simulation loop doesn't cause silent discrepancies, our automated cross-check report achieved a 100% exact match across all 42 applicable comparisons. Furthermore, the entire system is deployed live on Streamlit Cloud, featuring an interactive Guided Tour designed specifically for viva examination walkthroughs."

---

## Slide 10: Conclusion & Corporate Entrepreneurship Relevance

### Slide Content
- **Technical Summary:**
  - 100% complete and verified pipeline (Scaffolding $\rightarrow$ ML $\rightarrow$ Digital Twin $\rightarrow$ Cloud UI).
  - Proven early warning (+64 min lead time on gradual drift).
  - Zero silent divergence between live simulation and batch metrics.
- **Managing Corporate Entrepreneurship Takeaways:**
  - *Evidence-First Risk Management:* Honest reporting of trade-offs (highlighting where the LSTM lagged rather than fabricating artificial 99% accuracy).
  - *Audit Discipline:* Maintained an append-only Architectural Decision log of 35 formal entries (D1–D35) catching real bugs during development.
  - *Technology Adoption:* Proved that classical ML can outperform complex deep learning on specific edge telemetry tasks.

### Spoken Presenter Cue (What to say)
> "To conclude: this project bridges machine learning, discrete-event digital twins, and disciplined corporate entrepreneurship. We did not cherry-pick our data or claim artificial perfection—we demonstrated exactly where classical ML provides real operational runway, where deep learning lags, and how an organization can rigorously evaluate technology under uncertainty. Thank you, and I look forward to your questions."
