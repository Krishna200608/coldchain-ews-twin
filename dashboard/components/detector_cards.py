"""
dashboard/components/detector_cards.py
======================================
Current telemetry status row and side-by-side detector cards (Naive Baseline,
Isolation Forest, and LSTM-Autoencoder).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.constants import (
    ICON_BASELINE,
    ICON_IF,
    ICON_LSTM,
    SEARCH_HORIZON_MINUTES,
)


def render_telemetry_metrics_row(
    curr_ts: pd.Timestamp,
    current_frame: int,
    total_frames: int,
    curr_temp: float,
    onset_ts: pd.Timestamp,
    end_ts: pd.Timestamp,
    horizon_end_ts: pd.Timestamp,
    inj_type: str,
    series: str,
    status: str,
    b_fired: pd.DataFrame,
    i_fired: pd.DataFrame,
    l_fired: pd.DataFrame,
) -> None:
    """Render top 4-metric telemetry overview bar."""
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric(
            "Replay Time",
            curr_ts.strftime("%H:%M:%S"),
            curr_ts.strftime("%Y-%m-%d"),
            delta_color="off",
            help=f"Replay Timestamp: {curr_ts} (Frame {current_frame + 1} / {total_frames})",
        )
    with col_m2:
        delta_onset = (curr_ts - onset_ts).total_seconds() / 60.0
        st.metric(
            "Live Temperature",
            f"{curr_temp:.2f} °C",
            f"{delta_onset:+.0f}m from onset",
            help=f"Sensor reading at current playhead. Offset from onset: {delta_onset:+.1f} minutes",
        )
    with col_m3:
        if onset_ts <= curr_ts <= end_ts:
            status_word = "Anomalous"
            status_help = f"Injection Active: {inj_type.upper()} ({onset_ts} to {end_ts})"
        elif end_ts < curr_ts <= horizon_end_ts:
            status_word = "Horizon"
            status_help = f"Evaluation Search Horizon Active ({SEARCH_HORIZON_MINUTES:.0f}m past end)"
        else:
            status_word = "Normal"
            status_help = "Baseline streaming telemetry without active injection"

        st.metric(
            "Stream Status",
            status_word,
            f"Series: {series}",
            help=status_help,
        )
    with col_m4:
        total_active_alarms = int(len(b_fired) > 0) + int(len(i_fired) > 0) + int(len(l_fired) > 0)
        st.metric(
            "Active Alarms",
            f"{total_active_alarms} / 3 Fired",
            f"Status: {status.upper()}",
            help="Number of distinct detectors that have fired at least once up to current playhead.",
        )


def render_detector_cards(
    curr_temp: float,
    clean_thresh: float,
    end_ts: pd.Timestamp,
    b_fired: pd.DataFrame,
    base_lead_val: float | None,
    current_reading: pd.Series,
    i_fired: pd.DataFrame,
    if_lead_val: float | None,
    lstm_thresh_val: float,
    l_fired: pd.DataFrame,
    lstm_lead_val: float | None,
    lstm_reason: str,
) -> None:
    """Render the 3 side-by-side detector cards using native st.metric primitives."""
    st.markdown("---")
    c_det1, c_det2, c_det3 = st.columns(3)

    # 1. Naive Baseline Card
    with c_det1:
        with st.container(border=True):
            st.subheader("Naive Baseline", icon=ICON_BASELINE)
            b_first_ts = b_fired.iloc[0]["ts"] if not b_fired.empty else None
            b_lead = (end_ts - b_first_ts).total_seconds() / 60.0 if b_first_ts is not None else None

            st.metric(
                label="Current Telemetry",
                value=f"{curr_temp:.2f} °C",
                delta=f"Threshold: {clean_thresh:.2f} °C",
                delta_color="off",
            )
            if b_first_ts:
                effective_lead = base_lead_val if base_lead_val is not None else b_lead
                st.metric(
                    label="Lead Time (Early Warning)",
                    value=f"{effective_lead:.1f} min",
                    delta=f"Alarm: {b_first_ts.strftime('%H:%M:%S')}",
                    delta_color="normal" if effective_lead > 0 else "off",
                    help=f"First baseline alarm fired at {b_first_ts}",
                )
            else:
                st.metric(
                    label="Lead Time (Early Warning)",
                    value="No Alarm",
                    delta="Normal in window",
                    delta_color="off",
                    help="Baseline threshold not breached within evaluation window",
                )

    # 2. Isolation Forest Card
    with c_det2:
        with st.container(border=True):
            st.subheader("Isolation Forest", icon=ICON_IF)
            i_first_ts = i_fired.iloc[0]["ts"] if not i_fired.empty else None
            i_lead = (end_ts - i_first_ts).total_seconds() / 60.0 if i_first_ts is not None else None

            st.metric(
                label="Decision Score",
                value=f"{current_reading['if_score']:.4f}",
                delta="Threshold: < 0.0000",
                delta_color="off",
            )
            if i_first_ts:
                effective_lead = if_lead_val if if_lead_val is not None else i_lead
                st.metric(
                    label="Lead Time (Early Warning)",
                    value=f"{effective_lead:.1f} min",
                    delta=f"Alarm: {i_first_ts.strftime('%H:%M:%S')}",
                    delta_color="normal" if effective_lead > 0 else "off",
                    help=f"First Isolation Forest alarm fired at {i_first_ts}",
                )
            else:
                st.metric(
                    label="Lead Time (Early Warning)",
                    value="No Alarm",
                    delta="Normal in window",
                    delta_color="off",
                    help="Decision score remained >= 0.0 throughout evaluation window",
                )

    # 3. LSTM-Autoencoder Card
    with c_det3:
        with st.container(border=True):
            st.subheader("LSTM-Autoencoder", icon=ICON_LSTM)
            l_first_ts = l_fired.iloc[0]["ts"] if not l_fired.empty else None
            l_lead = (end_ts - l_first_ts).total_seconds() / 60.0 if l_first_ts is not None else None

            st.metric(
                label="Reconstruction MSE",
                value=f"{current_reading['lstm_score']:.4f}",
                delta=f"Threshold: ≥ {lstm_thresh_val:.4f}",
                delta_color="off",
            )
            if l_first_ts:
                effective_lead = lstm_lead_val if lstm_lead_val is not None else l_lead
                st.metric(
                    label="Lead Time (Early Warning)",
                    value=f"{effective_lead:.1f} min",
                    delta=f"Alarm: {l_first_ts.strftime('%H:%M:%S')}",
                    delta_color="normal" if effective_lead > 0 else ("inverse" if effective_lead < 0 else "off"),
                    help=f"First LSTM alarm fired at {l_first_ts}",
                )
            else:
                if lstm_reason == "never_flagged":
                    reason_short = "Never flagged"
                elif "excluded" in lstm_reason:
                    reason_short = "Excluded (Train)"
                else:
                    reason_short = "No Alarm"
                st.metric(
                    label="Lead Time (Early Warning)",
                    value="No Alarm",
                    delta=reason_short,
                    delta_color="off",
                    help=f"Evaluation Status: {lstm_reason}",
                )
