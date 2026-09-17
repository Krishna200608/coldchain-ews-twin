# Architecture Decision Log — Cold Chain EWS Digital Twin

All significant design/data decisions for this project are recorded here in
reverse-chronological order. Each entry states *what* was decided and *why*.

## 2026-09-17 — D8: Reusing baseline irreversibility timestamps for lead-time benchmarking (Milestone 3)

**Decision:** `irreversibility_timestamp` is directly reused from `data/processed/injection_evaluation_baseline.csv` (Milestone 2 output) for all 30 injections — it is **never recomputed**. Isolation Forest triggers its alarm at `alarm_timestamp_IF` (the first reading within the bounded window `[onset_ts, injection_end_ts + SEARCH_HORIZON_MINUTES]` where `if_anomaly = True`). The early-warning lead time is defined as `lead_time_IF = irreversibility_timestamp - alarm_timestamp_IF` and compared side-by-side with `lead_time_baseline`.

**Rationale:** The irreversibility timestamp represents the simulated failure / damage milestone (sustained 10-minute threshold exceedance). By keeping this timestamp invariant across all models, differences in lead time purely measure the detectors' relative early-warning responsiveness rather than artifactual shifts in the failure criterion.

**Limitation:** For injections where the irreversibility criterion was never met under M2's bounded search horizon (such as flatline anomalies or sub-threshold excursions), both baseline and IF lead times are undefined (`NaN`).

---

## 2026-09-17 — D7: Contamination parameter 'auto' and PR curve evaluation (Milestone 3)

