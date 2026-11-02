# Terminology and Glossary

> **Single Source of Truth:** `Context/PROJECT/TERMINOLOGY.md`  
> **Related Documents:**  
> - [`PROJECT_OVERVIEW.md`](PROJECT_OVERVIEW.md)  
> - [`PROBLEM_STATEMENT.md`](PROBLEM_STATEMENT.md)  
> - [`../MODELS/MODEL_EVALUATION.md`](../MODELS/MODEL_EVALUATION.md)  
> - [`../DIGITAL_TWIN/SIMULATION_ENGINE.md`](../DIGITAL_TWIN/SIMULATION_ENGINE.md)

---

## Standardized Project Lexicon

To prevent ambiguity across code comments, documentation, and academic reporting, this repository enforces the following standardized definitions:

### 1. Domain & Physical Concepts

* **Cold Chain:** An unbroken, temperature-controlled supply chain required to preserve the quality, potency, and safety of perishable foods, biopharmaceuticals, and chemical reagents from synthesis to point-of-use.
* **Thermal Excursion:** Any event where temperature deviates outside prescribed safe product boundaries (e.g., above $+8.0^\circ\text{C}$ or below $+2.0^\circ\text{C}$ for standard refrigerated biologicals).
* **Thermal Inertia:** The physical resistance of a material (due to its mass and specific heat capacity) to temperature change. Because cargo has high thermal inertia, interior product temperature warms much more slowly than surrounding air.
* **Structural Proxy:** An experimental dataset or environment that possesses the exact statistical and structural properties of a target domain (e.g., irregular temporal gaps, multi-channel streams, sensor noise) but originates from a different physical setting. In this project, `IOT-temp.csv` (an office IoT dataset) is used strictly as a structural proxy for refrigerated transit pipelines (D1, D31).

---

### 2. Temporal & Evaluation Metrics

* **Alarm Timestamp ($t_{\text{alarm}}$):** The earliest timestamp within an evaluation search window at which an anomaly detector emits an active alarm flag (`alarm == True`).
* **Irreversibility Timestamp ($t_{\text{irreversibility}}$ or $t_{\text{irr}}$):** The timestamp marking the onset of sustained, catastrophic thermal failure. In this project, it is formally defined as the first point of a continuous, unbroken exceedance of the naive $2\sigma$ baseline threshold lasting $\ge 10.0\text{ minutes}$ (`D_IRREV_MINUTES = 10.0`, D4).
* **Early-Warning Lead Time ($\Delta t_{\text{lead}}$):** The primary operational metric in this repository, quantifying the intervention runway delivered by a detector:
  $$\Delta t_{\text{lead}} = t_{\text{irreversibility}} - t_{\text{alarm}}$$
  * **Positive Lead Time ($\Delta t_{\text{lead}} > 0$):** Actionable advance warning. The alarm fired before irreversibility occurred (e.g., $+64.0\text{ min}$).
  * **Zero Lead Time ($\Delta t_{\text{lead}} = 0.0\text{ min}$):** Synchronous alarm. The alarm fired at the exact moment of onset/exceedance.
  * **Negative Lead Time ($\Delta t_{\text{lead}} < 0$):** Late alarm. The detector alarmed after irreversible damage had already occurred (e.g., $-14.0\text{ min}$).
  * **Undefined Lead Time (`NaN`):** Occurs when the irreversibility criterion was never met (e.g., sub-threshold flatlines) or the detector never alarmed.
* **Search Horizon (`SEARCH_HORIZON_MINUTES = 60.0`):** The bounded temporal window $[t_{\text{onset}}, t_{\text{end}} + 60\text{ min}]$ within which alarms and irreversibility must occur to be credited to a synthetic disruption event (D4 fix). Prevents latching onto unrelated real excursions occurring days later.

---

### 3. Machine Learning & Statistical Definitions

* **Causal Feature Engineering:** Computing features at timestamp $t_k$ strictly using historical observations ($t \le t_k$). Any feature that incorporates future observations ($t > t_k$) is a **lookahead leakage** violation.
* **Count-Based Window:** A sliding window defined by a fixed number of consecutive real readings ($L = 30$ readings for LSTM, $W = 10$ readings for IF), rather than a fixed clock time span (e.g., 30 minutes). Count-based windowing avoids artificial resampling across irregular arrival intervals (D1, D9).
* **Blind Spot (NaN Rows):** The initial rows at the beginning of an evaluation partition that lack sufficient preceding history to fill a count-based sliding window (e.g., the first 29 rows of a split for an LSTM requiring $L=30$).
* **Reconstruction Error (MSE):** The mean squared difference between the normalized input tensor and the decoded output tensor of an autoencoder. In our causal formulation (D16), anomaly scoring uses the MSE at the **last timestep** of the window ($t_k$).
* **Contamination Parameter:** The proportion of anomalies expected in a dataset. In this project, it is frozen at `contamination='auto'` (scikit-learn default heuristic) to prevent leaking test-set ground-truth labels into model configuration (D7).
* **Point-Wise vs. Event-Level Evaluation:**
  * *Point-Wise:* Treating each individual row/timestamp as an isolated classification instance (evaluating Precision, Recall, $F_1$, and AUC-PR). Heavily penalizes early alarms before the synthetic label boundary.
  * *Event-Level:* Treating the entire disruption incident as a single operational event (evaluating whether an alarm was raised and calculating $\Delta t_{\text{lead}}$).

---

### 4. Digital Twin & Simulation Terms

* **Discrete-Event Simulation (DES):** A modeling paradigm where system state changes occur instantaneously at discrete points in time when events happen, rather than advancing on continuous differential clock steps.
* **Virtual Clock (`env.now`):** SimPy's simulation time variable. It advances from event to event based on real historical inter-arrival gaps (`gap_seconds`), simulating 133 days of telemetry in ~6 seconds of CPU time (D18).
* **Buffer Pre-Warming (D33):** The protocol of silently feeding preceding historical telemetry readings into detector deques before starting a visible replay window, completely eliminating cold-start false alarms.
* **Live/Batch Parity:** A state where streaming online detectors running inside the digital twin loop produce the exact same alarm flags and timestamps as offline batch vector processing (0 mismatches).
* **Single Source of Truth (SSOT):** An architectural design pattern where every quantitative claim, metric, or threshold originates from a single authoritative serialized artifact, preventing documentation or UI drift.

