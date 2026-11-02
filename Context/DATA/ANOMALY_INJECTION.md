# Synthetic Anomaly Injection

The anomaly injection subsystem (`src/anomaly_injection.py`) synthesizes realistic thermal disruption scenarios into clean telemetry copies to establish ground-truth labels for early warning benchmarking (Milestone 2).

---

## 1. Motivation & Governance

Real cold-chain telemetry rarely contains known, labeled thermal failure events accompanied by microsecond-accurate ground-truth onset timestamps. To rigorously evaluate detector lead times and false alarm rates, controlled synthetic perturbations are injected onto uncorrupted sensor logs.

### 1.1. Methodological Guardrails
- **Non-Destructive Execution (D3):** Clean reference feature files (`out_features.csv`, `in_features.csv`) are read-only. Perturbations are applied to memory copies and persisted into separate labeled artifacts (`out_labeled.csv`, `in_labeled.csv`).
- **Comprehensive Audit Trail:** Every injected event is logged in `data/processed/injection_log.csv` with its seed, start index, onset timestamp, duration, and magnitude.
- **Reproducibility Guarantee:** Random operations use `np.random.default_rng(RANDOM_SEED)` with `RANDOM_SEED = 42`.
- **Zero-Overlap Isolation:** An injection buffer of at least 5 readings (`MIN_GAP_BETWEEN_INJECTIONS = 5`) ensures perturbations never intersect or corrupt preceding baseline states.

---

## 2. Injected Fault Typologies

```mermaid
flowchart LR
    Clean["Clean Telemetry Stream<br>(temp)"]
    
    Clean -->|Add Constant M| Step["Step (Spike)<br>Sudden door opening / breach"]
    Clean -->|Add Linear Ramp| Drift["Drift (Thermal Runaway)<br>Coolant leak / compressor wear"]
    Clean -->|Freeze at T[s-1]| Flatline["Flatline (Sensor Freeze)<br>Stuck ADC / hardware fault"]
```

### 2.1. Step (Abrupt Thermal Spike)
Models sudden catastrophic temperature jumps, such as an open reefer container door, direct sunlight exposure, or sudden power disconnection.
- **Mathematical Formula:**
  
  $$T_{\text{injected}}[i] = T_{\text{clean}}[i] + M \quad \text{for } i \in [s, s + D - 1]$$
  
- **Magnitude ($M$):** Uniformly sampled from $[5.0, 15.0]^\circ\text{C}$ (`STEP_MAG_MIN` to `STEP_MAG_MAX`).
- **Duration ($D$):** Integer sampled from $[5, 30]$ readings (`DUR_MIN` to `DUR_MAX`).

### 2.2. Drift (Incipient Thermal Runaway)
Models progressive thermodynamic degradation, such as slow refrigerant leakage, failing insulation gaskets, or thermal mass heat-soak.
- **Mathematical Formula:**
  
  $$T_{\text{injected}}[i] = T_{\text{clean}}[i] + \left( \frac{i - s}{D - 1} \right) \cdot M_{\text{final}} \quad \text{for } i \in [s, s + D - 1]$$
  
- **Final Magnitude ($M_{\text{final}}$):** Uniformly sampled from $[5.0, 20.0]^\circ\text{C}$ (`DRIFT_FINAL_MAG_MIN` to `DRIFT_FINAL_MAG_MAX`).
- **Duration ($D$):** Integer sampled from $[5, 30]$ readings.

### 2.3. Flatline (Sensor Freeze / Stuck Telemetry)
Models electrical sensor faults, microcontroller lockups, or frozen ADC converters where the telemetry value ceases updating and reports a constant reading.
- **Mathematical Formula:**
  
  $$T_{\text{injected}}[i] = T_{\text{clean}}[s - 1] \quad \text{for } i \in [s, s + D - 1]$$
  
- **Source Value ($T_{\text{clean}}[s - 1]$):** The unperturbed real reading immediately preceding the injection onset.
- **Duration ($D$):** Integer sampled from $[5, 30]$ readings.
- **Theoretical Implication:** If the frozen temperature is below the static baseline threshold, **static threshold monitors can never fire**, creating an indefinite blind spot that only structural models can detect.

---

## 3. Discrepancy Note: Source Code vs. Early Documentation

> [!NOTE]
> **Authoritative Parameter Resolution:**
> Early documentation drafts mentioned injection durations varying across types (e.g., 10–50 for step, 30–120 for drift, 20–80 for flatline). The authoritative, implemented codebase in `src/anomaly_injection.py` unifies injection durations to **5–30 readings** across all three fault types (`DUR_MIN = 5`, `DUR_MAX = 30`). The code constants represent ground truth.

---

## 4. Injection Inventory & Train/Test Partitioning

The injection suite generates:
$$\text{Total Injections} = (5\text{ Step} + 5\text{ Drift} + 5\text{ Flatline}) \times 2\text{ Series} = \mathbf{30\text{ Injections}}$$

### 4.1. Chronological Partitioning (D6, D26)
With chronological cutoff at $t_{\text{cutoff}} = \text{2018-10-29 11:10:48}$:
- **Train-Side Injections (24 total):** 12 in Out, 12 in In. Labeled `train_test_status = "train"`. Used for exploratory visualization and UI demonstration only.
- **Test-Side Injections (6 total):** 3 in Out, 3 in In. Labeled `train_test_status = "test"`. Constitutes the **authoritative scientific benchmark suite**.

### 4.2. Authoritative Test-Side Benchmark Injections

| Injection ID | Series | Fault Type | Start Timestamp | End Timestamp | Duration | Perturbation Parameter |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`out_step_001`** | Out | Step | 2018-11-17 13:25:00 | 2018-11-17 14:05:00 | 17 readings | $M = +10.97 ^\circ\text{C}$ |
| **`out_drift_001`** | Out | Drift | 2018-11-16 01:59:00 | 2018-11-16 03:03:00 | 18 readings | $M_{\text{final}} = +13.56 ^\circ\text{C}$ |
| **`out_flatline_001`** | Out | Flatline | 2018-11-09 23:44:00 | 2018-11-10 00:06:00 | 12 readings | Frozen at $41.00 ^\circ\text{C}$ |
| **`in_step_016`** | In | Step | 2018-11-05 13:30:00 | 2018-11-05 14:14:00 | 11 readings | $M = +10.37 ^\circ\text{C}$ |
| **`in_drift_016`** | In | Drift | 2018-11-06 08:38:00 | 2018-11-06 09:32:00 | 10 readings | $M_{\text{final}} = +16.03 ^\circ\text{C}$ |
| **`in_flatline_016`** | In | Flatline | 2018-11-07 15:46:00 | 2018-11-07 16:35:00 | 12 readings | Frozen at $29.00 ^\circ\text{C}$ |

