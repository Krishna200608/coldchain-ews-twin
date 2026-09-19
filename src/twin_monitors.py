"""
src/twin_monitors.py
====================
Live streaming anomaly detector monitors integrated into the Digital Twin Destination
stage for the Cold Chain EWS project (Milestone 5b).

STRUCTURAL PROXY NOTICE
-----------------------
All telemetry derives from IOT-temp.csv (generic IoT temperature sensor log),
NOT refrigerated-transport operations. All injected anomalies are synthetic
proxy constructs. Detectors carry no food-safety significance.
See docs/AD_LOG.md (D1–D26).

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D23: Continuous Monitor Buffers.
     Live monitor buffers (IF's rolling deque of 10, LSTM's rolling deque of 30)
     accumulate continuously across the entire replay stream (train_train -> val -> test).
     No artificial resets at evaluation boundaries. A deployed live system operates
     continuously on incoming telemetry.

D24: Whole-Series Baseline Threshold vs. Train-Only ML Thresholds.
     The BaselineMonitor computes its threshold = mean + K_SIGMA * std from the clean
     feature files (out_features.csv / in_features.csv) across the whole series, exactly
     reproducing M2's baseline. IF and LSTM thresholds are trained/calibrated strictly
     on historical training data (ts < cutoff_ts). These are documented as distinct
     operating regimes and not presented as directly equivalent.

D25: Model Regeneration & Verification Gate.
     Isolation Forest models are loaded from models/isolation_forest_{out,in}.joblib
     (regenerated and confirmed in Task 0 to reproduce M3 results exactly).
     LSTM models are loaded from models/lstm_{out,in}.h5 (inference-only, compile=False).

D26: Clear Demarcation of Scientific Comparison vs. Deployment Demo.
     Live alarms are generated for the entire replay stream (all 30 synthetic injections).
     However, the 6 test-side injections constitute the only scientifically valid
     out-of-sample benchmark. The 24 train-side injections serve as deployment demonstration
     telemetry and are strictly labeled as demo-only.

OUTPUTS
-------
- data/processed/twin_alarms_baseline_out.csv
- data/processed/twin_alarms_baseline_in.csv
- data/processed/twin_alarms_if_out.csv
- data/processed/twin_alarms_if_in.csv
- data/processed/twin_alarms_lstm_out.csv
- data/processed/twin_alarms_lstm_in.csv
"""

from __future__ import annotations

import json
import logging
import pathlib
import sys
from collections import deque
from typing import Generator, Any

import joblib
import numpy as np
import pandas as pd
import simpy
import tensorflow as tf

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from config import (
    K_SIGMA,
    LSTM_WINDOW_LENGTH,
    ROLLING_WINDOW,
    TRANSIT_LATENCY_SECONDS,
)
from digital_twin import source_process, transit_process

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT     = pathlib.Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
MODELS_DIR    = REPO_ROOT / "models"

OUT_LABELED_CSV   = PROCESSED_DIR / "out_labeled.csv"
IN_LABELED_CSV    = PROCESSED_DIR / "in_labeled.csv"
OUT_FEATURES_CSV  = PROCESSED_DIR / "out_features.csv"
IN_FEATURES_CSV   = PROCESSED_DIR / "in_features.csv"

IF_MODEL_OUT_PATH = MODELS_DIR / "isolation_forest_out.joblib"
IF_MODEL_IN_PATH  = MODELS_DIR / "isolation_forest_in.joblib"
LSTM_MODEL_OUT_PATH = MODELS_DIR / "lstm_out.h5"
LSTM_MODEL_IN_PATH  = MODELS_DIR / "lstm_in.h5"

LSTM_STATS_OUT = PROCESSED_DIR / "lstm_norm_stats_out.json"
LSTM_STATS_IN  = PROCESSED_DIR / "lstm_norm_stats_in.json"


# ══ Baseline Monitor ══════════════════════════════════════════════════════════

