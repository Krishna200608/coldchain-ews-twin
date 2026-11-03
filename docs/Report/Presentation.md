# Presentation Deck: Digital Twin-Based Early Warning System for Cold Chain Disruption Detection

**Topic 21:** Digital Twin-Based Early Warning System for Cold Chain Disruption Detection Using Anomaly Detection  
**Course:** Managing Corporate Entrepreneurship (B.Tech 7th Semester, 2026)  
**Presenter:** Krishna Sikheriya (Roll No: IIT2023139)  
**Supervisor / Instructor:** Dr. Netranand Pathak  
**Institution:** Indian Institute of Information Technology, Allahabad (IIITA)  
**Live Application:** [https://coldchain-ews-twin.streamlit.app/](https://coldchain-ews-twin.streamlit.app/)  
**GitHub Repository:** [https://github.com/Krishna200608/coldchain-ews-twin](https://github.com/Krishna200608/coldchain-ews-twin)  

> **How to use this file in Canva / PowerPoint:**  
> Each slide is organized into modular cards, visual containers, and exact copyable text boxes. You can copy each text block directly into your Canva text elements without needing to clean up markdown asterisks or LaTeX code.

---

## Slide 1: Title & Project Identity

### Recommended Canva Layout
- **Style:** Deep Navy Background (`#0E264D`) with clean white and light cyan typography.
- **Top Image:** Drag and drop `figures/iiit_allahabad_logo.png` centered at the top.
- **Center:** Main Title & Subtitle.
- **Bottom:** Metadata block & pill badges.

### Text Box 1: Slide Title (Large, 36–40 pt, Bold White)
```text
Digital Twin-Based Early Warning System for Cold Chain Disruption Detection
```

### Text Box 2: Subtitle (18–20 pt, Light Cyan #BAE6FD)
```text
Physics-Informed Deep Learning, Multi-Horizon Forecasting & Evidential Fusion in a Discrete-Event Simulation Loop (Topic 21)
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
> "Good morning, Professor and peers. Today I am presenting our capstone project for Topic 21: A Digital Twin-Based Early Warning System for Cold Chain Disruption Detection. Our objective is to answer a crucial operational question: Can we move beyond reactive temperature alarms by embedding physics-informed deep learning, uncertainty quantification, and predictive multi-horizon forecasting directly inside an event-driven digital twin, warning operators hours before irreversible spoilage occurs?"

---

## Slide 2: Industrial Context & The Cold Chain Dilemma

### Recommended Canva Layout
- **Style:** 2-Card Horizontal Split (Left Card: The Cold Chain Reality | Right Card: The Status Quo Failure).
- **Icons to search in Canva:** `refrigerated truck`, `temperature sensor`, `alarm bell`.

### Top Header Bar
```text
Topic 21: Cold Chain EWS Twin | Introduction: The Cold-Chain Reality
```

### Card 1 (Left Box): The Cold Chain Reality & High Stakes
- **Card Title:**
```text
The Cold Chain Reality & High Economic Stakes
```
- **Card Content:**
```text
• Strict Thermal Bounds: Cold-chain cargo (vaccines, biologics, perishable foods) demands strict, unbroken temperature control (e.g., 2°C to 8°C).
• High Economic Impact: Over $35 billion in biopharma products and one-third of global food supplies are lost annually due to temperature excursions during transit.
• Public Health Risk: Temperature abuse compromises drug potency and vaccine efficacy, creating severe risks for patients and triggering massive recalls.
```

### Card 2 (Right Box): The Traditional Failure Mode
- **Card Title:**
```text
The Traditional Failure Mode: Reactive Static Alarms
```
- **Card Content:**
```text
• Status Quo: Commercial cold chains rely on static threshold alarms (alerting only if temperature breaches 8°C for >10–15 minutes).
• The Post-Hoc Flaw: Alarms only fire after the thermal boundary has already been breached.
• Irreversible Damage: By the time an operator or driver is notified, cumulative thermal exposure has already caused irreversible biochemical degradation.
```

### Bottom Callout Banner (Red Highlight Box)
```text
The Core Flaw: Waiting for an absolute threshold breach is fundamentally reactive—by the time alarms fire, product damage is already irreversible!
```

### Spoken Presenter Cue (What to say)
> "In pharmaceutical and food cold chains, thermal stability is critical. Over 35 billion dollars of vaccines and biopharmaceuticals are discarded every year due to temperature breaches. Yet today, commercial logistics still relies on static threshold alarms that fire only after temperatures have exceeded limits for 10 or 15 minutes. By that time, cumulative heat exposure has already degraded the product. Traditional monitoring is fundamentally post-hoc and reactive."

---

## Slide 3: Research Gaps & Core Objectives

### Recommended Canva Layout
- **Style:** Left Column (Academic Literature Gap) | Right Column (4 Stacked Research Questions).
- **Icons to search in Canva:** `document search`, `stopwatch`, `neural network`, `atom physics`.

### Top Header Bar
```text
Topic 21: Cold Chain EWS Twin | Research Gap & Core Objectives
```

### Card 1 (Left Box): The Academic Literature Gap
- **Card Title:**
```text
The Academic Gap & Proposed Paradigm Shift
```
- **Card Content:**
```text
• Prior Literature Focus: Academic studies focus predominantly on post-hoc shelf-life kinetics (calculating Arrhenius microbial or enzyme decay after the excursion has completed).
• The Missing Capability: Proactive, real-time early warning embedded within an event-driven digital twin that flags developing thermal failures hours before irreversible breach.
• Proposed Solution: Build an end-to-end discrete-event digital twin hosting physics-informed deep learning, multi-horizon quantile forecasting, and evidential fusion.
```

### Card 2 (Right Top): Research Question 1
- **Title:** `RQ1: Early Warning Runway (Lead Time)`
- **Content:**
```text
How many minutes or hours of actionable early warning (Δt_lead = t_irreversibility - t_alarm) can machine learning deliver relative to when spoilage becomes irreversible?
```

### Card 3 (Right Upper-Middle): Research Question 2
- **Title:** `RQ2: Classical vs. Deep Learning Trade-Offs`
- **Content:**
```text
How do tree ensembles (Isolation Forest) compare against deep autoencoders on irregular, real-world edge telemetry?
```

### Card 4 (Right Lower-Middle): Research Question 3
- **Title:** `RQ3: Digital Twin Simulation Fidelity`
- **Content:**
```text
Can an event-driven SimPy simulation loop process streaming telemetry in real time without cold-start divergence compared to offline batch evaluation?
```

### Card 5 (Right Bottom): Research Question 4
- **Title:** `RQ4: Physics & Uncertainty Integration`
- **Content:**
```text
Can incorporating Newton cooling laws and epistemic uncertainty quantification eliminate false alarms while extending early-warning lead times?
```

### Spoken Presenter Cue (What to say)
> "This brings us to the research gap: most academic literature focuses on post-hoc damage modeling—calculating how much product was ruined after the excursion ended. Our work shifts the paradigm to real-time proactive early warning. We formulated four concrete research questions: First, how much early warning lead time can we gain before irreversible breach? Second, what are the true trade-offs between classical tree models and deep sequence models? Third, can a digital twin run these models in live streaming without cold-start lag? And fourth, can physics-informed loss and uncertainty quantification eliminate the false alarms that plague edge deployments?"

---

## Slide 4: Theoretical Foundations & Literature Review

### Recommended Canva Layout
- **Style:** Clean 6-Row Comparison Table (or 6 Structured Cards).
- **Header Row:** Deep Navy (`#0E264D`) with White Text.

### Top Header Bar
```text
Theoretical Foundations | Literature Review (2023–2026 Key Benchmark Papers)
```

### Table Content (Copy cell by cell into Canva Table)

| Paper Citation | Publication Venue | Core Contribution | Direct Relevance to Topic 21 |
|---|---|---|---|
| **Vukšić et al. (2026)** | Applied Sciences (MDPI) | Hybrid physics-based digital twin + autoencoder for reefer maritime containers. | Reports median lead time of ~68 minutes; independently corroborates our empirical early-warning findings. |
| **Xie et al. (2025)** | PLOS ONE | Improved Isolation Forest with subsampling and feature grouping for cold-chain fleet streams. | Primary tree-ensemble streaming benchmark; contextualizes point-wise F1 metrics under severe anomaly rarity. |
| **Meng et al. (2024)** | Journal of Food Engineering | Box-level digital twin thermal model with static over-temperature alarms. | Represents the static threshold industry standard that our proactive predictive system benchmarks against. |
| **Wu et al. (2023)** | J. Industrial Information Integration | Internet-of-Everything and Digital Twin service platform for cold-chain logistics. | Establishes the architectural precedent for embedding AI inference into operational digital-twin pipelines. |
| **Defraeye et al. (2023)** | Comput. Electron. Agric. | Comprehensive state-of-the-art review on food cold-chain digital twins and sensor dynamics. | Formulates the core challenge: transitioning from reactive post-hoc loss calculation to live event-driven early warning. |
| **Sensoy et al. (2018)** | NeurIPS | Evidential Deep Learning for quantifying classification uncertainty without sampling. | Theoretical foundation for our Dempster-Shafer multimodal evidence fusion module (P5). |

### Bottom Key Takeaway Badge (Green Highlight)
```text
Literature Alignment: Vukšić et al. (2026) report ~68 min lead time on maritime reefers, independently corroborating our findings!
```

### Spoken Presenter Cue (What to say)
> "Our architecture builds on recent peer-reviewed literature. In 2026, Vukšić and colleagues published in Applied Sciences demonstrating a 68-minute median lead time using deep learning on reefer containers, which independently corroborates our empirical results. In 2025, Xie et al. benchmarked Isolation Forest on cold-chain streams, while Meng et al. and Wu et al. established digital twin foundations. Finally, we incorporate Sensoy et al.'s evidential deep learning from NeurIPS to fuse multi-modal evidence under uncertainty."

---

## Slide 5: Data Strategy & Structural Proxy Framing

### Recommended Canva Layout
- **Style:** Left Column (Telemetry Properties & Academic Rigor) | Right Column (Two Stacked Plots).
- **Image 1 (Right Top):** Drag and drop `figures/fig_temperature_distribution.png`.
- **Image 2 (Right Bottom):** Drag and drop `figures/fig_sampling_intervals_corrected.png`.

### Top Header Bar
```text
Experimental Setup | Data Strategy & Structural Proxy Framing
```

### Left Column: Telemetry Dynamics
- **Card Title:**
```text
Empirical Telemetry Properties & Edge Jitter
```
- **Card Content:**
```text
• Real IoT Telemetry: 97,606 raw sensor readings across 133 continuous days (July 28 to Dec 8, 2018), 27,920 unique minute timestamps.
• Extreme Arrival Irregularity: Mean arrival gap = 117.8 s, Median = 0.0 s, Std = 5,446.3 s, Coefficient of Variation CoV = 46.23. Dropouts reach up to 11.57 days, accurately reflecting edge cellular dropouts.
• Dual Streams: Ambient conditions (Out stream, 77,260 rows) and Enclosure internal conditions (In stream, 20,345 rows).
```

### Left Column Bottom: Scientific Rigor Notice (Amber Box #FFFBEB, Border #D97706)
- **Notice Title:**
```text
Academic Rigor: Structural Proxy Notice (Decision D31)
```
- **Notice Content:**
```text
Data originates from an office IoT deployment ('Room Admin'), not live vaccine reefers. Framed strictly as an experimental structural proxy to evaluate irregular streaming pipelines, buffer dynamics, and fault detection without fabricating unverified pharmaceutical claims.
```

### Spoken Presenter Cue (What to say)
> "For our empirical evaluation, we utilized a real-world IoT telemetry dataset of over 97,000 readings spanning 133 days. Real cold-chain IoT networks suffer from severe cellular jitter and packet dropouts—our telemetry reflects this with an arrival variation coefficient of 46.2 and dropouts reaching several days. In adherence to academic integrity and our Architectural Decision D31, we explicitly frame this as a structural proxy for irregular streaming mechanics, rather than fabricating claims of live clinical field deployment."

---

## Slide 6: Digital Twin Architecture & SimPy Simulation

### Recommended Canva Layout
- **Style:** Left Column (Simulation Architecture) | Right Column (5-Stage Flowchart).
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
- **Card Content:**
```text
• Causal Ingestion: Day-first timestamp parsing (preventing 48.8% silent parse inversions). Trailing rolling statistics computed with strict zero look-ahead leakage (D22).
• SimPy 3-Stage Transit: Models physical progression across Source, Transit, and Destination driven by real historical inter-arrival gaps.
• Embedded Streaming Monitors: Real-time scoring at destination sink via Baseline 2-sigma, Isolation Forest, Baseline LSTM-AE, Physics-Informed LSTM, and Evidential Fusion.
• Silent Buffer Pre-Warming (D33): Sliding window buffers are primed with historical telemetry before visible playback begins, eliminating cold-start false alarms.
```

### Right Column: 5 Flowchart Steps (Copy for each card)
- **Card 1 (Navy #0E264D, White text):**
```text
1. Physical Stream Ingestion (97,606 raw IoT sensor events)
```
- **Card 2 (Light Blue #F0F7FF, Border #0284C7):**
```text
2. Causal Feature Engineering (dayfirst=True, Δt_k, trailing rolling statistics, zero leakage)
```
- **Card 3 (Teal #F0FDFA, Border #0D9488):**
```text
3. SimPy Discrete-Event Digital Twin (Source -> Transit -> Destination virtual clock)
```
- **Card 4 (Light Gray #F8FAFC, Border #CBD5E1):**
```text
4. Multi-Paradigm Monitor Inference (Baseline 2σ | Isolation Forest | LSTM-AE | PILSTM | Evidential Fusion)
```
- **Card 5 (Cyan #E0F2FE, Border #0284C7):**
```text
5. Verification Engine & Deployed Dashboard (100% bit-for-bit parity, Streamlit Cloud UI)
```

### Spoken Presenter Cue (What to say)
> "The heart of our system is an event-driven SimPy digital twin modeling the journey of goods from Source, through Transit, to Destination. Every telemetry packet advances the simulation clock based on its true historical inter-arrival interval. At the destination sink, embedded monitors evaluate the stream in real time. We introduced silent buffer pre-warming, ensuring sliding feature windows are primed before playback starts, completely eliminating cold-start false positives."

---

## Slide 7: Controlled Anomaly Protocol & Split Discipline

### Recommended Canva Layout
- **Style:** Left Column (Fault Typologies & Split Rigor) | Right Column (Injection Examples Visual).
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
- **Card Content:**
```text
• 30 Controlled Synthetic Injections (15 Out / 15 In) representing 3 real failure modes:
  - Step Spikes (10): Abrupt +5°C to +15°C jumps (rapid door opening or seal breach).
  - Linear Drifts (10): Gradual ramps of +0.05°C to +0.25°C/min (refrigerant leak or compressor failure).
  - Sensor Flatlines (10): Zero variance persistence (frozen ADC or mechanical stiction).
• Strict Chronological Split: 70% Train / 30% Test split (Cutoff: Oct 29, 2018 11:10:48).
• Out-of-Sample Discipline: 24 injections fall on the training split. All formal benchmark claims are evaluated exclusively on the 6 untouched test injections.
```

### Left Column Bottom: Lead Time Formula Box (Blue Fill #F0F7FF, Border #0284C7)
- **Formula:**
```text
Lead Time Metric: Δt_lead = t_irreversibility - t_alarm
(Where t_irr is a sustained 10-minute breach. Positive = Early Warning; Negative = Late Alarm)
```

### Spoken Presenter Cue (What to say)
> "To benchmark early-warning capability, we designed a controlled anomaly injection protocol with 30 synthetic disruption events representing three real physical failure modes: sudden step spikes, gradual thermal drifts, and frozen sensor flatlines. We enforced a strict chronological 70/30 train/test split. To prevent data leakage and guarantee scientific validity, all headline benchmark claims are evaluated strictly on the six untouched test injections."

---

## Slide 8: Baseline Models & Initial Empirical Findings

### Recommended Canva Layout
- **Style:** Left Column (Lead Time Benchmark Table) | Right Column (Lead Time Bar Chart).
- **Right Image:** Drag and drop `figures/fig_m4b_three_way_lead_times.png`.

### Top Header Bar
```text
Initial Findings | Lead-Time Benchmark on Out-of-Sample Test Injections
```

### Table Content (Copy cell by cell into Canva Table)

| Injection ID | Fault Type | Baseline 2σ Alarm | Isolation Forest Lead Time | Baseline LSTM-AE Lead Time |
|---|---|---|---|---|
| `out_step_001` | Step | 0.0 min | 0.0 min | 0.0 min |
| `out_drift_009` | Drift | 0.0 min | **+64.0 min (Early Warning)** | **-14.0 min (Late Lag)** |
| `out_flatline_012` | Flatline | Undefined (Missed) | **Detected (Variance Collapse)** | **Detected (Variance Collapse)** |
| `out_flatline_013` | Flatline | Undefined (Missed) | **Detected (Variance Collapse)** | Missed |
| `in_step_018` | Step | 0.0 min | 0.0 min | 0.0 min |
| `in_drift_023` | Drift | 0.0 min | **+11.0 min (Early Warning)** | 0.0 min |

### Left Column Bottom: Summary Takeaways
- **Card Content:**
```text
• Decisive Drift Lead Time: Isolation Forest provides +64 minutes (Out) and +11 minutes (In) of early warning before irreversibility, detecting anomalous variance before absolute temperatures breach baseline limits.
• Step Synchrony: For sudden step spikes, all models trigger simultaneously at onset (0.0 min).
• Flatline Blindspot: Static thresholds completely miss frozen sensors, whereas Isolation Forest detects both.
• Deep Learning Adaptation Lag: The baseline LSTM-AE suffered a -14 min lag on Out drift due to gradual sequence reconstruction adaptation.
```

### Spoken Presenter Cue (What to say)
> "Here are our baseline findings: On gradual compressor drift, Isolation Forest delivered 64 minutes of early warning on ambient and 11 minutes on enclosure streams. However, we discovered a major limitation in standard deep learning: the baseline LSTM-AE actually suffered a 14-minute lag on the ambient drift because its recurrent hidden state slowly adapted to the rising trend. Furthermore, Isolation Forest suffered high false positive rates of 26% to 45%. This motivated our five GPU-accelerated research breakthroughs."

---

## Slide 9: Research Breakthroughs 1 & 2 — Physics & Uncertainty

### Recommended Canva Layout
- **Style:** 2-Card Horizontal Split (Left Card: P1 Variational LSTM | Right Card: P2 Physics-Informed LSTM).
- **Embedded Figure Asset:** Drag and drop `figures/fig_breakthrough_p2_physics.png` or `figures/fig_breakthrough_p1_uncertainty.png` into the visual panel.
- **Icons to search in Canva:** `brain network`, `temperature cold`, `balance scale`.

### Top Header Bar
```text
Research Innovations | P1: Uncertainty Quantification & P2: Physics-Informed Neural Networks
```

### Card 1 (Left Box): P1 — Variational LSTM-AE
- **Card Title:**
```text
Proposal P1: Variational LSTM-AE with Epistemic Uncertainty
```
- **Card Content:**
```text
• Mechanism: Implements Monte Carlo Dropout (N=15 forward passes during inference) to decompose total prediction variance into aleatoric (sensor noise) and epistemic (model unfamiliarity) uncertainty.
• Operational Impact: Eliminates unconfident alerts during edge network jitter. On flatline event out_flatline_012, detected +4.0 min early with 9.69% uncertainty, triggering a HIGH_CONFIDENCE_ALARM.
• Benchmark: In PR-AUC improved to 0.3912 (vs 0.3852 baseline LSTM).
```

### Card 2 (Right Box): P2 — Physics-Informed LSTM-AE
- **Card Title:**
```text
Proposal P2: Physics-Informed LSTM-AE (Newton Cooling Law)
```
- **Card Content:**
```text
• Mechanism: Augments reconstruction MSE with a differential thermal physics loss: Loss = MSE + λ_phys · ||dT/dt + k(T - T_amb)||^2, enforcing thermodynamic rate-of-change limits.
• False Alarm Reduction: Slashes Out stream FPR from 20.28% down to 12.52% (a 38.3% relative reduction in false positives).
• Overcoming Adaptation Lag: Converts baseline LSTM's -14.0 min lag on out_drift_009 into +18.0 min early warning (+32 min net operational gain!).
• Fault Categorization: Classifies unphysical spikes as SENSOR_ARTIFACT vs genuine thermal excursion.
```

### Bottom Callout Banner (Green Highlight Box)
```text
Key Physics Gain: Incorporating Newton cooling converted a 14-minute deep learning lag into an 18-minute early warning (+32 min gain) and slashed false alarms by 38.3%!
```

### Spoken Presenter Cue (What to say)
> "To address these shortcomings, our first breakthrough was the Variational LSTM-AE, which runs 15 Monte Carlo dropout passes to quantify epistemic uncertainty, separating genuine structural faults from random sensor noise. Our second breakthrough was the Physics-Informed LSTM-AE. By penalizing violations of Newton's Law of Cooling directly in the loss function, we slashed the ambient false positive rate from 20.28% down to 12.52%. Crucially, the physics regularizer eliminated the LSTM's adaptation lag, turning a 14-minute delay into an 18-minute early warning—a net operational gain of 32 minutes."

---

## Slide 10: Research Breakthrough 3 — Multi-Horizon Forecasting

### Recommended Canva Layout
- **Style:** Left Column (Multi-Horizon Architecture & Lead Time Gains) | Right Column (Quantile Fan Chart).
- **Embedded Figure Asset:** Drag and drop `figures/fig_breakthrough_p3_tft_forecast.png` into the right column.
- **Icons to search in Canva:** `crystal ball forecast`, `chart line trend`, `clock fast forward`.

### Top Header Bar
```text
Research Innovations | P3: Multi-Horizon Quantile Forecaster (TFT)
```

### Left Column: Forecasting Architecture & Proactive Warning
- **Card Title:**
```text
Proactive Excursion Prevention via Quantile Forecasting
```
- **Card Content:**
```text
• Temporal Fusion Transformer (TFT): Multi-horizon autoregressive forecaster predicting future trajectories across 30, 60, and 120-minute horizons.
• Quantile Loss (Pinball Loss): Simultaneously outputs 10th, 50th (median), and 90th percentiles, providing upper-bound worst-case thermal risk profiles.
• Pre-emptive Breach Alarm: Alarms trigger when the 90th percentile forecast breaches thermal bounds within the forecast window—long before the physical cargo heats up.
• Massive Lead-Time Gains:
  - On in_drift_023: Achieves +189.0 minutes (+3.15 hours) of pre-emptive early warning!
  - On out_drift_009: Achieves +56.0 minutes of pre-emptive early warning!
```

### Right Column: Operational Runway Impact Box
- **Card Title:**
```text
Operational Decision Runway
```
- **Card Content:**
```text
• Reactive Threshold Alarm: 0 minutes runway (Damage already occurring).
• Classical Anomaly Detector: 11 to 64 minutes runway (Detection after drift begins).
• Multi-Horizon Quantile Forecaster: 56 to 189 minutes runway (>3 hours advance warning!).
• Logistics Actionability: Gives dispatchers sufficient time to reroute refrigerated vehicles, service auxiliary generators, or transfer sensitive cargo to backup reefers.
```

### Spoken Presenter Cue (What to say)
> "Our third breakthrough was a Temporal Fusion Transformer for multi-horizon quantile forecasting. Instead of merely asking whether the current temperature reading is anomalous, the model forecasts temperature trajectories 30, 60, and 120 minutes into the future across the 10th, 50th, and 90th percentiles. When the 90th percentile indicates a future boundary breach, the system triggers a pre-emptive alert. This extended our early warning lead time to an extraordinary 189 minutes—more than three hours before product spoilage becomes irreversible."

---

## Slide 11: Research Breakthroughs 4 & 5 — Adaptive Thresholds & Evidential Fusion

### Recommended Canva Layout
- **Style:** 2-Card Horizontal Split (Left Card: P4 Kalman CUSUM | Right Card: P5 Evidential Fusion).
- **Embedded Figure Asset:** Drag and drop `figures/fig_breakthrough_p5_evidential_fusion.png` into the presentation slide.
- **Icons to search in Canva:** `filter funnel`, `shield checkmark`, `target bullseye`.

### Top Header Bar
```text
Research Innovations | P4: Adaptive Thresholds & P5: Evidential Deep Learning Fusion
```

### Card 1 (Left Box): P4 — Kalman-CUSUM Adaptive Thresholding
- **Card Title:**
```text
Proposal P4: Contamination-Guarded Kalman Filter + CUSUM
```
- **Card Content:**
```text
• Mechanism: Replaces static sigma thresholds with dynamic boundaries driven by a 1D Kalman state estimator and two-sided Cumulative Sum (CUSUM) change-point detection.
• Contamination Guard: Freezes Kalman state updates when anomaly probability exceeds 0.70, preventing the threshold from absorbing creeping drift.
• Benchmark Impact: Slashed Out stream FPR from 45.68% down to 29.45% (a 35.5% relative reduction in false positives).
```

### Card 2 (Right Box): P5 — Evidential Deep Learning & Dempster-Shafer Fusion
- **Card Title:**
```text
Proposal P5: Dempster-Shafer Multimodal Evidence Fusion
```
- **Card Content:**
```text
• Multimodal Input: Fuses Physics Residuals, Temporal Reconstruction Error, and Epistemic Uncertainty into Dirichlet belief masses (Belief_normal, Belief_anomaly, Uncertainty/Vacuity).
• Zero False Alarm Rate: Achieved 0.00% FPR across both Out and In streams (0 false alarms out of 13,307 test Out and 3,744 test In observations!).
• Benchmark Accuracy: 100.0% Precision, 86.96% Recall, F1 = 0.9302, and In PR-AUC = 0.9137 (vs 0.3852 baseline LSTM).
• Retained Lead Times: +178.0 min (in_drift_023), +30.0 min (out_drift_009), +46.0 min (out_step_001), +16.0 min (in_step_018).
```

### Bottom Callout Banner (Green Highlight Box)
```text
The Evidential Fusion Breakthrough: 0.00% False Positive Rate, 100% Precision, F1 of 0.9302, and up to 178 minutes of early warning!
```

### Spoken Presenter Cue (What to say)
> "Our fourth breakthrough was Kalman-CUSUM adaptive thresholding with a contamination guard, which reduced false positives by 35%. However, our crowning achievement is Proposal P5: Evidential Deep Learning Fusion. Using Dempster-Shafer theory, we fused physics residuals, temporal reconstruction errors, and epistemic uncertainty into a unified belief space. This completely eliminated false alarms—achieving a 0.00% False Positive Rate across more than 17,000 test observations, 100% Precision, an F1 score of 0.93, while preserving up to 178 minutes of actionable early warning."

---

## Slide 12: Master Benchmark & Comparative Performance Matrix

### Recommended Canva Layout
- **Style:** Comprehensive 7-Row Performance Comparison Table with Visual Plot Badges.
- **Embedded Figure Assets:** Drag and drop `figures/fig_breakthrough_leadtimes.png` and `figures/fig_breakthrough_master_tradeoff.png`.
- **Header Row:** Deep Navy (`#0E264D`) with White Text.
- **Highlight:** Highlight the Evidential Fusion row in subtle Gold or Green.

### Top Header Bar
```text
Empirical Validation | Master Performance Benchmark Across All Paradigms
```

### Table Content (Copy cell by cell into Canva Table)

| Model Paradigm | In FPR (%) | Out FPR (%) | Recall (%) | F1 Score | In PR-AUC | In Drift Lead Time | Out Drift Lead Time |
|---|---|---|---|---|---|---|---|
| **Static Threshold (2σ)** | 26.98% | 45.68% | 91.30% | 0.040 | 0.0400 | 0.0 min | 0.0 min |
| **Isolation Forest** | 26.98% | 45.59% | 91.30% | 0.040 | 0.0400 | +11.0 min | +64.0 min |
| **Baseline LSTM-AE** | 2.85% | 20.28% | 43.48% | 0.1587 | 0.3852 | 0.0 min | -14.0 min (lag) |
| **P1: Variational LSTM-AE** | 2.80% | 19.84% | 43.48% | 0.1613 | 0.3912 | 0.0 min | -14.0 min |
| **P2: Physics-Informed LSTM** | 2.10% | 12.52% | 43.48% | 0.2041 | 0.4210 | 0.0 min | **+18.0 min** |
| **P3: Multi-Horizon Forecaster** | — | — | — | — | — | **+189.0 min** | **+56.0 min** |
| **P5: Evidential Fusion (EDL)** | **0.00%** | **0.00%** | **86.96%** | **0.9302** | **0.9137** | **+178.0 min** | **+30.0 min** |

### Bottom Key Insights Box (Copy directly)
```text
• False Positive Eradication: Evidential Fusion slashes FPR from 45.7% to 0.00% while driving PR-AUC from 0.3852 to 0.9137.
• Physics Breakthrough: Physics loss eliminates LSTM adaptation lag, converting a 14-min delay into an 18-min early warning.
• Maximum Warning Runway: TFT Forecaster delivers up to 189 minutes (>3 hours) of pre-emptive decision runway.
```

### Spoken Presenter Cue (What to say)
> "Here is our comprehensive master benchmark matrix. Moving from static thresholding to Evidential Deep Learning fusion drives our F1 score from 0.04 up to 0.9302 and PR-AUC from 0.3852 to 0.9137, while completely eliminating false positives on the test set. At the same time, our multi-horizon forecasting delivers over three hours of early warning. Every metric on this slide is backed by reproducible automated tests and JSON artifacts."

---

## Slide 13: Interactive Dashboard & Digital Twin Demonstration

### Recommended Canva Layout
- **Style:** Left Column (Dashboard Features & Architecture) | Right Column (Interactive Modes & Parity Badge).
- **Icons to search in Canva:** `dashboard screen`, `video play`, `speed gauge`, `check shield`.

### Top Header Bar
```text
System Deployment | Interactive Streamlit Dashboard & Live Digital Twin
```

### Left Column: Cloud Dashboard Architecture
- **Card Title:**
```text
Streamlit Cloud Live Deployment
```
- **Card Content:**
```text
• Production Deployment: Deployed on Streamlit Community Cloud at coldchain-ews-twin.streamlit.app with full GPU research showcase.
• Dynamic Visualizations: Interactive Plotly time-series charts rendering temperature trajectories, 2σ boundaries, anomaly score overlays, and playhead markers.
• Research Showcase Tab: Dedicated interactive exploration of Physics Residuals, Epistemic Uncertainty bands, Multi-Horizon Quantile forecasts, and Evidential Belief masses.
```

### Right Column Top: Dual Interaction Modes
- **Card Title:**
```text
Dual User Experience Modes
```
- **Card Content:**
```text
• Guided Tour Mode: Curated 4-step walkthrough for non-technical executives and evaluators, highlighting baseline failure, Isolation Forest early warning, LSTM precision, and Evidential zero-FPR fusion.
• Free Explore Mode: Full parameter control allowing operators to select any of 30 synthetic injections, adjust replay speed (1× to 10,000×), and inspect raw telemetry.
```

### Right Column Bottom: Parity Verification Badge (Green Fill #DCFCE7, Border #16A34A)
- **Badge Content:**
```text
100% Bit-for-Bit Digital Twin Simulation Parity (Decision D33)
Replayed 97,603 readings in 6.03 s CPU (>1.9M× speedup) with 0.00 s virtual clock drift. All 42 test evaluations matched batch results bit-for-bit (0 mismatches).
```

### Spoken Presenter Cue (What to say)
> "We translated our research into an operational interactive dashboard deployed live on Streamlit Cloud. It features two user modes: a Guided Tour for non-technical stakeholders and a Free Explore mode for operations engineers. Our SimPy digital twin replays over 97,000 events in just six seconds—a 1.9-million-times speedup—with zero clock drift and a 100% bit-for-bit parity match against batch evaluations."

---

## Slide 14: Corporate Entrepreneurship, Technology Adoption & Conclusion

### Recommended Canva Layout
- **Style:** 2 × 2 Grid of 4 Corporate Entrepreneurship Pillars + Bottom Full-Width Navy Banner.
- **Icons to search in Canva:** `scales of justice`, `checklist document`, `rocket growth`, `badge checkmark`.

### Top Header Bar
```text
Conclusion & Corporate Entrepreneurship | Defense Summary (Topic 21)
```

### Card 1 (Top-Left): Evidence-First Risk Management
```text
1. Evidence-First Engineering & Risk Management
Honest reporting of real trade-offs: We documented where deep learning lagged on drift and where classical ML excelled, avoiding the common corporate trap of fabricating artificial 99% accuracy claims without validation.
```

### Card 2 (Top-Right): Architectural Decision Governance
```text
2. Disciplined Architecture & Auditability (D1–D40)
Maintained an append-only Architectural Decision Log across 40 formal decisions. This governance framework caught 4 critical bugs (timestamp parse inversion, rolling leakage, cold starts) before they could bias evaluation.
```

### Card 3 (Bottom-Left): Technology Adoption ROI Strategy
```text
3. Tiered Technology Adoption Strategy
Demonstrated that a multi-tiered architecture provides optimal ROI: lightweight classical ML / Kalman filters for cheap edge gateways, backed by physics-informed and evidential models for central cloud dispatchers.
```

### Card 4 (Bottom-Right): 100% Technical Completion
```text
4. Comprehensive Deliverable Portfolio
100% technically complete: Scaffolding, Models, Digital Twin, 26 Automated Tests, 12-Chapter IEEE Report, and Live Deployed Cloud Dashboard.
```

### Bottom Full-Width Banner (Navy Fill #0E264D, White Text, 15 pt Bold)
```text
Thank You for Your Time! | Open for Questions & Live Interactive Demonstration
Live Deployed Dashboard: coldchain-ews-twin.streamlit.app
```

### Spoken Presenter Cue (What to say)
> "To conclude: this project embodies the core principles of Corporate Entrepreneurship. We tackled an unsolved industrial challenge, governed development through 40 audited architectural decisions, reported genuine empirical trade-offs with complete scientific integrity, and demonstrated a multi-tiered AI architecture delivering zero false alarms and hours of operational runway. Thank you, Professor and peers. I am now open to your questions and ready for the live demonstration."

---

## Slide 15: References & Scientific Bibliography

### Recommended Canva Layout
- **Style:** 2-Card Horizontal Split (Left Card: Cold-Chain & Digital Twin Papers | Right Card: AI, Physics & Foundational Papers).

### Top Header Bar
```text
References | Academic Literature & Project Repositories
```

### Card 1 (Left Box): Cold Chain & Digital Twin Literature
```text
1. Vukšić, M., et al. (2026). Early Anomaly Detection in Maritime Refrigerated Containers Using a Hybrid Digital Twin and Deep Learning Framework. Applied Sciences, 16(4), 1887.
2. Xie, Z., et al. (2025). An Anomaly Detection Scheme for Data Stream in Cold Chain Logistics. PLOS ONE, 20(3), e0315322.
3. Meng, X., et al. (2024). A Cost-Effective Over-Temperature Alarm System for Cold Chain Delivery. Journal of Food Engineering, 368, 111914.
4. Wu, W., et al. (2023). Internet of Everything and Digital Twin Enabled Service Platform for Cold Chain Logistics. J. Industrial Information Integration, 33, 100443.
5. Defraeye, T., et al. (2023). Digital Twins of Food Cold Chains: Advances, Challenges, and Opportunities. Computers and Electronics in Agriculture, 214, 108252.
```

### Card 2 (Right Box): Machine Learning & Evidential Foundations
```text
6. Sensoy, M., Kaplan, L., & Kandemir, M. (2018). Evidential Deep Learning to Quantify Classification Uncertainty. NeurIPS 2018, 31, 3179–3189.
7. Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). Physics-Informed Neural Networks. Journal of Computational Physics, 378, 686–707.
8. Lim, B., et al. (2021). Temporal Fusion Transformers for Interpretable Multi-Horizon Time Series Forecasting. Int. J. Forecasting, 37(4), 1748–1764.
9. Liu, F. T., Ting, K. M., & Zhou, Z.-H. (2008). Isolation Forest. IEEE ICDM, 413–422.
10. Anand Jha, A. (2018). Temperature Readings: IoT Devices Telemetry Dataset. Kaggle Datasets (Structural Proxy Dataset).

• Live Web Application: coldchain-ews-twin.streamlit.app
• Open-Source Code: github.com/Krishna200608/coldchain-ews-twin
```

### Spoken Presenter Cue (What to say)
> "Finally, here is the complete bibliography of peer-reviewed literature across food cold chains, digital twins, physics-informed neural networks, and evidential deep learning that grounds our methodology and empirical conclusions. Thank you."
