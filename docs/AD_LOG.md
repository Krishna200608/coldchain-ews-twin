# Architecture Decision Log — Cold Chain EWS Digital Twin

All significant design/data decisions for this project are recorded here in
reverse-chronological order. Each entry states *what* was decided and *why*.

## 2026-09-19 — D26: Dual reporting structure — scientific benchmark vs. deployment demo (Milestone 5b)

**Decision:** Live streaming anomaly detection is executed and reported for all 30 synthetic injections across the entire 133-day replay stream. However, reporting strictly segregates results into two distinct evaluation categories:
1. **Test-side injections (6 events):** The ONLY scientifically valid, out-of-sample benchmark (matching M3 and M4b). Models had zero exposure to this period during training.
2. **Train-side injections (24 events):** Strictly labeled as "deployment demonstration only" (demo-only). Because models were fit on the training period, live alarms triggered on these rows demonstrate streaming pipeline throughput, memory buffer maintenance, and real-time execution mechanics, but carry NO validity as detection performance claims. Train-side results are never merged into out-of-sample accuracy or lead-time metrics.

**Rationale:** In an operational deployment, a digital twin monitors an ongoing stream indefinitely without knowledge of historical train/test partitions. Running detection across the entire replay demonstrates the twin's end-to-end viability. However, claiming performance on data used to fit the models would constitute gross methodological circularity. Explicitly bifurcating the report upholds rigorous academic and scientific standards.

**Limitation:** Test-side sample size remains constrained to 6 injections (1 Out step, 1 Out drift, 2 Out flatlines, 1 In step, 1 In drift) due to the strict chronological partition (D6).

---

## 2026-09-19 — D25: Pre-flight model regeneration gate and exact batch verification (Milestone 5b)

**Decision:** Before integrating anomaly detectors into the digital twin, `models/isolation_forest_{out,in}.joblib` were regenerated fresh from source (`src/isolation_forest_model.py`) using `.venv`. A strict pre-flight verification gate was executed: the regenerated models were evaluated against `data/processed/if_evaluation.csv` (M3 baseline). An exact, bit-for-bit reproduction of all alarm timestamps and lead times across the 6 test-side injections was required before proceeding to twin integration.

**Rationale:** Model artifacts (`*.joblib`) are excluded from version control under `.gitignore` to prevent repository bloat. Ensuring that fresh execution of the frozen training pipeline deterministically reproduces historical metrics guarantees that any observed discrepancy in the digital twin stems from streaming architecture differences rather than silent model drift or dependency discrepancies.

**Limitation:** Regeneration relies on the fixed random seed (`IF_RANDOM_STATE = 42`) and scikit-learn deterministic tree construction. Scikit-learn version differences across environments could theoretically alter tree split thresholds if dependencies are unpinned.

---

## 2026-09-19 — D24: Whole-series baseline threshold vs. train-only ML thresholds (Milestone 5b)

**Decision:** The live `BaselineMonitor` recomputes Milestone 2's naive threshold (`threshold = mean + K_SIGMA * std`, with `K_SIGMA = 2.0`) dynamically at startup from the clean feature files (`out_features.csv`, `in_features.csv`) across the entire historical series, without an artificial train/test partition (since M2 predated the M3 split). In contrast, Isolation Forest and LSTM-Autoencoder thresholds are calibrated strictly on training-split data (`ts < cutoff_ts`). These two thresholding strategies are explicitly documented as fundamentally distinct operational regimes and are not presented as equivalent statistical baselines.

**Rationale:** Milestone 2 had no saved threshold artifact on disk. Recomputing the threshold directly from the uncontaminated feature files preserves exact fidelity to M2's original experimental protocol. Acknowledging the whole-series nature of the baseline prevents false equivalence with the out-of-sample machine learning models.

**Limitation:** Whole-series thresholding incorporates global mean and variance across the full dataset span, creating lookahead knowledge for the naive baseline that the train-only ML models did not possess.

---

## 2026-09-19 — D23: Continuous monitor buffer accumulation without boundary resets (Milestone 5b)