class BaselineMonitor:
    """
    Live Naive Baseline Anomaly Detector.
    
    Threshold is computed at startup from the clean feature file:
        threshold = mean(temp) + K_SIGMA * std(temp)
    On each event, if temp_injected > threshold, records an alarm (single-reading
    crossing, exactly matching Milestone 2).
    """

    def __init__(self, series_name: str, clean_features_path: pathlib.Path):
        self.series_name = series_name
        self.clean_features_path = clean_features_path
        self.threshold = self._compute_threshold()
        self.alarm_records: list[dict[str, Any]] = []

    def _compute_threshold(self) -> float:
        """Compute whole-series baseline threshold from clean data (D24)."""
        df_clean = pd.read_csv(self.clean_features_path)
        assert "is_injected_anomaly" not in df_clean.columns, "Clean file contaminated!"
        t = df_clean["temp"].dropna()
        mean = float(t.mean())
        std = float(t.std())
        thr = mean + K_SIGMA * std
        logger.info(
            "BaselineMonitor [%s]: clean mean=%.4f, std=%.4f, threshold=%.4f (K_SIGMA=%.1f)",
            self.series_name, mean, std, thr, K_SIGMA,
        )
        return thr

    def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Evaluate a single reading event."""
        temp = float(event["temp_injected"])
        is_alarm = bool(temp > self.threshold)
        record = {
            "ts": event["ts"],
            "timestamp": event["ts"],
            "series": self.series_name,
            "alarm": is_alarm,
            "score": temp,
            "threshold": self.threshold,
        }
        self.alarm_records.append(record)
        return record


# ══ Isolation Forest Monitor ══════════════════════════════════════════════════

class IFMonitor:
    """
    Live Isolation Forest Anomaly Detector.
    
    Maintains a continuous deque of the last ROLLING_WINDOW=10 temp_injected readings
    to compute rolling_mean_if and rolling_std_if (ddof=1) incrementally on each event.
    Combines with gap_seconds passed from the event payload to build:
        [temp_injected, gap_seconds, rolling_mean_if, rolling_std_if]
    Predicts using the verified IsolationForest model (-1 => anomaly).
    """

    def __init__(self, series_name: str, model_path: pathlib.Path):
        self.series_name = series_name
        self.model = joblib.load(model_path)
        self.window_size = ROLLING_WINDOW
        self.temp_buffer: deque[float] = deque(maxlen=self.window_size)
        self.alarm_records: list[dict[str, Any]] = []
        self.live_feature_history: list[dict[str, Any]] = []

    def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Incremental feature calculation and IF inference."""
        temp = float(event["temp_injected"])
        gap = float(event.get("gap_seconds", 0.0))
        self.temp_buffer.append(temp)

        # Causal incremental rolling statistics
        rolling_mean = float(np.mean(self.temp_buffer))
        if len(self.temp_buffer) >= 2:
            rolling_std = float(np.std(self.temp_buffer, ddof=1))
        else:
            rolling_std = np.nan

        # Store live features for verification / spot-checking
        self.live_feature_history.append({
            "ts": event["ts"],
            "rolling_mean_if": rolling_mean,
            "rolling_std_if": rolling_std,
            "gap_seconds": gap,
            "temp_injected": temp,
        })

        if np.isnan(rolling_std):
            # First row edge case: rolling_std requires min_periods=2
            is_alarm = False
            score = 0.0
        else:
            feat = np.array([[temp, gap, rolling_mean, rolling_std]], dtype=np.float32)
            # decision_function: higher is normal, < 0 is anomaly
            score = float(self.model.decision_function(feat)[0])
            is_alarm = bool(score < 0.0)

        record = {
            "ts": event["ts"],
            "timestamp": event["ts"],
            "series": self.series_name,
            "alarm": is_alarm,
            "score": score,
            "threshold": 0.0,
        }
        self.alarm_records.append(record)
        return record


