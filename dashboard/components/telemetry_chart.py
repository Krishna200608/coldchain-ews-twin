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

    st.altair_chart(chart.properties(height=360), width="stretch")

    legend_html = """
    <div style="
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
        margin-top: 6px;
        margin-bottom: 12px;
        padding: 8px 12px;
        background: rgba(15, 23, 42, 0.55);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    ">
        <span style="font-weight: 700; color: #94a3b8; margin-right: 4px; text-transform: uppercase; font-size: 0.72rem; letter-spacing: 0.5px;">
            Legend
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; background: rgba(234, 88, 12, 0.15); border: 1px solid rgba(249, 115, 22, 0.45); border-radius: 6px; color: #fb923c; font-size: 0.78rem; font-weight: 500;">
            <span style="display: inline-block; width: 10px; height: 10px; background: #ea580c; border-radius: 2px;"></span>
            Injection Duration
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; background: rgba(147, 51, 234, 0.15); border: 1px solid rgba(168, 85, 247, 0.45); border-radius: 6px; color: #c084fc; font-size: 0.78rem; font-weight: 500;">
            <span style="display: inline-block; width: 10px; height: 10px; background: #9333ea; border-radius: 2px;"></span>
            Search Horizon (60m)
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; background: rgba(220, 38, 38, 0.15); border: 1px solid rgba(239, 68, 68, 0.45); border-radius: 6px; color: #f87171; font-size: 0.78rem; font-weight: 500;">
            <span style="color: #ef4444; font-size: 0.72rem; line-height: 1;">▲</span>
            Baseline Alarm
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; background: rgba(22, 163, 74, 0.15); border: 1px solid rgba(34, 197, 94, 0.45); border-radius: 6px; color: #4ade80; font-size: 0.78rem; font-weight: 500;">
            <span style="color: #22c55e; font-size: 0.75rem; line-height: 1;">■</span>
            Isolation Forest
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; background: rgba(37, 99, 235, 0.15); border: 1px solid rgba(59, 130, 246, 0.45); border-radius: 6px; color: #60a5fa; font-size: 0.78rem; font-weight: 500;">
            <span style="color: #3b82f6; font-size: 0.75rem; line-height: 1;">●</span>
            LSTM-Autoencoder
        </span>
        <span style="display: inline-flex; align-items: center; gap: 6px; padding: 3px 9px; background: rgba(14, 165, 233, 0.12); border: 1px solid rgba(56, 189, 248, 0.45); border-radius: 6px; color: #38bdf8; font-size: 0.78rem; font-weight: 500;">
            <span style="display: inline-block; border-left: 2px dashed #38bdf8; height: 11px;"></span>
            Current Playhead
        </span>
    </div>
    """
    st.markdown(legend_html, unsafe_allow_html=True)

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
            st.altair_chart((if_chart + if_rule + playhead_rule).properties(height=200), width="stretch")
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
            st.altair_chart((lstm_chart + lstm_rule + playhead_rule).properties(height=200), width="stretch")
            st.caption(f"LSTM Reconstruction Error MSE (D13 Threshold: {lstm_thresh_val:.4f})")
