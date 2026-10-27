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

## Slide 2: Introduction

### Slide Content
- **What is Cold Chain Logistics?**
  - Transportation of temperature-sensitive cargo (vaccines, biologics, perishable foods) requiring unbroken thermal control (e.g., 2°C to 8°C).
- **The High Stakes of Temperature Excursions:**
  - A single excursion causes biochemical degradation, loss of pharmaceutical efficacy, or food spoilage—resulting in billions in economic losses annually.
- **The Traditional Status Quo:**
  - Standard industrial monitoring relies on **static threshold alarms** that trigger only after temperature exceeds a fixed limit for a sustained duration (e.g., >8°C for 10–15 minutes).
- **The Core Flaw (The Post-Hoc Problem):**
  - By the time a static threshold alarm sounds, cumulative thermal exposure has already caused **irreversible spoilage**. Traditional monitoring is fundamentally reactive.

### Spoken Presenter Cue (What to say)
> "In cold-chain logistics, temperature control is non-negotiable—a single temperature excursion can render an entire batch of vaccines or biologics completely useless. The fundamental problem with today's commercial monitoring is that it relies on static threshold alarms. These alarms only go off after temperatures have already breached safe limits for 10 or 15 minutes. By that time, cumulative heat exposure has already caused irreversible damage. It is a fundamentally reactive approach."

---

## Slide 3: Research Gap and Core Objectives

### Slide Content
- **The Academic Research Gap:**
  - Prior cold-chain research focuses almost exclusively on **post-hoc shelf-life / spoilage modeling** (calculating quality loss after an excursion has concluded).
  - Proactive, real-time anomaly detection embedded within an event-driven digital twin to deliver quantifiable **early-warning runway ($\Delta t_{\text{lead}}$)** is underexplored.
- **Proposed Solution:**
  - Develop a digital twin simulation loop embedding unsupervised and sequential deep learning models to catch precursor thermal anomalies before irreversible failure occurs.
- **Core Research Questions:**
  - **RQ1 (Early Warning Runway):** How many minutes of early warning runway ($\Delta t_{\text{lead}} = t_{\text{irr}} - t_{\text{alarm}}$) can embedded machine learning provide?
  - **RQ2 (Model Comparison):** How does classical Isolation Forest compare to deep LSTM-Autoencoders on irregular sensor telemetry?
  - **RQ3 (Simulation Fidelity):** Can a live simulation loop run these detectors without silent divergence from offline batch evaluation?

### Spoken Presenter Cue (What to say)
> "This brings us to our research gap: existing academic literature focuses almost entirely on post-hoc quality decay models—telling you how much damage occurred after the fact. Our objective was to shift from post-hoc damage calculation to real-time early warning. We formulated three core research questions: First, how many minutes of operational runway can an embedded anomaly detector give us before irreversible failure? Second, how does a classical Isolation Forest compare against a deep LSTM-Autoencoder? And third, can a digital twin run these models in live simulation without diverging from offline batch results?"

---

## Slide 4: Relevant Literature Review (Recent Key Papers)

### Slide Content
**Key Recent Benchmark Papers Grounding Our Research (2023–2026):**

1. **Vukšić et al. (2026, *Applied Sciences*):**  
   *Early Anomaly Detection in Maritime Refrigerated Containers Using a Hybrid Digital Twin and Deep Learning.*  
   • Combines reefer digital twin with autoencoders; reports median lead time of **~68 minutes**, independently corroborating our **64-minute** lead time on drift disruptions.
2. **Xie et al. (2025, *PLOS ONE*):**  
   *An Anomaly Detection Scheme for Data Stream in Cold Chain Logistics.*  
   • Implements improved Isolation Forest on cold-chain fleet telemetry; benchmarks tree-based streaming anomaly detection and contextualizes point-wise metrics.
3. **Meng et al. (2024, *Journal of Food Engineering*):**  
   *A Cost-Effective Over-Temperature Alarm System for Cold Chain Delivery.*  
   • Demonstrates box-level digital twin temperature modeling, exemplifying the threshold-alarm paradigm our proactive anomaly-detection system benchmarks against.
4. **Wu et al. (2023, *Journal of Industrial Information Integration*):**  
   *Internet of Everything and Digital Twin Enabled Service Platform for Cold Chain Logistics.*  
   • Establishes architectural precedent for embedding AI models into live digital-twin data pipelines at platform scale.
