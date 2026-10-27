# Presentation Deck: Digital Twin-Based Early Warning System for Cold Chain Disruption Detection

**Topic 21:** Digital Twin-Based Early Warning System for Cold Chain Disruption Detection Using Anomaly Detection  
**Course:** Managing Corporate Entrepreneurship (B.Tech 7th Semester, 2026)  
**Presenter:** Krishna Sikheriya (Roll No: IIT2023139)  
**Supervisor / Instructor:** Dr. Netranand Pathak  
**Institution:** Indian Institute of Information Technology, Allahabad (IIITA)  
**Live Application:** [https://coldchain-ews-twin.streamlit.app/](https://coldchain-ews-twin.streamlit.app/)  
**GitHub Repository:** [https://github.com/Krishna200608/coldchain-ews-twin](https://github.com/Krishna200608/coldchain-ews-twin)  

> **How to use this file in Canva:**  
> Each slide is broken down into exact text boxes and visual containers. You can copy each text block directly into your Canva text elements without needing to clean up asterisks or LaTeX code.

---

## Slide 1: Title & Project Identity

### Recommended Canva Layout
- **Style:** Deep Navy Background (`#0E264D`) with clean white/cyan typography.
- **Top Image:** Drag and drop `figures/iiit_allahabad_logo.png` centered at the top.
- **Center:** Main Title & Subtitle.
- **Bottom:** Metadata block & 3 pill badges.

### Text Box 1: Slide Title (Large, 36–40 pt, Bold White)
```text
Digital Twin-Based Early Warning System for Cold Chain Disruption Detection
```

### Text Box 2: Subtitle (18–20 pt, Light Cyan #BAE6FD)
```text
Embedding Anomaly Detection Inside a Discrete-Event Simulation Loop (Topic 21)
```

### Text Box 3: Presenter & Course Metadata (13–14 pt, Off-White #E2E8F0)
```text
Presenter: Krishna Sikheriya (Roll No: IIT2023139) — 7th Semester B.Tech (IT)
Course: Managing Corporate Entrepreneurship | Instructor: Dr. Netranand Pathak
Department of Information Technology, Indian Institute of Information Technology, Allahabad (IIITA)
```

### Text Box 4: Project Links / Badges (10–11 pt)
```text
Live Web App: coldchain-ews-twin.streamlit.app   |   GitHub: github.com/Krishna200608/coldchain-ews-twin
```

### Spoken Presenter Cue (What to say)
> "Good morning, Professor and peers. Today I am presenting our project on Topic 21: A Digital Twin-Based Early Warning System for Cold Chain Disruption Detection. We set out to investigate whether embedding streaming machine learning detectors directly inside a digital twin can flag dangerous temperature breaches *before* irreversible spoilage occurs, rather than waiting for reactive alarms after the damage is already done."

---

## Slide 2: Introduction

### Recommended Canva Layout
- **Style:** 2-Card Horizontal Split (Left Card: The Cold Chain Reality | Right Card: The Status Quo Failure).
- **Icons to search in Canva:** `refrigerated truck`, `temperature sensor`, `alarm bell`.

### Top Header Bar
```text
Topic 21: Cold Chain EWS Twin | Introduction: The Cold-Chain Reality
```

### Card 1 (Left Box): The Logistics Problem
- **Card 1 Title:**
```text
The Cold Chain Reality & High Stakes
```
- **Card 1 Content (Copy directly):**
```text
• Strict Thermal Bounds: Cold-chain cargo (vaccines, biologics, perishable foods) demands strict, unbroken temperature control (e.g., 2°C to 8°C).
• High Economic Impact: A single temperature excursion compromises drug potency or causes food spoilage, generating billions in economic losses annually.
• Public Health Risk: Spoiled biologicals risk patient safety and cause massive pharmaceutical recalls.
```

### Card 2 (Right Box): The Status Quo Failure
- **Card 2 Title:**
```text
The Traditional Failure Mode: Static Alarms
```
- **Card 2 Content (Copy directly):**
```text
• Status Quo: Commercial supply chains rely on static threshold alarms (e.g., alert only if temperature exceeds 8°C for >10–15 minutes).
• The Post-Hoc Flaw: Alarms only sound after the thermal excursion has already occurred.
• Irreversible Damage: By the time an operator is notified, cumulative heat exposure has already caused irreversible biochemical degradation. Traditional monitoring is fundamentally reactive.
```

### Bottom Callout Banner (Red Highlight Box)
```text
The Core Flaw: Waiting for a threshold breach is fundamentally reactive—by the time alarms sound, the damage is already irreversible!
```

### Spoken Presenter Cue (What to say)
> "In cold-chain logistics, temperature control is non-negotiable—a single excursion can render an entire batch of vaccines or biologics completely useless. The fundamental problem with today's commercial monitoring is that it relies on static threshold alarms. These alarms only go off after temperatures have already breached safe limits for 10 or 15 minutes. By that time, cumulative heat exposure has already caused irreversible damage. It is a fundamentally reactive approach."

---

## Slide 3: Research Gap and Core Objectives

### Recommended Canva Layout
- **Style:** Left Column (The Academic Gap + Core Solution) | Right Column (3 Stacked Research Question Cards).
- **Icons to search in Canva:** `document search`, `stopwatch`, `neural network`, `sync loop`.

### Top Header Bar
```text
Topic 21: Cold Chain EWS Twin | Research Gap & Core Objectives
```

### Card 1 (Left Box): The Literature Gap & Proposed Solution
- **Card 1 Title:**
```text
The Academic Gap & Proposed Solution
```
- **Card 1 Content (Copy directly):**
```text
• Prior Literature Focus: Academic research focuses almost exclusively on post-hoc shelf-life calculation (modeling Arrhenius degradation after the excursion has completed).
• The Underexplored Gap: Proactive, real-time anomaly detection embedded within an event-driven digital twin to deliver quantifiable early warning is underexplored.
• Proposed Solution: Embed streaming anomaly detectors (Isolation Forest & LSTM-Autoencoder) inside a discrete-event SimPy digital twin to catch precursor symptoms before irreversible failure.
```

### Card 2 (Right Top): Research Question 1
- **Title:** `RQ1: Early Warning Runway (Lead Time)`
- **Content:**
```text
How many minutes of actionable early warning (Δt_lead = t_irreversibility - t_alarm) can machine learning deliver relative to when spoilage becomes irreversible?
```

### Card 3 (Right Middle): Research Question 2
- **Title:** `RQ2: Classical vs. Deep Learning Trade-Offs`
- **Content:**
```text
How does a classical tree ensemble (Isolation Forest) compare against a deep sequence autoencoder (LSTM-Autoencoder) on highly irregular sensor telemetry?
```

### Card 4 (Right Bottom): Research Question 3
- **Title:** `RQ3: Digital Twin Simulation Fidelity`
- **Content:**
```text
Can an event-driven digital twin simulation loop run these detectors in real time without silent divergence or cold-start lag compared to offline batch evaluation?
```

### Spoken Presenter Cue (What to say)
> "This brings us to our research gap: existing academic literature focuses almost entirely on post-hoc quality decay models—telling you how much damage occurred after the fact. Our objective was to shift from post-hoc damage calculation to real-time early warning. We formulated three core research questions: First, how many minutes of operational runway can an embedded anomaly detector give us before irreversible failure? Second, how does a classical Isolation Forest compare against a deep LSTM-Autoencoder? And third, can a digital twin run these models in live simulation without diverging from offline batch results?"

---

## Slide 4: Relevant Literature Review (Recent Key Papers)

### Recommended Canva Layout
- **Style:** Clean 5-Row Comparison Table (or 5 Structured Cards).
- **Header Row:** Navy Blue (`#0E264D`) with White Text.

### Top Header Bar
```text
Theoretical Foundations | Relevant Literature Review (Recent Papers 2023–2026)
```

### Table Content (Copy cell by cell into Canva Table)

| Paper Citation | Publication Venue | Core Contribution | Direct Relevance to Topic 21 |
|---|---|---|---|
| **Vukšić et al. (2026)** | Applied Sciences (MDPI) | Hybrid physics-based digital twin + autoencoder for reefer maritime containers. | Reports median lead time of ~68 minutes; independently corroborates our 64-minute drift early warning. |
| **Xie et al. (2025)** | PLOS ONE | Improved Isolation Forest (subsampling + feature grouping) for cold-chain fleet streams. | Primary tree-ensemble streaming benchmark; contextualizes point-wise F1 metrics under high anomaly rarity. |
| **Meng et al. (2024)** | Journal of Food Engineering (Elsevier) | Box-level digital twin temperature model + static over-temperature alarms. | Exemplifies the static threshold alarm baseline that our proactive anomaly-detection system benchmarks against. |
| **Wu et al. (2023)** | J. Industrial Information Integration (Elsevier) | Internet-of-Everything and Digital-Twin platform for cold-chain service logistics. | Establishes architectural precedent for embedding AI inference into operational digital-twin pipelines. |
| **Defraeye et al. (2023)** | Comput. Electron. Agric. / J. Food Eng. | Comprehensive review of food cold-chain digital twins and sensor dynamics. | Identifies fundamental research gap: shifting from reactive quality loss to live event-driven early warning. |

### Bottom Key Takeaway Badge (Green Highlight)
```text
Corroborated Lead Time: Vukšić et al. (2026) report ~68 min lead time on reefer containers, independently validating our 64-minute early warning!
```

### Spoken Presenter Cue (What to say)
> "Our work is grounded in recent literature from top journals in food engineering and industrial systems. Crucially, Vukšić et al. in 2026 demonstrated a 68-minute lead time using deep learning on maritime reefer containers, which independently corroborates our finding of a 64-minute lead time on drift faults. Furthermore, Xie et al. in 2025 benchmarked Isolation Forest on cold-chain fleets, while Meng et al. in 2024 in the Journal of Food Engineering and Wu et al. in 2023 established the digital twin framework we build upon."

---

## Slide 5: Data Strategy & Structural Proxy Framing

### Recommended Canva Layout
- **Style:** Left Column (Telemetry Dynamics + Rigor Notice) | Right Column (Two Stacked Plots).
- **Image 1 (Right Top):** Drag and drop `figures/fig_temperature_distribution.png`.
- **Image 2 (Right Bottom):** Drag and drop `figures/fig_sampling_intervals_corrected.png`.

### Top Header Bar
```text
Experimental Setup | Data Strategy & Structural Proxy Framing
```

### Left Column: Telemetry Dynamics
- **Card Title:**
```text
Empirical Telemetry Properties & Rigor
```
- **Card Content (Copy directly):**
```text
• Kaggle IoT Telemetry: 97,606 raw sensor readings across 133 continuous days (July 28 to Dec 8, 2018), 27,920 unique minute timestamps.
• Extreme Arrival Irregularity: Mean arrival gap = 117.8 s, Median = 0.0 s, Std = 5,446.3 s, Coefficient of Variation CoV = 46.23. Transmission dropouts reach up to 11.57 days, accurately reflecting edge network jitter.
• Dual Streams: Separated into ambient (Out, 77,260 rows) and internal enclosure proxy (In, 20,345 rows).
```

### Left Column Bottom: Scientific Rigor Notice (Amber Box #FFFBEB, Border #D97706)
- **Notice Title:**
```text
Academic Integrity: Structural Proxy Notice
```
- **Notice Content (Copy directly):**
```text
Originates from an office installation ('Room Admin'), not live pharmaceutical reefer vehicles. Framed strictly as an experimental structural proxy to evaluate irregular streaming pipelines and buffer mechanics without making unverified food-safety claims.
```

### Spoken Presenter Cue (What to say)
> "We used a 97,000-reading real IoT dataset covering over 4 months. In real supply chains, sensor packets arrive irregularly due to network jitter and dropouts—our data reflects this with a high variance coefficient of 46.2. Importantly, we maintain complete academic honesty: we explicitly treat this as a structural proxy for sensor streaming, rather than fabricating claims of live pharmaceutical field testing."

---

## Slide 6: System Architecture & The Digital Twin

### Recommended Canva Layout
- **Style:** Left Column (Simulation Features) | Right Column (Vertical Process Flow).
- **Process Flow:** 5 stacked colored cards connected by downward arrows (`↓`).

### Top Header Bar
```text
System Architecture | SimPy Discrete-Event Digital Twin
```

### Left Column: Architecture Overview
- **Card Title:**
```text
Discrete-Event Simulation Architecture
```
- **Card Content (Copy directly):**
```text
• Causal Ingestion: Day-first parsing (dayfirst=True, preventing 48.8% silent parse failures). Derived trailing rolling statistics with zero look-ahead leakage (D22).
• SimPy 3-Stage Transit: Models physical progression: Source -> Transit -> Destination driven by real historical inter-arrival gaps.
• Embedded Streaming Monitors:
  - BaselineMonitor: Static 2-sigma threshold (47.7°C Out, 34.9°C In).
  - IFMonitor: Classical Isolation Forest tree partition score.
  - LSTMMonitor: Deep sequence reconstruction MSE.
• Silent Buffer Pre-Warming (D33): Sliding window buffers are silently primed with preceding history before visible playback, eliminating cold-start false alarms.
```

### Right Column: 5 Flowchart Steps (Copy for each card)
- **Card 1 (Navy #0E264D, White text):**
```text
1. Raw Physical Stream (97,606 IoT sensor readings)
```
- **Card 2 (Light Blue #F0F7FF, Border #0284C7):**
```text
2. Causal Ingestion & Feature Engineering (dayfirst=True, Δt_k, trailing rolling statistics)
```
- **Card 3 (Teal #F0FDFA, Border #0D9488):**
```text
3. SimPy Discrete-Event Digital Twin (Source -> Transit -> Destination virtual clock)
```
- **Card 4 (Light Gray #F8FAFC, Border #CBD5E1):**
```text
4. Destination Sink: Baseline (2σ) | Isolation Forest | LSTM-Autoencoder
```
- **Card 5 (Cyan #E0F2FE, Border #0284C7):**
```text
5. Live Verification Engine (D33 Buffer Pre-Warming) & Streamlit Cloud Dashboard
```

### Spoken Presenter Cue (What to say)
> "Our architecture consists of three stages: data ingestion, machine learning detectors, and an event-driven SimPy digital twin modeling Source, Transit, and Destination. When a telemetry event reaches Destination, our three monitors score it in real time. We implemented silent buffer pre-warming so the rolling buffers have history, eliminating cold-start errors."

---

## Slide 7: Experimental Setup & Anomaly Protocol

### Recommended Canva Layout
- **Style:** Left Column (Perturbation Protocol + Split Discipline) | Right Column (Injection Examples Image).
- **Right Image:** Drag and drop `figures/fig_injection_examples.png`.

### Top Header Bar
```text
Experimental Setup | Controlled Anomaly Protocol & Split Discipline
```

### Left Column: Anomaly Injection Protocol
- **Card Title:**
```text
Controlled Perturbation Protocol (Seed 42)
```
- **Card Content (Copy directly):**
```text
• 30 Controlled Synthetic Injections (15 Out / 15 In) representing 3 real failure modes:
  - Step Spikes (10): Abrupt +5°C to +15°C sudden jumps (container door left wide open).
  - Linear Drifts (10): Gradual ramps of +0.05°C to +0.25°C/min (compressor refrigerant leak).
  - Sensor Flatlines (10): Zero variance persistence (frozen ADC sensor / mechanical stiction).
• Strict Chronological Split: 70% Train / 30% Test split (Cutoff: 2018-10-29 11:10:48).
• Out-of-Sample Discipline: 24 injections fall on train split (used only for development/previews). All formal headline claims are evaluated strictly on the 6 untouched test injections.
```

### Left Column Bottom: Formula Box (Blue Fill #F0F7FF, Border #0284C7)
- **Formula:**
```text
Lead Time Metric: Δt_lead = t_irreversibility - t_alarm
(Where t_irr is a sustained 10-minute breach. Positive = Early Warning; Negative = Late Alarm)
```

### Spoken Presenter Cue (What to say)
> "To test the system rigorously, we injected 30 controlled synthetic disruptions representing real failure modes: abrupt steps, gradual drifts, and flatlines. We enforced a strict chronological 70/30 train/test split. To ensure scientific validity, all our performance benchmarks are evaluated solely on the 6 untouched test-set injections."

---

## Slide 8: Core Result 1 — Early-Warning Lead Times

### Recommended Canva Layout
- **Style:** Left Column (Complete Benchmark Table) | Right Column (Lead Time Bar Chart).
- **Right Image:** Drag and drop `figures/fig_m4b_three_way_lead_times.png`.

### Top Header Bar
```text
Core Findings | Lead-Time Benchmark on Out-of-Sample Test Injections
```

### Table Content (Copy cell by cell into Canva Table)

| Injection ID | Fault Type | Baseline Alarm | Isolation Forest Lead Time | LSTM-Autoencoder Lead Time |
|---|---|---|---|---|
| `out_step_001` | Step | 0.0 min | 0.0 min | 0.0 min |
| `out_drift_009` | Drift | 0.0 min | **+64.0 min (Early Warning)** | **-14.0 min (Late)** |
| `out_flatline_012` | Flatline | Undefined (Missed) | **Detected (Variance Collapse)** | **Detected (Variance Collapse)** |
| `out_flatline_013` | Flatline | Undefined (Missed) | **Detected (Variance Collapse)** | Missed |
| `in_step_018` | Step | 0.0 min | 0.0 min | 0.0 min |
| `in_drift_023` | Drift | 0.0 min | **+11.0 min (Early Warning)** | 0.0 min |

*(Tip: In Canva, color `+64.0 min` in bold green `#16A34A` and `-14.0 min` in bold red `#DC2626`).*

### Left Column Bottom: Summary Takeaways
- **Card Content (Copy directly):**
```text
• Decisive Drift Lead Time: Isolation Forest alarms 64 minutes (Out) and 11 minutes (In) before irreversibility, detecting anomalous variance before absolute temperatures breach baseline thresholds.
• Step Synchrony: For sudden jumps, all models trigger simultaneously at onset (0.0 min lead time).
• Flatline Excursions: Static thresholds fail completely; Isolation Forest catches both frozen sensor events.
• LSTM Adaptation Lag: LSTM was late by 14 min on Out drift due to gradual sequence reconstruction adaptation.
```

### Spoken Presenter Cue (What to say)
> "Here is our primary research finding: On gradual drift disruptions—which represent slow compressor failures—Isolation Forest wins decisively, providing an early warning 64 minutes ahead on Out and 11 minutes ahead on In. On abrupt step breaches, all detectors trigger concurrently at 0 minutes. And for sensor flatlines, the traditional threshold completely fails to fire, while Isolation Forest catches both."

---

## Slide 9: Core Result 2 — Classification Trade-offs & Simulation Parity

### Recommended Canva Layout
- **Style:** Left Column (Model Trade-offs) | Right Column Top (PR Curves Image) + Right Column Bottom (Parity Badge).
- **Right Top Image:** Drag and drop `figures/fig_m4b_pr_curves.png`.

### Top Header Bar
```text
Model Evaluation | Point-Wise Trade-offs & Simulation Fidelity
```

### Left Column: Point-Wise Metrics & Roles
- **Card Title:**
```text
Operational Roles & Classification Trade-Offs
```
- **Card Content (Copy directly):**
```text
• Isolation Forest — High-Recall Early Tripwire:
  - Recall: 80.00% (Out), 91.30% (In)
  - Trade-off: Elevated False Positive Rate (45.59% Out, 26.98% In)
  - Role: Aggressive frontline tripwire where missing an excursion is fatal.
• LSTM-Autoencoder — Precision-Favoring Verifier:
  - On In series: 13.11% Precision, 2.85% FPR, 0.3852 AUC-PR
  - Trade-off: Lower recall on Out series (20.00%, AUC-PR 0.0049)
  - Role: Conservative secondary verifier to prevent operator alarm fatigue.
• Prevalence Context (~0.5% Anomaly Rate):
  - True anomalies represent only ~0.5% of rows (65/13,372 on Out, 23/3,767 on In). Under severe class imbalance, low absolute F1 is mathematically inevitable.
  - Primary Operational Metric: Early-warning lead time (Δt_lead), not point-wise F1!
```

### Right Column Bottom: Parity Badge Box (Green Fill #DCFCE7, Border #16A34A)
- **Badge Title:**
```text
100% Bit-for-Bit Live / Batch Simulation Parity
```
- **Badge Content (Copy directly):**
```text
• High-Speed Replay: SimPy twin replayed 97,603 readings in 6.03 s CPU (>1.9M× speedup) with 0.00 s virtual clock drift.
• Zero Mismatches: Across 30 injections × 3 monitors, all 42 applicable test evaluations matched batch results bit-for-bit (0 mismatches).
• Live Streamlit App: Deployed on Streamlit Cloud with Guided Tour & Free Explore modes (coldchain-ews-twin.streamlit.app).
```

### Spoken Presenter Cue (What to say)
> "Looking at point-wise metrics, we see a classic engineering trade-off: Isolation Forest acts as an aggressive tripwire with high recall over 80–90%, while the LSTM is highly conservative with a 2.85% false-positive rate on enclosure data. Neither detector universally dominates, demonstrating why hybrid architectures are valuable. Crucially, our automated cross-check report achieved a 100% exact match across all 42 comparisons between live SimPy replay and offline batch results, and the entire system is deployed live on Streamlit Cloud."

---

## Slide 10: Conclusion & Corporate Entrepreneurship Relevance

### Recommended Canva Layout
- **Style:** 2 × 2 Grid of 4 Strategic Takeaways + Bottom Full-Width Navy Banner.
- **Icons to search in Canva:** `scales of justice`, `checklist document`, `rocket growth`, `badge checkmark`.

### Top Header Bar
```text
Conclusion & Defense Summary | Topic 21
```

### Card 1 (Top-Left): Evidence-First Risk Management
```text
1. Evidence-First Engineering & Risk Management
Honest reporting of real trade-offs: We openly documented where deep learning lagged on drift and where classical ML excelled, avoiding the common corporate trap of fabricating artificial 99% accuracy claims.
```

### Card 2 (Top-Right): Disciplined Architecture & Auditability
```text
2. Disciplined Architecture & Auditability
Maintained an append-only Architectural Decision Log (35 formal entries D1–D35). This rigorous audit process caught 4 critical bugs (timestamp parse inversion, rolling leakage, cold starts) before they could bias evaluation.
```

### Card 3 (Bottom-Left): Technology Adoption Strategy
```text
3. Technology Adoption Strategy
Demonstrated that classical ML (Isolation Forest) can outperform deep neural networks for edge streaming early warning (+64 min lead time), providing high ROI at low compute overhead.
```

### Card 4 (Bottom-Right): 100% Technical Completion
```text
4. Complete Deliverable Portfolio
100% technically complete and verified: Scaffolding, Models, Discrete-Event Twin, Automated Tests, Full 12-Chapter IEEE Report, and Live Web Dashboard.
```

### Bottom Full-Width Banner (Navy Fill #0E264D, White Text, 15 pt Bold)
```text
Thank You for Your Time! | Open for Questions & Live Interactive Demonstration
Live Deployed Dashboard: coldchain-ews-twin.streamlit.app
```

### Spoken Presenter Cue (What to say)
> "To conclude: this project bridges machine learning, discrete-event digital twins, and disciplined corporate entrepreneurship. We did not cherry-pick our data or claim artificial perfection—we demonstrated exactly where classical ML provides real operational runway, where deep learning lags, and how an organization can rigorously evaluate technology under uncertainty. Thank you, and I look forward to your questions."

---

## Slide 11: References & Benchmark Literature

### Recommended Canva Layout
- **Style:** 2-Card Horizontal Split (Left Card: Recent Cold-Chain Literature 2023–2026 | Right Card: Foundational ML & Project Assets).
- **Icons to search in Canva:** `books literature`, `citation quote`, `code github`.

### Top Header Bar
```text
Topic 21: Cold Chain EWS Twin | References & Benchmark Literature
```

### Card 1 (Left Box): Recent Benchmark Literature (2023–2026)
- **Card 1 Title:**
```text
Recent Cold-Chain & Digital Twin Benchmarks
```
- **Card 1 Content (Copy directly):**
```text
1. Vukšić, M., Ćelić, J., Ogrizović, D., & Perić Hadžić, A. (2026). Early Anomaly Detection in Maritime Refrigerated Containers Using a Hybrid Digital Twin and Deep Learning Framework. Applied Sciences, 16(4), 1887.
2. Xie, Z., Long, H., Ling, C., Zhou, Y., & Luo, Y. (2025). An Anomaly Detection Scheme for Data Stream in Cold Chain Logistics. PLOS ONE, 20(3), e0315322.
3. Meng, X., Xie, R., Liao, J., Shen, X., & Yang, S. (2024). A Cost-Effective Over-Temperature Alarm System for Cold Chain Delivery. Journal of Food Engineering, 368, 111914.
4. Wu, W., Shen, L., Zhao, Z., Harish, A. R., Zhong, R. Y., & Huang, G. Q. (2023). Internet of Everything and Digital Twin Enabled Service Platform for Cold Chain Logistics. Journal of Industrial Information Integration, 33, 100443.
5. Defraeye, T., Shrivastava, C., Berry, T., Verboven, P., Onwude, D., Schudel, S., et al. (2023). Digital Twins of Food Cold Chains: Advances, Challenges, and Opportunities. Computers and Electronics in Agriculture, 214, 108252.
```

### Card 2 (Right Box): Foundational Algorithms & Project Assets
- **Card 2 Title:**
```text
Foundational ML Algorithms & Project Links
```
- **Card 2 Content (Copy directly):**
```text
6. Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation Forest. 2008 Eighth IEEE International Conference on Data Mining (ICDM), 413–422.
7. Malhotra, P., Ramakrishnan, A., Anand, G., Vig, L., Agarwal, P., & Shroff, G. (2016). LSTM-based Encoder-Decoder for Multi-sensor Anomaly Detection. ICML 2016 Anomaly Detection Workshop.
8. Anand Jha, A. (2018). Temperature Readings: IoT Devices Telemetry Dataset. Kaggle Datasets (Structural Proxy Dataset).

• Live Web Application: https://coldchain-ews-twin.streamlit.app/
• Open-Source Code Repository: https://github.com/Krishna200608/coldchain-ews-twin
• Institutional Affiliation: Department of Information Technology, IIIT Allahabad
```

### Spoken Presenter Cue (What to say)
> "Finally, our research is thoroughly grounded in contemporary peer-reviewed literature across food engineering, industrial digital twins, and machine learning. Here are the core benchmark references supporting our methodology and empirical findings. Thank you, and I am now happy to take any questions."