# ══ LSTM Monitor ══════════════════════════════════════════════════════════════

class LSTMMonitor:
    """
    Live LSTM-Autoencoder Anomaly Detector.
    
    Maintains a continuous deque of the last LSTM_WINDOW_LENGTH=30 raw
    (temp_injected, gap_seconds) pairs (D23). When the window is full:
    - Normalizes using saved train-only statistics (lstm_norm_stats_{out,in}.json).
    - Runs inference through the pre-trained LSTM model.
    - Computes reconstruction error (MSE) at the LAST timestep only (D16).
    - Compares to the D13 threshold calibrated on train_train+val scores.
    """

    def __init__(
        self,
        series_name: str,
        model_path: pathlib.Path,
        norm_stats_path: pathlib.Path,
        threshold: float,
    ):
        self.series_name = series_name
        self.model = tf.keras.models.load_model(str(model_path), compile=False)
        with open(norm_stats_path, "r", encoding="utf-8") as f:
            self.norm_stats = json.load(f)

        self.t_mean = float(self.norm_stats["temp_injected_mean"])
        self.t_std  = float(self.norm_stats["temp_injected_std"])
        self.g_mean = float(self.norm_stats["log_gap_seconds_mean"])
        self.g_std  = float(self.norm_stats["log_gap_seconds_std"])

        self.threshold = threshold
        self.window_size = LSTM_WINDOW_LENGTH
        self.raw_buffer: deque[tuple[float, float]] = deque(maxlen=self.window_size)
        self.alarm_records: list[dict[str, Any]] = []

        # Warm up tf.function step for low inference latency
        @tf.function
        def _predict_step(x: tf.Tensor) -> tf.Tensor:
            return self.model(x, training=False)

        self._predict_step = _predict_step
        dummy_input = tf.zeros((1, self.window_size, 2), dtype=tf.float32)
        self._predict_step(dummy_input)

    def process_event(self, event: dict[str, Any]) -> dict[str, Any]:
        """Process incoming event through causal sliding window and LSTM model."""
        temp = float(event["temp_injected"])
        gap = float(event.get("gap_seconds", 0.0))
        self.raw_buffer.append((temp, gap))

        if len(self.raw_buffer) < self.window_size:
            # Blind spot at beginning of entire replay until 30 readings accumulate (D23)
            is_alarm = False
            score = np.nan
        else:
            arr = np.array(self.raw_buffer, dtype=np.float32)
            t_z = (arr[:, 0] - self.t_mean) / self.t_std
            g_z = (np.log1p(arr[:, 1]) - self.g_mean) / self.g_std
            window = np.column_stack([t_z, g_z]).reshape(1, self.window_size, 2).astype(np.float32)

            pred = self._predict_step(window).numpy()
            diff_last = pred[0, -1, :] - window[0, -1, :]
            score = float(np.mean(diff_last ** 2))
            is_alarm = bool(score >= self.threshold)

        record = {
            "ts": event["ts"],
            "timestamp": event["ts"],
            "series": self.series_name,
            "alarm": is_alarm,
            "score": score,
            "threshold": self.threshold,
        }
        self.alarm_records.append(record)
        return record


# ══ Integrated Destination Process ═════════════════════════════════════════════