**Decision:** In the live digital twin, detector memory buffers (`deque(maxlen=10)` for IF rolling statistics; `deque(maxlen=30)` for LSTM input windows) accumulate **continuously across the entire telemetry replay** (`train_train` → `val` → `test`). Monitor buffers are NEVER reset or purged at evaluation split boundaries. Live scoring begins as soon as the first window fills (row 1 for IF; row 29 for LSTM) and runs unbroken through the end of the stream.

**Audit of M4b Blind-Spot Impact:** In Milestone 4b batch evaluation, carving regions strictly caused the first 29 rows of the test split to be excluded as NaN blind spots (D16). Under live continuous buffering (D23), these first 29 test rows have valid sliding-window context and receive real anomaly scores. We performed an empirical audit to determine if this discrepancy affected any test-side injections:
- Out test cutoff: `2018-10-29 11:10:48`. First 29 test rows span `2018-10-30 00:21:00` to `2018-10-30 01:55:00`. Earliest test injection (`out_drift_009`) onset is `2018-10-30 01:59:00` (4 minutes *after* the initial 29 rows).
- In test cutoff: `2018-10-29 11:10:48`. First 29 test rows span `2018-10-30 01:50:00` to `2018-10-30 05:28:00`. Earliest test injection (`in_drift_023`) onset is `2018-11-02 07:41:00` (days after the initial 29 rows).
- **Result:** Exactly 0 of the 6 test-side injections fall within the initial 29-row transition window. Live alarm timestamps match batch evaluation 100% identically across all test injections.

**Rationale:** A production digital twin monitoring live industrial sensor streams has no knowledge of offline academic train/val/test splits. Resetting rolling buffers at arbitrary timestamps would artificially introduce cold-start latency spikes and blind spots into operational monitoring.

**Limitation:** Continuous buffering across the train/test boundary means the first 29 test predictions utilize inputs from the tail of the training period as historical context. However, because these inputs reflect observed past reality rather than future test data, this preserves strict causal time directionality ($t - k \rightarrow t$).

---

## 2026-09-18 — D19: TRANSIT_LATENCY_SECONDS = 0.0 pass-through delay (Milestone 5a)

**Decision:** A named constant `TRANSIT_LATENCY_SECONDS = 0.0` is added to `src/config.py`. In `src/digital_twin.py`, the `transit_process` applies `yield env.timeout(TRANSIT_LATENCY_SECONDS)` to every emitted reading event. With latency set to 0.0 s (disabled by default), the stage acts as a transparent pass-through pipe connecting Source to Destination.

**Rationale:** Maintaining a dedicated Transit process models realistic data transmission and processing delay while providing an architectural hook for future network latency stress-testing. Keeping it set to 0.0 s ensures that virtual arrival time (`sim_time_received`) matches elapsed dataset time (`delta_real`) exactly, enabling zero-discrepancy cross-checks against batch evaluation results from M3 and M4b in Milestone 5b.

**Limitation:** Setting `TRANSIT_LATENCY_SECONDS = 0.0` assumes idealized instantaneous packet transmission and processing. Any nonzero delay in future experiments will shift event arrival times and alarm timestamps relative to the raw sensor timestamps, requiring separate validation.

---

## 2026-09-18 — D18: Event-driven virtual clock advancement via real inter-arrival gaps (Milestone 5a)

**Decision:** SimPy's virtual simulation clock (`env.now`) advances exclusively using real inter-arrival gaps (`gap_seconds`, computed causally in M2), via `yield env.timeout(gap)`. No wall-clock pacing, `time.sleep()`, or fixed regular tick rates are used. Out and In series execute as independent, decoupled SimPy processes. Replay feeds `temp_injected` (the "as-observed" stream per D5) into the pipeline, never the clean `temp` column.

**Rationale:** The physical IoT telemetry exhibits extreme irregular sampling (sampling intervals range from 0 s to >11 days across outages, CoV = 46.23). An event-driven virtual clock faithfully reproduces the real-world temporal dynamics of sensor arrivals while allowing 133 days of telemetry (97,603 readings across both series) to simulate in ~6 seconds of wall-clock time. Using `temp_injected` ensures the digital twin monitors what an operational sensor would actually report.