**Decision:** The discrete decision threshold for Isolation Forest is set to `contamination='auto'` (scikit-learn's default, untuned heuristic). The true injected-row fraction is **strictly not passed** as the contamination parameter. In addition to discrete point-wise metrics (precision, recall, F1, FPR, confusion counts: TP/FP/TN/FN), a complete continuous precision-recall curve and average precision (AUC-PR) are computed on the negated continuous decision function (`-if_score`).

**Rationale:** In an operational cold-chain deployment, future anomaly rates are unknown a priori. Setting `contamination` to the ground-truth injected fraction would leak test labels into model configuration. Using `contamination='auto'` evaluates an honest, untuned unsupervised detector. Generating the continuous PR curve and reporting AUC-PR exposes the detector's complete ranking quality across the entire threshold operating spectrum.

**Limitation:** `contamination='auto'` flags ~20.4% of Out rows and ~13.4% of In rows as anomalies, whereas synthetic anomalies comprise <0.5% of test data. Consequently, the discrete operating point exhibits high recall (80.0% Out, 91.3% In) but very low precision (<2%) and high false positive rates (45.6% Out, 27.0% In). This highlights the fundamental limitation of untuned unsupervised Isolation Forests on raw tabular features without task-specific threshold calibration.

**Distributional drift diagnostic (Addendum):** An explicit diagnostic comparing train rows (`ts < cutoff_ts`) vs test rows (`ts >= cutoff_ts`) reveals that the high FPR on the test set is also partly driven by significant **temporal and seasonal distributional drift**, not solely the untuned contamination parameter:
- **Series Out:** Mean temperature in the test period is **+3.50 °C higher** than in the training period (39.18 °C test vs 35.68 °C train) with narrower variance (std 3.36 °C test vs 5.95 °C train). Concurrently, average inter-reading sampling intervals more than doubled (mean 266.1 s test vs 124.3 s train).
- **Series In:** Mean temperature shifted **-1.66 °C lower** (29.17 °C test vs 30.83 °C train) and inter-reading intervals doubled (mean 944.3 s test vs 479.1 s train).
Because the Isolation Forest learned density contours exclusively on the earlier training period, the substantial upward temperature shift and doubled sampling gaps in the test period caused many unperturbed test readings to fall into low-density regions of the training feature space, contributing directly as an additional factor to the elevated false positive rate.

---

## 2026-09-17 — D6: Chronological train/test split (Milestone 3)

**Decision:** A strict chronological train/test split is applied across both series using `cutoff_ts = date_min + TRAIN_FRACTION * (date_max - date_min)` with `TRAIN_FRACTION = 0.7` (named constant in `src/config.py`). The exact same cutoff timestamp (`2018-10-29 11:10:48`) is applied to both Out and In series. Isolation Forest models are fit exclusively on train-split rows (`ts < cutoff_ts`). Injections are categorized into three mutually exclusive subsets:
- **train-side**: injection `end_ts < cutoff_ts` (24 injections)
- **test-side**: injection `start_ts >= cutoff_ts` (6 injections)
- **straddling**: start before and end on/after `cutoff_ts` (0 injections)
Only test-side injections are evaluated for EWS lead times; train-side and straddling injections are explicitly logged in `injection_train_test_status.csv` and `if_evaluation.csv` with their status, never silently omitted.

**Rationale:** Random shuffling or k-fold cross-validation creates severe temporal data leakage in time-series anomaly detection. Training on historical telemetry and testing on unseen future telemetry mirrors actual operational deployment. Requiring the entire injection window to fall strictly after `cutoff_ts` prevents partial-overlap contamination during test evaluation.

**Limitation:** The strict chronological partition restricts test-side lead-time evaluation to 6 injections (1 Out step, 1 Out drift, 2 Out flatlines, 1 In step, 1 In drift). While statistically constrained in sample size, this ensures rigorous, zero-leakage evaluation.

---

## 2026-09-17 — D5: Recomputing rolling features from temp_injected (Milestone 3)

**Decision:** For the Isolation Forest feature set, `rolling_mean` and `rolling_std` are **recomputed dynamically from `temp_injected`** (`ROLLING_WINDOW = 10` consecutive observations). The stale pre-injection columns `rolling_mean` and `rolling_std` in `out_labeled.csv` and `in_labeled.csv` (which were derived from clean `temp` during preprocessing) are strictly NOT reused. `gap_seconds` is retained as-is (timestamp-only). `in_out_diff` is out of scope for Milestone 3's feature set.

**Rationale:** In a real-time digital twin or streaming EWS, features are derived from the observed sensor signal, which includes disturbances. Computing rolling features from `temp_injected` allows the detector to observe rolling variance spikes and mean shifts caused by disruptions. Reusing pre-injection rolling features would leak unperturbed clean history into the anomaly window, artificially muting anomaly scores. `gap_seconds` is invariant to temperature values and requires no recomputation.

**Limitation:** `in_out_diff` requires cross-series nearest-neighbor recomputation across both perturbed series (`temp_injected`), which is deferred to avoid cross-series recompute complexity in Milestone 3. This is noted as a feature limitation, not a gap to silently fill.

---

## 2026-09-17 — D4: Baseline alarm and irreversibility definitions (Milestone 2)

**Decision:** The naive baseline alarm fires on the **first single reading** where
`temp_injected > threshold` (no sustained-duration requirement). The threshold is
`per-series mean + K_SIGMA × std` (K_SIGMA = 2, a conventional heuristic).
"Irreversibility" is defined as the threshold being **continuously exceeded for
≥ D_IRREV_MINUTES** (default: 10 minutes). Both are labelled as proxy constructs.

**Rationale:** A single-threshold alarm is the simplest interpretable baseline for
an EWS; it provides a reference against which Isolation Forest and LSTM-Autoencoder
(later milestones) can be benchmarked. The 2-sigma threshold is a standard
conventional default. D_IRREV_MINUTES = 10 is an arbitrary round number chosen to
exercise the evaluation code on this proxy dataset — it has **no basis in real food
spoilage kinetics** and is explicitly not presented as a regulatory limit.

**Limitation:** The baseline alarm is deliberately naive (single-reading, no
context). It will produce false positives if the real temperature happens to be
near the threshold, and will miss flatline anomalies whose frozen value is below
threshold. The irreversibility construct is a proxy label, not a validated
food-safety criterion.

**⚠ Fix note (2026-09-17 — supersedes the original unbounded implementation):**
The original implementation used `post_onset = df_lbl.iloc[start_idx:]`, which
searched to the **end of the entire series**. This caused `baseline_alarm_timestamp`
and `irreversibility_timestamp` to latch onto unrelated real temperature excursions
occurring hours or days after the injected window ended, producing inflated
mean lead times (~3,709 min step, ~2,094 min drift) that did not reflect the
injected event's actual detectability. This was a bug, not a design choice.

**Fix applied:** Search is now bounded to
`[onset_ts, injection_end_ts + SEARCH_HORIZON_MINUTES]`.
Any alarm or irreversibility not found within this window is null.

- `SEARCH_HORIZON_MINUTES = 60` — **ARBITRARY DOCUMENTED DEFAULT**; sized to let
  a 10-min sustained exceedance criterion resolve shortly after a short-lived
  injection ends, without reaching into unrelated future real data.
  Not derived from cold-chain data.

**Updated results (bounded):** null alarm=14/30, null irrev=21/30. The increased
null count is the honest result under an honest search scope — not a failure to
suppress. It correctly surfaces that a naive threshold alarm (with bounded horizon)
fails on most flatlines and many drift/step injections whose base temperature is
below threshold, and on injections where the D_IRREV_MINUTES sustained criterion
cannot be met within the 60-min post-window.

---

## 2026-09-17 — D3: Anomaly injection protocol (Milestone 2)

**Decision:** Synthetic anomalies are injected as additive perturbations onto a
**copy** of the clean feature DataFrames. Three types are used: **step** (spike,
held then reverts), **drift** (linear ramp to a final offset), and **flatline**
(freeze the last real value). An audit log (`injection_log.csv`) records every
injection's parameters. Clean reference files (`out_features.csv`,
`in_features.csv`) are never overwritten.