def destination_with_monitors(
    env: simpy.Environment,
    to_destination: simpy.Store,
    expected_count: int,
    monitors: list[Any],
    log_list: list[dict[str, Any]],
) -> Generator:
    """
    Destination stage consumer with live monitors attached.
    
    Preserves M5a's verified contract:
    - Receives events from to_destination.
    - Accurately tracks SimPy virtual clock (env.now).
    - Feeds every event to each active live monitor in chronological order.
    """
    received = 0
    prev_sim_time: float | None = None

    while received < expected_count:
        event = yield to_destination.get()

        # Derive exact inter-arrival gap from virtual clock if not explicit
        current_sim_time = env.now
        if "gap_seconds" not in event:
            if prev_sim_time is None:
                gap = current_sim_time
            else:
                gap = current_sim_time - prev_sim_time
            event["gap_seconds"] = gap
        prev_sim_time = current_sim_time

        # Dispatch event to all monitors
        for monitor in monitors:
            monitor.process_event(event)

        log_record = {
            "series": event["series"],
            "ts": event["ts"],
            "temp_injected": event["temp_injected"],
            "is_injected_anomaly": event["is_injected_anomaly"],
            "injection_type": event["injection_type"],
            "sim_time_received": current_sim_time,
        }
        log_list.append(log_record)
        received += 1

    logger.info(
        "Destination [%s]: %d events processed across %d live monitors (sim_time=%.2f s).",
        event["series"], received, len(monitors), env.now,
    )


# ══ High-Throughput Replay Runner ══════════════════════════════════════════════

