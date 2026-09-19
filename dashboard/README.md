# Cold Chain EWS Digital Twin — Live Dashboard

Presentation-grade interactive streaming dashboard built with Streamlit for instructor evaluations, viva demonstrations, and technical walkthroughs of the **Digital Twin-Based Early Warning System for Cold Chain Disruption Detection**.

---

### Structural Proxy Notice (D31)
> **Notice:** All telemetry in this repository derives from `IOT-temp.csv` (a generic indoor/outdoor IoT temperature sensor dataset), **not** refrigerated transport or active cold-chain logistics operations. All injected anomalies are synthetic proxy constructs. Detectors carry no regulatory or food-safety significance. Refer to `docs/AD_LOG.md` (D1–D34) for complete architectural decisions and rationale.

---

## 1. Quickstart & Launch

Ensure the Python virtual environment (`.venv`) is active and dependencies are installed:

```bash
# Launch the dashboard locally
.\.venv\Scripts\streamlit run dashboard/app.py
```

Upon launch, Streamlit opens an interactive web interface at `http://localhost:8501`.

### Pre-Flight Verification Gate (D32)
At startup, `dashboard/app.py` verifies the presence of all required model checkpoints and processed evaluation tables:
- `models/isolation_forest_{out,in}.joblib`
- `models/lstm_{out,in}.h5`
- `data/processed/lstm_norm_stats_{out,in}.json`
- `data/processed/{out,in}_features.csv`
- `data/processed/{out,in}_labeled.csv`
- `data/processed/twin_crosscheck_report.csv`
- `data/processed/three_way_comparison.csv`

If any artifact is missing, playback is halted with clear remediation instructions to run `python src/twin_monitors.py && python src/twin_crosscheck.py`.

---

## 2. Operating Modes (D29)

### Mode A: 🎯 Guided Tour (Viva Showcase)
A curated 4-step sequence designed for viva presentations, showcasing distinct failure modes and behavioral contrasts across the three detectors strictly on **out-of-sample test injections**:

1. **Step Anomaly (`out_step_001`)**
   - *Failure Mode:* Abrupt catastrophic step jump (+12.0 °C).
   - *Key Insight:* All three detectors (Naive Baseline, Isolation Forest, and LSTM-Autoencoder) trigger synchronously at the very first reading at `2018-11-17 13:25:00` with an identical lead time of `0.0 min`. Demonstrates zero latency divergence under gross failures.
2. **Incipient Thermal Drift (`out_drift_009`)**
   - *Failure Mode:* Gradual thermal drift (+0.03 °C/min) simulating subtle insulation failure.
   - *Key Insight:* Baseline remains blind until the static threshold is crossed at `03:03:00` (`0.0 min` lead). Isolation Forest detects multivariate anomalies early at `01:59:00`, delivering an early warning advantage of **+64.0 minutes**. LSTM-Autoencoder flags at `03:17:00` with a lead time of **-14.0 minutes** (a 14-minute lag relative to threshold crossing), illustrating sequence memory inertia during creeping, low-slope drift.
3. **In-Range Sensor Flatline (`out_flatline_013`)**
   - *Failure Mode:* Sensor freezes at constant temperature (~37.3 °C) inside normal operating bounds.
   - *Key Insight:* Because temperature never exceeds the static threshold (47.70 °C), the Naive Baseline completely fails to alarm (`None`). Isolation Forest detects the abnormal collapse in rolling variance at `01:22:00`. LSTM reconstruction error stays below threshold (`never_flagged`).
4. **Inbound Thermal Drift (`in_drift_023`)**
   - *Failure Mode:* Inbound sensor drift beginning at `08:07:00`.
   - *Key Insight:* Isolation Forest alarms early at `07:56:00` (**+11.0 min early warning**), while Baseline and LSTM both trigger at `08:07:00` (`0.0 min` lead).

### Mode B: 🔍 Free Explore (All 30 Injections)
- Allows arbitrary inspection of all 30 synthetic anomalies across Out and In series.
- **D26/D31 Clear Demarcation:** Every injection is explicitly tagged in the dropdown as either `[TEST]` (scientifically validated benchmark) or `[TRAIN DEMO]` (training-region demonstration preview). When a train-side injection is selected, a prominent banner clarifies that the model had prior training exposure to that period and no out-of-sample performance claim is made.
- Configurable window padding from $\pm 0.5$ hours to $\pm 6.0$ hours around the injection and search horizon.

---

## 3. Playback & Replay Controls (D28)

- **Timeline Scrubber:** Scrub back and forth across the replayed window to inspect intermediate states, rolling buffers, and detector decisions at any historical timestamp.
- **Replay Controls:** Play (`▶️`), Pause (`⏸️`), Reset (`⏮️`), and Jump to End (`⏭️`).
- **Display-Only Speed Factor:** Speed selection (`1x`, `5x`, `10x`, `25x`, `Instant`) controls UI render intervals only and **never** alters telemetry timestamps, gap seconds, or values passed to detectors (`D28`).

---

## 4. Key Architectural Safeguards

| Decision | Design Principle | Implementation in Dashboard |
|---|---|---|
| **D27** | Zero New Detection Logic | Directly imports `BaselineMonitor`, `IFMonitor`, and `LSTMMonitor` from `src/twin_monitors.py`. Uses exact stable event sorting from `src/digital_twin.py`. |
| **D28** | Accelerated Replay Fidelity | Playback speed is purely visual; streaming telemetry values fed to models are identical to full replay. |
| **D31** | Explicit Proxy Demarcation | Persistent proxy disclaimer banner at the top of the UI; explicit training-exposure warning on all train-region injections. |
| **D32** | Startup Verification Gate | Verifies all 7 model/data files exist before permitting execution; outputs exact command line remediation if missing. |
| **D33** | Silent Buffer Pre-Warming | Pre-warms IF rolling buffer with preceding 10 readings and LSTM buffer with preceding 30 readings prior to the visible window, eliminating cold-start artifacts and ensuring 18/18 exact alarm matches. |
| **D34** | Runtime Dynamic Captions | Captions dynamically interpolate values from `three_way_comparison.csv` and `twin_crosscheck_report.csv` at runtime; zero hardcoded performance claims. |

---

## 5. Automated Tests

The dashboard's pre-warming engine and startup validation are tested via:

```bash
.\.venv\Scripts\python.exe -m unittest tests/test_d33_prewarm.py
```

This suite programmatically verifies:
1. `test_d32_startup_check_existing_files`: Passes when all model/data artifacts exist.
2. `test_d32_startup_check_missing_files`: Properly identifies missing files and triggers remediation.
3. `test_d33_prewarm_reproduces_exact_alarms`: Programmatically runs all 6 test-side injections through pre-warmed window slices and asserts **18/18 bit-exact alarm matches** against `twin_crosscheck_report.csv`.
