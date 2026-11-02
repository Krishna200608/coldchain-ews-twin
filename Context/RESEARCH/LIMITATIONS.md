# Research Limitations & Threats to Validity

This document explicitly identifies the structural, theoretical, and empirical limitations of this project.

---

## 1. Structural Proxy Limitations

> [!WARNING]
> **Data Origin Invariant (D31):**
> The underlying telemetry is derived from `IOT-temp.csv`, an ambient room temperature dataset deployed in an office administrative space. It does **not** originate from real refrigerated trucks, cold-storage warehouses, or pharmaceutical cryo-shippers.

1. **Absence of Real Spoilage Data:** No biological or biochemical degradation assays (e.g., bacterial colony-forming unit counts, enzyme denaturation assays, or sensory quality evaluations) exist for this dataset.
2. **Proxy Irreversibility:** The 10-minute continuous threshold excursion (`D_IRREV_MINUTES = 10.0`) is an **arbitrary mathematical proxy construct**. It must not be interpreted as an empirical microbial growth curve.
3. **Synthetic Fault Injection:** Injected step, drift, and flatline faults are mathematical models. While grounded in realistic failure physics, they cannot capture all complexities of physical refrigerant phase transitions or compressor short-cycling.

---

## 2. Spatial & Topological Limitations

1. **Lack of Multi-Hop Transit Routing:** Milestone 1 EDA confirmed that the `room_id/id` field is 100% constant (`'Room Admin'`). The dataset lacks spatial GPS coordinates, altitude data, or multi-stage logistics hops (e.g., farm $\to$ distribution hub $\to$ retail store).
2. **Single-Point Ambient Telemetry:** Sensors measured ambient air temperature. In physical cold chains, products possess substantial **thermal mass**, causing internal core temperatures to lag ambient air fluctuations. This thermal inertia is not captured in air-only telemetry.
3. **Absence of Auxiliary Channels:** The dataset does not contain relative humidity, door-contact reed switches, compressor electrical current draw, or vibration accelerometer data.

---

## 3. Algorithmic & Operational Limitations

### 3.1. False Positive Burden in High-Entropy Telemetry
Under scikit-learn's default `contamination='auto'`, Isolation Forest exhibits a **False Positive Rate of 45.59%** in the outdoor ambient channel (`Out`).
- In operational logistics, such a high false alarm rate would cause immediate **operator alarm fatigue**, leading technicians to ignore alerts.
- Production deployment would require supervised threshold tuning using domain-calibrated acceptable alarm rates (e.g., $< 1.0\%$).

### 3.2. LSTM Sliding Window Sequence Lag
The LSTM-Autoencoder requires a sliding window of $L = 30$ observations to execute inference.
- On rapid thermal spikes or sudden catastrophic breaches (`out_step_001`), the model exhibits **sequence memory inertia**, lagging the baseline detector by several minutes while anomalous points gradually fill the buffer.
- The model carries an initial **29-reading causal blind spot** at the beginning of any isolated telemetry stream.

### 3.3. Stationary Normalization Assumption
Normalization parameters are computed from the historical training split. If long-term multi-year climate shifts alter nominal seasonal ranges, the fixed normalization statistics will experience distribution drift, degrading reconstruction fidelity.