**Limitation:** Virtual time progression does not reflect real-time processing bottlenecks or compute latency of downstream anomaly detection models (which will be benchmarked separately in M5b).

---

## 2026-09-18 — D17: 3-stage data-pipeline topology (Source → Transit → Destination) with no spatial topology (Milestone 5a)

**Decision:** The digital twin architecture is structured as a 3-stage data pipeline: `Source` (sensor reading generation / emission), `Transit` (network transmission / processing latency), and `Destination` (monitoring / logging layer, where anomaly detection will reside in M5b). This structure models the computational telemetry pipeline, NOT a physical multi-location refrigerated supply chain route.

**Rationale:** Separating generation, transmission, and monitoring into discrete SimPy processes follows standard discrete-event simulation design principles, enabling clean decoupling of concerns, modular testing, and independent latency modeling.

**Limitation:** **No Real Spatial Topology Caveat:** The underlying dataset (`IOT-temp.csv`) contains no geographic routing, vehicle GPS coordinates, or multi-location facility transitions. The `room_id/id` column is a single invariant constant ("Room Admin") across all 97,605 rows (confirmed in Milestone 1 EDA). Therefore, the 3-stage structure must NOT be interpreted as physical cold-chain transit (e.g., warehouse → refrigerated truck → retail display). It is strictly a software telemetry ingestion and monitoring pipeline abstraction.

---

## 2026-09-18 — D16: Causal single-window-per-row scoring for all alarm computations (Milestone 4b)

**Decision:** For every row `i` in a given split-region (train_train, val, or test), exactly one window is constructed: the `LSTM_WINDOW_LENGTH = 30` contiguous rows ending at row `i` (i.e., rows `[i−29, i]`). All 30 rows in the window must come from the **same split-region** — there is strictly no reaching back across region boundaries (train_train ↔ val ↔ test). Normalization uses the **saved train-only statistics** from `lstm_norm_stats_{out,in}.json`; normalization is never recomputed. The reconstruction score for row `i` is the MSE between the model's reconstructed output and the actual normalized input **at the window's last timestep only** (timestep index −1). Rows without 29 full preceding same-region rows receive `score = NaN`; these blind-spot rows are **never filled in** by interpolation, the nearest valid score, or any other estimate. Blind-spot counts are reported explicitly per series and split.

**Rationale:** Single-window-per-row scoring is the only causal formulation for producing a per-row alarm flag. Using the last timestep MSE focuses the score on the current observation, making the reconstruction error interpretable as a signal for that specific reading rather than an average of historical accuracy. Cross-region boundary prohibition prevents test data from influencing the window features of the train period (or vice versa), maintaining strict chronological integrity. Saving normalization statistics from M4a and reusing them here ensures the M4b scoring pipeline is completely frozen — there are no ways for test distribution information to leak into feature scaling.

**Limitation:** Each split-region independently loses its first 29 rows to the blind spot (LSTM_WINDOW_LENGTH − 1 = 29). For test-period evaluation, 29 rows are excluded per series (Out: 29/13,372 = 0.22%; In: 29/3,767 = 0.77%). All 6 test-side injections were verified to have zero blind-spot rows within their evaluation windows `[onset_ts, injection_end_ts + SEARCH_HORIZON_MINUTES]`. The last-timestep MSE discards reconstruction accuracy at earlier positions in the window; this makes the score noisier than a full-window MSE average, but preserves causal point-in-time interpretability.

---

## 2026-09-18 — D15: Trained LSTM weights committed to repository (Milestone 4b, retroactive documentation of M4a decision)

**Decision:** The trained model weight files `models/lstm_out.h5` and `models/lstm_in.h5` are committed and tracked in the GitHub repository (`main` branch), despite their binary format (~193 KB each). They are explicitly NOT added to `.gitignore`. The `.gitignore` rule for `models/*.joblib` (Isolation Forest pickles) is retained separately, as Isolation Forest models can be trivially re-trained from source (deterministic, seconds), whereas LSTM model weights require a Colab GPU session to reproduce.