**Rationale:** Keeping injection on a copy and maintaining a separate audit log
ensures reproducibility and makes it impossible for synthetic values to silently
contaminate the baseline statistics. Three types cover qualitatively different
anomaly shapes relevant to sensor failure and cold-chain breach scenarios.

**Limitation:** Injection parameters (duration 5–30 readings, step magnitude
5–15 °C, drift final magnitude 5–20 °C) are **arbitrary proxy defaults** — they are
not derived from real cold-chain equipment failure modes or food-safety literature.
The injected anomalies should not be described as realistic cold-chain events.

---

## 2026-09-17 — D2: Out and In series treated as independent (Milestone 2)

**Decision:** The `"Out"` and `"In"` sensor tags are treated as **two independent
time series** throughout Milestone 2. `gap_seconds` is computed within each series
(time since the previous reading of the *same* tag) — not the global inter-row gap
computed in Milestone 1's EDA. Cross-series proximity is captured as a separate
`in_out_diff` feature via `merge_asof` (nearest-neighbor, capped at 15 minutes).

**Rationale:** Interleaving Out and In into a single sequence would conflate two
physically distinct signals and produce misleading gap statistics. Treating them
independently preserves each series' temporal structure and avoids spurious
zero-gap artefacts (which arose in M1's global analysis because Out/In readings
are logged at the same minute). The `merge_asof` cap prevents false "nearby"
matches across long outage gaps.

**Limitation:** With a single room (`room_id/id = "Room Admin"`) and only one Out
and one In channel, there is no genuine multi-sensor topology to exploit. The
independent-series treatment is formally correct but adds less value than it would
in a real cold-chain dataset with multiple cargo sensors.

---

## 2026-09-17 — D1: No resampling to a fixed time grid (Milestone 2)

**Decision:** The dataset is **never resampled to a fixed time grid** at any point
in this project. All features (rolling mean, rolling std) are computed over a fixed
**count** of consecutive real readings (`ROLLING_WINDOW = 10`), not over a fixed
time span. Fixed-size model inputs in later milestones will use a fixed count of
consecutive real readings, not a fixed time span. No temperature values are
interpolated or synthetically infilled.

**Rationale:** Resampling would require inventing temperature values between
observed readings (interpolation) — this is explicitly prohibited for a proxy
dataset where the inter-reading gaps are themselves a structurally important signal
(CoV = 46.23; max gap = 277.6 hours). Count-based windows are model-agnostic and
preserve the actual observation times.

**Limitation:** Count-based rolling features treat a 1-second gap and a 4-hour gap
between consecutive readings identically. Later milestones must decide whether to
include `gap_seconds` as an explicit model feature to compensate for this.

---

## 2026-09-17 — Dataset selection

**Decision:** `atulanandjha/temperature-readings-iot-devices` (Kaggle) is used
as the structural proxy for cold-chain telemetry throughout Milestone 1.

**Rationale:** This dataset was selected at the project synopsis stage
(*not* a new decision made during implementation). It is a generic IoT
temperature sensor log, not real refrigerated-transport data. It was chosen
solely because it exhibits the structural properties — irregular sampling
intervals and an in/out room sensor tag — that allow the ingestion pipeline
and anomaly-detection scaffolding to be developed before real cold-chain data
is available.

**Limitation:** Any statistics derived from this dataset (sampling intervals,
temperature distributions, row counts) describe the proxy dataset, *not*
operational cold-chain telemetry. All downstream modules must carry this
caveat explicitly.

---
