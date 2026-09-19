"""
dashboard/replay_engine.py
==========================
D33 pre-warmed streaming playback loop orchestration wrapping verified
detectors from src.twin_monitors (D27).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.constants import (
    DATA_DIR,
    IF_PREWARM_STEPS,
    LSTM_PREWARM_STEPS,
    LSTM_THRESH_IN,
    LSTM_THRESH_OUT,
    MODELS_DIR,
)
from dashboard.data_loader import load_clean_stream
from src.twin_monitors import BaselineMonitor, IFMonitor, LSTMMonitor


@st.cache_data
def simulate_prewarmed_window(
    series_name: str,
    win_start_idx: int,
    win_end_idx: int,
) -> pd.DataFrame:
    """
    Simulate streaming telemetry across the visible window with D33 silent buffer pre-warming.
    Directly instantiates and executes verified detectors from src.twin_monitors (D27).
    """
    df_clean = load_clean_stream(series_name)
    clean_features_path = DATA_DIR / f"{series_name.lower()}_features.csv"
    if_model_path = MODELS_DIR / f"isolation_forest_{series_name.lower()}.joblib"
    lstm_model_path = MODELS_DIR / f"lstm_{series_name.lower()}.h5"
    lstm_stats_path = DATA_DIR / f"lstm_norm_stats_{series_name.lower()}.json"
    lstm_thresh = LSTM_THRESH_OUT if series_name == "Out" else LSTM_THRESH_IN

    # Instantiate verified monitors
    base_mon = BaselineMonitor(series_name, clean_features_path)
    if_mon = IFMonitor(series_name, if_model_path)
    lstm_mon = LSTMMonitor(series_name, lstm_model_path, lstm_stats_path, lstm_thresh)

    # D33: Pre-warm IF monitor with 10 readings prior to visible window
    prewarm_if = df_clean.iloc[max(0, win_start_idx - IF_PREWARM_STEPS) : win_start_idx]
    for _, r in prewarm_if.iterrows():
        if_mon.process_event({
            "ts": r["ts"],
            "temp_injected": float(r["temp_injected"]),
            "gap_seconds": float(r["gap_seconds"]),
        })
    if_mon.alarm_records.clear()

    # D33: Pre-warm LSTM monitor with 30 readings prior to visible window
    prewarm_lstm = df_clean.iloc[max(0, win_start_idx - LSTM_PREWARM_STEPS) : win_start_idx]
    for _, r in prewarm_lstm.iterrows():
        lstm_mon.process_event({
            "ts": r["ts"],
            "temp_injected": float(r["temp_injected"]),
            "gap_seconds": float(r["gap_seconds"]),
        })
    lstm_mon.alarm_records.clear()

    # Process visible window events sequentially
    vis_rows = df_clean.iloc[win_start_idx : win_end_idx + 1]
    window_records = []
    for _, r in vis_rows.iterrows():
        ev = {
            "ts": r["ts"],
            "temp_injected": float(r["temp_injected"]),
            "gap_seconds": float(r["gap_seconds"]),
        }
        b_rec = base_mon.process_event(ev)
        i_rec = if_mon.process_event(ev)
        l_rec = lstm_mon.process_event(ev)

        window_records.append({
            "ts": r["ts"],
            "temp_injected": float(r["temp_injected"]),
            "gap_seconds": float(r["gap_seconds"]),
            "is_injected_anomaly": bool(r.get("is_injected_anomaly", False)),
            "baseline_score": b_rec["score"],
            "baseline_alarm": b_rec["alarm"],
            "baseline_threshold": b_rec["threshold"],
            "if_score": i_rec["score"],
            "if_alarm": i_rec["alarm"],
            "if_threshold": 0.0,
            "lstm_score": l_rec["score"],
            "lstm_alarm": l_rec["alarm"],
            "lstm_threshold": lstm_thresh,
        })

    return pd.DataFrame(window_records)


def get_active_telemetry_slice(
    sim_df: pd.DataFrame,
    current_frame: int,
    onset_ts: pd.Timestamp,
    horizon_end_ts: pd.Timestamp,
) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Extract current telemetry reading, active historical slice up to playhead,
    and detector alarms within the evaluation horizon [onset_ts, horizon_end_ts].
    """
    active_slice = sim_df.iloc[: current_frame + 1]
    current_reading = sim_df.iloc[current_frame]
    eval_slice = active_slice[(active_slice["ts"] >= onset_ts) & (active_slice["ts"] <= horizon_end_ts)]
    b_fired = eval_slice[eval_slice["baseline_alarm"] == True]
    i_fired = eval_slice[eval_slice["if_alarm"] == True]
    l_fired = eval_slice[eval_slice["lstm_alarm"] == True]
    return active_slice, current_reading, eval_slice, b_fired, i_fired, l_fired