**Rationale:** Committing the H5 weights provides reproducibility and auditability: any reviewer can pull the repository and run LSTM inference immediately without triggering a GPU training session. The files are small enough (~193 KB each) that HTTPS push/pull succeeds instantly and does not burden the repository. The alternative (`.gitignore`-ing and requiring re-training) would prevent Milestone 4b CPU inference from working out-of-the-box on a fresh clone.

**Limitation:** `.h5` (HDF5 legacy format) is considered legacy by TensorFlow ≥ 2.12 (Keras 3 recommends `.keras` format). The Colab training notebook records the resulting `UserWarning` from `model.save()`. The weights remain usable for inference with `tf.keras.models.load_model(..., compile=False)`.

---

## 2026-09-18 — D14: Non-causal aggregation scope — calibration only (Milestone 4b)

**Decision:** Window-level score aggregation (collecting causal per-row scores across the full `train_train + val` region into a single distribution) is used **exclusively** for computing the D13 threshold parameter — an offline, retrospective step that does not produce any `alarm_timestamp`. Any computation that produces an `alarm_timestamp` (the first row within a bounded search window where `lstm_anomaly = True`) is derived solely from the **causal per-row scores** defined in D16 and the threshold defined in D13. No future-looking aggregation, sliding-window average of scores, or smoothed alarm signal is used anywhere in the alarm pipeline.

**Rationale:** In a deployed real-time EWS, only historical data is available when an alarm fires. Non-causal score aggregation (e.g., computing a centered moving average of reconstruction errors) would use future readings to smooth the score at a given timestamp — this is inadmissible for a live system. Restricting non-causal operations to offline calibration keeps the `alarm_timestamp` definition operationally valid and avoids artificial lead-time inflation.