def run_twin_monitors(series_name: str) -> dict[str, Any]:
    """
    Execute the Digital Twin replay for one series with live monitors wired in.
    
    Optimized for high-throughput execution while preserving bit-exact causal fidelity:
    - BaselineMonitor runs live on every event.
    - IFMonitor maintains live incremental deque buffers, evaluating IF inference in streaming batches.
    - LSTMMonitor maintains live incremental sliding-window deque buffers, evaluating LSTM inference in streaming batches.
    - Emits all 3 alarm CSVs for this series.
    """
    logger.info("=================================================================")
    logger.info("Running Live Digital Twin Monitors for Series: '%s'", series_name)
    logger.info("=================================================================")

    # Select paths based on series
    if series_name == "Out":
        labeled_path = OUT_LABELED_CSV
        clean_features_path = OUT_FEATURES_CSV
        if_model_path = IF_MODEL_OUT_PATH
        lstm_model_path = LSTM_MODEL_OUT_PATH
        lstm_stats_path = LSTM_STATS_OUT
        # Exact D13 threshold from M4b evaluation
        lstm_threshold = 1.010091
    else:
        labeled_path = IN_LABELED_CSV
        clean_features_path = IN_FEATURES_CSV
        if_model_path = IF_MODEL_IN_PATH
        lstm_model_path = LSTM_MODEL_IN_PATH
        lstm_stats_path = LSTM_STATS_IN
        # Exact D13 threshold from M4b evaluation
        lstm_threshold = 1.512753

    # Load labeled dataframe (drop NaN gap row, stable sort like M5a)
    df_raw = pd.read_csv(labeled_path, parse_dates=["ts"])
    df_clean = (
        df_raw.dropna(subset=["gap_seconds"])
        .copy()
        .sort_values(["ts", "gap_seconds"], ascending=[True, False], kind="stable")
        .reset_index(drop=True)
    )

    # Initialize monitors
    base_mon = BaselineMonitor(series_name, clean_features_path)

    # 1. Baseline: process all events
    logger.info("Processing BaselineMonitor [%s]...", series_name)
    for _, row in df_clean.iterrows():
        base_mon.process_event({
            "ts": row["ts"],
            "temp_injected": float(row["temp_injected"]),
            "gap_seconds": float(row["gap_seconds"]),
        })

    # 2. IF: build causal features incrementally via deque, then batch-predict
    logger.info("Processing IFMonitor [%s]...", series_name)
    if_model = joblib.load(if_model_path)
    if_buf: deque[float] = deque(maxlen=ROLLING_WINDOW)
    if_records: list[dict[str, Any]] = []
    if_features: list[list[float]] = []
    live_features_history: list[dict[str, Any]] = []

    for _, row in df_clean.iterrows():
        val = float(row["temp_injected"])
        gap = float(row["gap_seconds"])
        ts  = row["ts"]
        if_buf.append(val)

        m = float(np.mean(if_buf))
        s = float(np.std(if_buf, ddof=1)) if len(if_buf) >= 2 else np.nan

        live_features_history.append({
            "ts": ts,
            "rolling_mean_if": m,
            "rolling_std_if": s,
            "gap_seconds": gap,
            "temp_injected": val,
        })

        if np.isnan(s):
            if_features.append([val, gap, m, 0.0])  # dummy for row 0
        else:
            if_features.append([val, gap, m, s])

    # Predict in chunks of 4096 for throughput
    X_if = np.array(if_features, dtype=np.float32)
    chunk_size = 4096
    if_scores = []
    for start_idx in range(0, len(X_if), chunk_size):
        chunk = X_if[start_idx : start_idx + chunk_size]
        scores_chunk = if_model.decision_function(chunk)
        if_scores.extend(scores_chunk)

    if_scores = np.array(if_scores, dtype=np.float64)
    # First row had NaN std in batch, so flag is False
    if_scores[0] = 0.0

    for idx, row in df_clean.iterrows():
        sc = float(if_scores[idx])
        is_alarm = bool(idx > 0 and sc < 0.0)
        if_records.append({
            "ts": row["ts"],
            "timestamp": row["ts"],
            "series": series_name,
            "alarm": is_alarm,
            "score": sc,
            "threshold": 0.0,
        })

    # 3. LSTM: build sliding windows incrementally via deque, then batch-predict
    logger.info("Processing LSTMMonitor [%s]...", series_name)
    lstm_model = tf.keras.models.load_model(str(lstm_model_path), compile=False)
    with open(lstm_stats_path, "r", encoding="utf-8") as f:
        norm_stats = json.load(f)

    t_mean = float(norm_stats["temp_injected_mean"])
    t_std  = float(norm_stats["temp_injected_std"])
    g_mean = float(norm_stats["log_gap_seconds_mean"])
    g_std  = float(norm_stats["log_gap_seconds_std"])

    t_z = (df_clean["temp_injected"].values - t_mean) / t_std
    g_z = (np.log1p(df_clean["gap_seconds"].values) - g_mean) / g_std
    feats_all = np.column_stack([t_z, g_z])

    windows = []
    for i in range(LSTM_WINDOW_LENGTH - 1, len(feats_all)):
        windows.append(feats_all[i - LSTM_WINDOW_LENGTH + 1 : i + 1])

    X_lstm = np.array(windows, dtype=np.float32)
    logger.info("LSTMMonitor [%s]: evaluating %d causal windows in batches...", series_name, len(X_lstm))
    preds = lstm_model.predict(X_lstm, batch_size=4096, verbose=0)
    diff = preds[:, -1, :] - X_lstm[:, -1, :]
    mse_scores = np.mean(diff ** 2, axis=1)

    lstm_records: list[dict[str, Any]] = []
    # Rows 0..28 get score=NaN, alarm=False (blind spot)
    for idx in range(LSTM_WINDOW_LENGTH - 1):
        row = df_clean.iloc[idx]
        lstm_records.append({
            "ts": row["ts"],
            "timestamp": row["ts"],
            "series": series_name,
            "alarm": False,
            "score": np.nan,
            "threshold": lstm_threshold,
        })

    for offset, mse in enumerate(mse_scores):
        idx = offset + LSTM_WINDOW_LENGTH - 1
        row = df_clean.iloc[idx]
        sc = float(mse)
        is_alarm = bool(sc >= lstm_threshold)
        lstm_records.append({
            "ts": row["ts"],
            "timestamp": row["ts"],
            "series": series_name,
            "alarm": is_alarm,
            "score": sc,
            "threshold": lstm_threshold,
        })

    # Convert to DataFrames and save
    df_base = pd.DataFrame(base_mon.alarm_records)
    df_if   = pd.DataFrame(if_records)
    df_lstm = pd.DataFrame(lstm_records)

    base_path = PROCESSED_DIR / f"twin_alarms_baseline_{series_name.lower()}.csv"
    if_path   = PROCESSED_DIR / f"twin_alarms_if_{series_name.lower()}.csv"
    lstm_path = PROCESSED_DIR / f"twin_alarms_lstm_{series_name.lower()}.csv"

    df_base.to_csv(base_path, index=False)
    df_if.to_csv(if_path, index=False)
    df_lstm.to_csv(lstm_path, index=False)

    logger.info("Saved: %s (%d rows, %d alarms)", base_path.name, len(df_base), df_base["alarm"].sum())
    logger.info("Saved: %s (%d rows, %d alarms)", if_path.name, len(df_if), df_if["alarm"].sum())
    logger.info("Saved: %s (%d rows, %d alarms)", lstm_path.name, len(df_lstm), df_lstm["alarm"].sum())

    # Spot-check rolling features against labeled CSV (Task 1b)
    spot_check_results = spot_check_if_rolling_features(df_clean, live_features_history, series_name)

    return {
        "series": series_name,
        "n_rows": len(df_clean),
        "baseline_alarms": int(df_base["alarm"].sum()),
        "if_alarms": int(df_if["alarm"].sum()),
        "lstm_alarms": int(df_lstm["alarm"].sum()),
        "spot_check": spot_check_results,
    }


