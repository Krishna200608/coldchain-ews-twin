"""
dashboard/components/telemetry_chart.py
=======================================
Interactive Altair streaming telemetry chart and secondary anomaly score
diagnostics panel.
"""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from dashboard.constants import (
    ICON_CHART,
    ICON_EXPANDER,
    SEARCH_HORIZON_MINUTES,
)


def render_telemetry_chart(
    sim_df: pd.DataFrame,
    clean_thresh: float,
    onset_ts: pd.Timestamp,
    end_ts: pd.Timestamp,
    horizon_end_ts: pd.Timestamp,
    inj_type: str,
    curr_ts: pd.Timestamp,
    b_fired: pd.DataFrame,
    i_fired: pd.DataFrame,
    l_fired: pd.DataFrame,
) -> alt.Chart:
    """Render interactive Altair telemetry line chart with alarm overlays and return playhead rule."""
    st.markdown("---")
    st.subheader("Live Streaming Telemetry & Alarm Horizon", icon=ICON_CHART)

    # Base line chart of temperature
    base_chart = alt.Chart(sim_df).encode(
        x=alt.X("ts:T", title="Timestamp", axis=alt.Axis(format="%Y-%m-%d %H:%M")),
    )

    temp_line = base_chart.mark_line(color="#1e293b", strokeWidth=2).encode(
        y=alt.Y("temp_injected:Q", title="Temperature (°C)", scale=alt.Scale(zero=False)),
        tooltip=[
            alt.Tooltip("ts:T", title="Timestamp", format="%Y-%m-%d %H:%M:%S"),
            alt.Tooltip("temp_injected:Q", title="Temp (°C)", format=".2f"),
            alt.Tooltip("if_score:Q", title="IF Score", format=".4f"),
            alt.Tooltip("lstm_score:Q", title="LSTM MSE", format=".4f"),
        ],
    )

    # Baseline threshold line
    thresh_df = pd.DataFrame([{"thresh": clean_thresh}])
    thresh_rule = alt.Chart(thresh_df).mark_rule(color="#ef4444", strokeDash=[6, 4], strokeWidth=1.5).encode(
        y="thresh:Q",
        tooltip=[alt.Tooltip("thresh:Q", title="Baseline Threshold (°C)", format=".2f")],
    )

    # Shaded span for Injection Active
    span_inj = alt.Chart(pd.DataFrame([{
        "start": onset_ts,
        "end": end_ts,
        "label": f"Injection Active: {inj_type.upper()}",
    }])).mark_rect(color="#f97316", opacity=0.18).encode(
        x="start:T",
        x2="end:T",
    )

    # Shaded span for Search Horizon
    span_horizon = alt.Chart(pd.DataFrame([{
        "start": end_ts,
        "end": horizon_end_ts,
        "label": f"Evaluation Search Horizon ({SEARCH_HORIZON_MINUTES:.0f}m)",
    }])).mark_rect(color="#a855f7", opacity=0.12).encode(
        x="start:T",
        x2="end:T",
    )

    # Vertical rule for current playback position
    playhead_rule = alt.Chart(pd.DataFrame([{"playhead": curr_ts}])).mark_rule(
        color="#2563eb",
        strokeWidth=2.5,
        strokeDash=[3, 3],
    ).encode(x="playhead:T")

    # Alarm point layers (plotted if alarms triggered up to current frame)
    alarm_layers = []

    if not b_fired.empty:
        b_pts = alt.Chart(b_fired).mark_point(color="#dc2626", shape="triangle-up", size=110, filled=True).encode(
            x="ts:T",
            y="temp_injected:Q",
            tooltip=[alt.Tooltip("ts:T", title="Baseline Alarm"), alt.Tooltip("temp_injected:Q", title="Temp")],
        )
        alarm_layers.append(b_pts)

    if not i_fired.empty:
        i_pts = alt.Chart(i_fired).mark_point(color="#16a34a", shape="square", size=90, filled=True).encode(
            x="ts:T",
            y="temp_injected:Q",
            tooltip=[alt.Tooltip("ts:T", title="IF Alarm"), alt.Tooltip("if_score:Q", title="IF Score")],
        )
        alarm_layers.append(i_pts)

    if not l_fired.empty:
        l_pts = alt.Chart(l_fired).mark_point(color="#2563eb", shape="circle", size=90, filled=True).encode(
            x="ts:T",
            y="temp_injected:Q",
            tooltip=[alt.Tooltip("ts:T", title="LSTM Alarm"), alt.Tooltip("lstm_score:Q", title="LSTM MSE")],
        )
        alarm_layers.append(l_pts)

    chart = span_inj + span_horizon + thresh_rule + temp_line + playhead_rule
    for al in alarm_layers:
        chart = chart + al

    st.altair_chart(chart.properties(height=360), use_container_width=True)

    st.caption(
        "Visual Legend: Orange Band = Injection Duration | Purple Band = Search Horizon (60 min) | "
        "Red Triangles = Baseline Alarms | Green Squares = Isolation Forest Alarms | "
        "Blue Circles = LSTM-Autoencoder Alarms | Dashed Blue Line = Current Playhead"
    )

    return playhead_rule


def render_score_diagnostics(
    sim_df: pd.DataFrame,
    playhead_rule: alt.Chart,
    lstm_thresh_val: float,
) -> None:
    """Render secondary collapsible diagnostic charts for IF and LSTM decision scores."""
    with st.expander("Inspect Live Anomaly Score Trajectories (IF Decision vs. LSTM MSE)", icon=ICON_EXPANDER):
        c_diag1, c_diag2 = st.columns(2)
        with c_diag1:
            if_chart = (
                alt.Chart(sim_df)
                .mark_line(color="#16a34a")
                .encode(
                    x=alt.X("ts:T", title="Timestamp"),
                    y=alt.Y("if_score:Q", title="IF Decision Score (<0 is Anomaly)"),
                )
            )
            if_rule = alt.Chart(pd.DataFrame([{"zero": 0.0}])).mark_rule(color="#991b1b", strokeDash=[4, 4]).encode(y="zero:Q")
            st.altair_chart((if_chart + if_rule + playhead_rule).properties(height=200), use_container_width=True)
            st.caption("Isolation Forest Decision Function Score (Threshold: 0.0)")

        with c_diag2:
            lstm_chart = (
                alt.Chart(sim_df)
                .mark_line(color="#2563eb")
                .encode(
                    x=alt.X("ts:T", title="Timestamp"),
                    y=alt.Y("lstm_score:Q", title="LSTM Reconstruction MSE (D16)"),
                )
            )
            lstm_rule = alt.Chart(pd.DataFrame([{"thresh": lstm_thresh_val}])).mark_rule(color="#991b1b", strokeDash=[4, 4]).encode(y="thresh:Q")
            st.altair_chart((lstm_chart + lstm_rule + playhead_rule).properties(height=200), use_container_width=True)
            st.caption(f"LSTM Reconstruction Error MSE (D13 Threshold: {lstm_thresh_val:.4f})")