5. **Defraeye et al. (2023, *Journal of Food Engineering* / *Comput. Electron. Agric.*):**  
   *Digital Twins of Food Cold Chains: Advances, Challenges, and Opportunities.*  
   • Highlights the critical need to transition from post-harvest post-hoc quality assessments to live, event-driven anomaly early warning.

### Spoken Presenter Cue (What to say)
> "Our work is grounded in recent literature from top journals in food engineering and industrial systems. Crucially, Vukšić et al. in 2026 demonstrated a 68-minute lead time using deep learning on maritime reefer containers, which independently corroborates our finding of a 64-minute lead time on drift faults. Furthermore, Xie et al. in 2025 benchmarked Isolation Forest on cold-chain fleets, while Meng et al. in 2024 in the Journal of Food Engineering and Wu et al. in 2023 established the digital twin framework we build upon."

---

## Slide 5: Data Strategy & Structural Proxy Framing

### Slide Content
- **Dataset:** Kaggle `atulanandjha/temperature-readings-iot-devices` (`IOT-temp.csv`, 97,606 readings, 133 days).
- **Realistic Irregularity:** Inter-arrival gaps have a Coefficient of Variation $\text{CoV} = 46.23$ (Mean: 117.8 s, Median: 0 s, Dropouts up to 11.5 days).
- **Dual Streams:** Separated into ambient (`Out`, 77,260 rows) and internal enclosure (`In`, 20,345 rows).
- **Academic Rigor (Structural Proxy Notice):**
  - This is generic IoT telemetry (`Room Admin`), not real reefer truck sensors.
  - We use it strictly as an experimental **structural proxy** to test streaming integration and irregular arrival dynamics without making ungrounded food-safety claims.

### Spoken Presenter Cue (What to say)
> "We used a 97,000-reading real IoT dataset covering over 4 months. In real supply chains, sensor packets arrive irregularly due to network jitter and dropouts—our data reflects this with a high variance coefficient of 46.2. Importantly, we maintain complete academic honesty: we explicitly treat this as a structural proxy for sensor streaming, rather than fabricating claims of live pharmaceutical field testing."

---

## Slide 6: System Architecture & The Digital Twin

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

## Slide 7: Experimental Setup & Anomaly Protocol

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

## Slide 8: Core Result 1 — Early-Warning Lead Times

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

## Slide 9: Core Result 2 — Classification Trade-offs & Simulation Parity

### Slide Content
- **Point-Wise Classification Metrics on Test Split (D35 Data):**
  - **Isolation Forest (High-Recall Tripwire):** Recall 80.0% (`Out`), 91.3% (`In`); FPR 45.6% (`Out`), 27.0% (`In`). Captures anomalies aggressively.
  - **LSTM-Autoencoder (Precision-Favoring Verifier):** On `In` series: 13.11% Precision, 2.85% FPR, 0.3852 AUC-PR. Suppresses false alarms, but exhibits adaptation lag on drift.
  - **Prevalence Context:** With true anomalies representing only ~0.5% of rows, lower absolute F1 scores are mathematically expected under extreme class imbalance.
- **100% Bit-for-Bit Live/Batch Parity:**
  - SimPy digital twin replayed 97,603 readings in 6.03 s CPU time ($>1.9\text{M}\times$ speedup) with **0.00 s virtual clock drift**.
  - Across 30 injections $\times$ 3 monitors, all **42 applicable test evaluations matched bit-for-bit** with offline batch evaluation (0 mismatches).
- **Live Streamlit Cloud Deployment:**
  - Public URL: `https://coldchain-ews-twin.streamlit.app/`
  - Features Guided Tour mode for presentations and Free Explore mode for interactive tuning.

### Spoken Presenter Cue (What to say)
> "Looking at point-wise metrics, we see a classic engineering trade-off: Isolation Forest acts as an aggressive tripwire with high recall over 80–90%, while the LSTM is highly conservative with a 2.85% false-positive rate on enclosure data. Neither detector universally dominates, demonstrating why hybrid architectures are valuable. Crucially, our automated cross-check report achieved a 100% exact match across all 42 comparisons between live SimPy replay and offline batch results, and the entire system is deployed live on Streamlit Cloud."

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