**Limitation:** The D13 calibration threshold is a global constant per series (not adaptive to local score dynamics). If the reconstruction error distribution drifts over the test period (e.g., due to seasonal shifts documented in D7's distributional drift addendum), a fixed threshold computed on `train_train + val` may become either too permissive or too conservative in later test windows.

---

## 2026-09-18 — D13: LSTM anomaly threshold — train-only causal score mean + K_SIGMA × std (Milestone 4b)

**Decision:** The per-series anomaly threshold is defined as: `threshold = mean(valid train scores) + K_SIGMA × std(valid train scores)`, where `K_SIGMA = 2.0` (shared constant from `config.py`, consistent with the M2 baseline alarm — `D4`). "Valid train scores" refers to all non-NaN causal per-row scores (D16) computed on the `train_train + val` split. NaN (blind-spot) rows are excluded from the mean and std calculation. The threshold is computed **exclusively from training-period data** — the test split is never observed or used in any way during threshold computation. The threshold is **not** tuned to match the known injected-anomaly fraction in the test set.

**Computed values:**
- Series Out: threshold = **1.0101** (mean=0.1391, std=0.4355, n_valid=63,829)
- Series In:  threshold = **1.5128** (mean=0.2698, std=0.6215, n_valid=16,519)

**Rationale:** The 2-sigma convention is a standard heuristic for identifying statistically unusual events in a unimodal distribution. Using train-only scores maintains causal integrity: no future anomaly information contaminates the decision boundary. Reusing `K_SIGMA = 2.0` from D4 ensures the LSTM threshold is defined on the same statistical basis as the naive baseline, making the lead-time comparison meaningful.

**Limitation:** The train-period LSTM reconstruction error distribution is right-skewed (both series have std >> mean, suggesting extreme outliers in the training period drive the threshold upward). The 2-sigma threshold (`~1.01` for Out, `~1.51` for In) is consequently high relative to most test anomaly scores, producing low recall and low precision on the Out series. The threshold was intentionally left at K_SIGMA=2.0 — not tuned to the known injection fraction — as tuning would leak ground-truth test labels into the decision boundary.

---


## 2026-09-17 — D12: LSTM-Autoencoder architecture and training protocol (Milestone 4a)

**Decision:** The sequential reconstruction architecture is defined in Keras/TensorFlow as:

`Encoder LSTM(32 units)` → bottleneck (last hidden state) → `RepeatVector(LSTM_WINDOW_LENGTH = 30)` → `Decoder LSTM(32 units, return_sequences=True)` → `TimeDistributed(Dense(2))` (reconstructing normalized `temp_injected` and `log_gap_seconds`). Training is configured with the Adam optimizer, MSE loss, `batch_size = 256`, up to 50 epochs, and early stopping on validation loss (`patience = 5`, restoring best weights). Models are trained independently per series (`lstm_out.h5`, `lstm_in.h5`).

**Rationale:** An LSTM autoencoder captures sequential dependencies and temporal autocorrelation across time that classical models (like Isolation Forest) cannot model. Learning to reconstruct normal multi-step thermal patterns allows the model to detect anomalies via reconstruction error spikes, providing sensitivity to subtle sequential disruptions.

**Limitation:** The architecture and hyperparameters (32 hidden units, MSE loss, batch size 256) are defined on standard theoretical heuristics and remain **completely unvalidated** until the student executes the authored notebook on a Google Colab T4 GPU session.

---

## 2026-09-17 — D11: Chronological validation split from train tail (Milestone 4a)

**Decision:** A validation set is carved chronologically from the tail of the historical training split: `LSTM_VAL_FRACTION = 0.1` (named constant in `src/config.py`). `train_train` consists of the earliest 90% of train-period rows by time, while `val` consists of the latest 10% of train-period rows. Test-period rows (`ts >= cutoff_ts`) remain strictly untouched and separate in this milestone. Sliding windows are constructed strictly within `train_train` and `val` respectively, with zero boundary crossing.

**Rationale:** Standard random validation splitting in time series causes severe lookahead data leakage. Carving validation chronologically from the end of the training horizon provides early stopping on realistic forward-in-time forecasting, matching operational deployment.

**Limitation:** Carving 10% of train rows from the tail slightly reduces the volume of primary training windows (`train_train`: 11,494 windows for Out, 2,978 for In) and introduces local seasonal variance between `train_train` and `val`.

---

## 2026-09-17 — D10: Bivariate feature set and train-only normalization (Milestone 4a)

**Decision:** The LSTM input vector per timestep is bivariate: `[temp_injected, log1p(gap_seconds)]`. Normalization parameters (mean and standard deviation) are computed exclusively on the full historical training split (`train_train + val`), saved to `data/processed/lstm_norm_stats_{out,in}.json`, and applied to z-score `train_train` and `val` windows. Test telemetry is strictly excluded from normalization statistics.

**Rationale:** Real telemetry in this dataset exhibits strong sampling irregularity (CoV = 46.23). Applying a monotonic `log1p` transform compresses extreme outage intervals while preserving temporal gaps as an explicit feature. Restricting normalization statistics to the training partition prevents test-set distribution leakage into feature scaling.

**Limitation:** Only temperature and sampling gap are modeled. Cross-series interactions (`in_out_diff`) and external covariates (ambient weather) are not included.

---

## 2026-09-17 — D9: Count-based sliding windows for sequential modeling (Milestone 4a)

**Decision:** Windows are constructed over a fixed count of consecutive real observations per D1: `LSTM_WINDOW_LENGTH = 30` readings with `LSTM_WINDOW_STRIDE = 5` readings (named constants in `src/config.py`). Windows are extracted independently per series (Out and In, per D2). No time-grid resampling or synthetic interpolation is performed.

**Rationale:** Resampling irregular time series introduces artificial interpolated temperatures, violating D1. Count-based windows respect observed sensor arrivals. A stride of 5 balances sequence redundancy against computational efficiency and sample diversity.

**Limitation:** Because sampling intervals vary, a 30-reading window covers varying physical elapsed times (from minutes during rapid logging to hours across outage periods).

---

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