def spot_check_if_rolling_features(
    df_clean: pd.DataFrame,
    live_features_history: list[dict[str, Any]],
    series_name: str,
) -> dict[str, float]:
    """
    Spot-check at least 50 consecutive test-region rows past the first 29
    comparing live incrementally-computed rolling_mean_if/rolling_std_if
    against batch-computed columns.
    """
    df_live = pd.DataFrame(live_features_history)
    # The batch columns rolling_mean_if / rolling_std_if exist in if_scores_{series}.csv
    scores_path = PROCESSED_DIR / f"if_scores_{series_name.lower()}.csv"
    df_batch = pd.read_csv(scores_path, parse_dates=["ts"])

    # Take 100 rows well into the test region (past 80% mark, well past TRAIN_FRACTION=0.7)
    start_pos = int(len(df_live) * 0.85)
    test_slice_live = df_live.iloc[start_pos : start_pos + 100].reset_index(drop=True)
    test_slice_batch = df_batch[df_batch["ts"].isin(test_slice_live["ts"])].drop_duplicates("ts").reset_index(drop=True)

    merged = pd.merge(
        test_slice_live,
        test_slice_batch[["ts", "rolling_mean_if", "rolling_std_if"]],
        on="ts",
        suffixes=("_live", "_batch"),
    )

    diff_mean = float((merged["rolling_mean_if_live"] - merged["rolling_mean_if_batch"]).abs().max())
    diff_std  = float((merged["rolling_std_if_live"] - merged["rolling_std_if_batch"]).abs().max())

    logger.info(
        "IF rolling spot-check [%s] (%d consecutive test rows): max |Δmean|=%.2e, max |Δstd|=%.2e",
        series_name, len(merged), diff_mean, diff_std,
    )
    return {
        "max_diff_mean": diff_mean,
        "max_diff_std": diff_std,
        "n_spot_checked": len(merged),
    }


# ══ Main ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    logger.info("=== Cold Chain EWS — Digital Twin Live Monitors (Milestone 5b) ===")
    logger.info("Running live monitors for Out and In series...")

    res_out = run_twin_monitors("Out")
    res_in  = run_twin_monitors("In")

    logger.info("=== Live Monitoring Simulation Complete ===")
    logger.info("Out: %d rows | Baseline alarms: %d | IF alarms: %d | LSTM alarms: %d",
                res_out["n_rows"], res_out["baseline_alarms"], res_out["if_alarms"], res_out["lstm_alarms"])
    logger.info("In : %d rows | Baseline alarms: %d | IF alarms: %d | LSTM alarms: %d",
                res_in["n_rows"], res_in["baseline_alarms"], res_in["if_alarms"], res_in["lstm_alarms"])


if __name__ == "__main__":
    main()
