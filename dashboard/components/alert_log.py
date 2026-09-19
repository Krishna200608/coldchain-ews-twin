"""
dashboard/components/alert_log.py
=================================
Live streaming alert log table with multi-detector filtering and verified
datetime column formatting.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.constants import ICON_ALERT_LOG, ICON_INFO


def render_alert_log(
    active_slice: pd.DataFrame,
    clean_thresh: float,
    onset_ts: pd.Timestamp,
    horizon_end_ts: pd.Timestamp,
    lstm_thresh_val: float,
) -> None:
    """Render streaming alert log table with detector and evaluation window filters."""
    st.markdown("---")
    st.subheader("Live Streaming Alert Log", icon=ICON_ALERT_LOG)

    all_active_alarms = []
    for _, r in active_slice.iterrows():
        t_stamp = r["ts"]
        temp = r["temp_injected"]
        if r["baseline_alarm"]:
            all_active_alarms.append({
                "Timestamp": t_stamp,
                "Detector": "Naive Baseline",
                "Telemetry (°C)": f"{temp:.2f}",
                "Score": f"{r['baseline_score']:.2f}",
                "Threshold": f"{clean_thresh:.2f}",
                "Evaluation Window": "In Horizon" if onset_ts <= t_stamp <= horizon_end_ts else "Outside Horizon",
            })
        if r["if_alarm"]:
            all_active_alarms.append({
                "Timestamp": t_stamp,
                "Detector": "Isolation Forest",
                "Telemetry (°C)": f"{temp:.2f}",
                "Score": f"{r['if_score']:.4f}",
                "Threshold": "0.0000",
                "Evaluation Window": "In Horizon" if onset_ts <= t_stamp <= horizon_end_ts else "Outside Horizon",
            })
        if r["lstm_alarm"]:
            all_active_alarms.append({
                "Timestamp": t_stamp,
                "Detector": "LSTM-Autoencoder",
                "Telemetry (°C)": f"{temp:.2f}",
                "Score": f"{r['lstm_score']:.4f}",
                "Threshold": f"{lstm_thresh_val:.4f}",
                "Evaluation Window": "In Horizon" if onset_ts <= t_stamp <= horizon_end_ts else "Outside Horizon",
            })

    c_filt1, c_filt2 = st.columns([2, 2])
    with c_filt1:
        detector_filter = st.selectbox(
            "Filter by Detector",
            ["All Detectors", "Naive Baseline", "Isolation Forest", "LSTM-Autoencoder"],
            index=0,
        )
    with c_filt2:
        window_filter = st.selectbox(
            "Filter by Window",
            ["All Window Readings", "Within Search Horizon Only"],
            index=0,
        )

    if all_active_alarms:
        df_alerts = pd.DataFrame(all_active_alarms)

        # Compute detector counts
        n_base = int((df_alerts["Detector"] == "Naive Baseline").sum())
        n_if = int((df_alerts["Detector"] == "Isolation Forest").sum())
        n_lstm = int((df_alerts["Detector"] == "LSTM-Autoencoder").sum())

        st.caption(
            f"{ICON_INFO} **Alert Distribution up to Playhead:** "
            f"Naive Baseline: **{n_base}** | Isolation Forest: **{n_if}** | LSTM-Autoencoder: **{n_lstm}**. "
            f"(Isolation Forest triggers frequently due to its known higher anomaly sensitivity / false-positive profile from M3)."
        )

        if detector_filter != "All Detectors":
            df_alerts = df_alerts[df_alerts["Detector"] == detector_filter]
        if window_filter == "Within Search Horizon Only":
            df_alerts = df_alerts[df_alerts["Evaluation Window"] == "In Horizon"]

        df_alerts = df_alerts.sort_values("Timestamp", ascending=False).reset_index(drop=True)
        st.dataframe(
            df_alerts,
            use_container_width=True,
            height=220,
            column_config={
                "Timestamp": st.column_config.DatetimeColumn(
                    "Timestamp",
                    format="YYYY-MM-DD HH:mm:ss",
                    width="medium",
                ),
                "Detector": st.column_config.TextColumn("Detector", width="medium"),
                "Telemetry (°C)": st.column_config.TextColumn("Telemetry (°C)", width="small"),
                "Score": st.column_config.TextColumn("Score", width="small"),
                "Threshold": st.column_config.TextColumn("Threshold", width="small"),
                "Evaluation Window": st.column_config.TextColumn("Evaluation Window", width="medium"),
            },
        )
    else:
        st.info("No anomaly alarms triggered up to current replay position.", icon=ICON_INFO)
