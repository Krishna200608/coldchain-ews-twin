"""
dashboard/components/showcase.py
================================
Guided Tour showcase caption container with D34 dynamic runtime interpolation
and truncation-proof showcase metadata metrics row.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st


def render_showcase_banner(
    mode: str,
    selected_inj_id: str,
    inj_type: str,
    onset_ts: pd.Timestamp,
    three_way_df: pd.DataFrame,
    clean_thresh: float,
    lstm_thresh_val: float,
) -> None:
    """
    Render Guided Tour showcase narrative caption and metadata metrics row (D34).
    Dynamically interpolates values from three_way_comparison.csv.
    """
    if "Guided Tour" not in mode:
        return

    # Fetch values dynamically from three_way_comparison.csv
    tw_match = three_way_df[three_way_df["injection_id"] == selected_inj_id]
    tw_row = tw_match.iloc[0] if not tw_match.empty else None

    base_alarm_str = str(tw_row["baseline_alarm_timestamp"]) if tw_row is not None and pd.notna(tw_row["baseline_alarm_timestamp"]) else "None"
    base_lead_val = float(tw_row["baseline_lead_time_min"]) if tw_row is not None and pd.notna(tw_row["baseline_lead_time_min"]) else None
    if_alarm_str = str(tw_row["alarm_timestamp_IF"]) if tw_row is not None and pd.notna(tw_row["alarm_timestamp_IF"]) else "None"
    if_lead_val = float(tw_row["lead_time_IF_min"]) if tw_row is not None and pd.notna(tw_row["lead_time_IF_min"]) else None
    lstm_alarm_str = str(tw_row["alarm_timestamp_LSTM"]) if tw_row is not None and pd.notna(tw_row["alarm_timestamp_LSTM"]) else "None"
    lstm_lead_val = float(tw_row["lead_time_LSTM_min"]) if tw_row is not None and pd.notna(tw_row["lead_time_LSTM_min"]) else None
    lstm_reason = str(tw_row["lstm_evaluation_reason"]) if tw_row is not None and pd.notna(tw_row["lstm_evaluation_reason"]) else "N/A"

    with st.container(border=True):
        if selected_inj_id == "out_step_001":
            st.markdown("### Showcase 1: Unambiguous Step Anomaly (Catastrophic Failure Anchor)")
            st.markdown(
                f"A sudden +12.0 °C step displacement occurs at `{onset_ts}`. "
                f"All three detectors trigger synchronously at the very first post-onset reading at "
                f"`{base_alarm_str}` with an identical lead time of **{base_lead_val:.1f} minutes**. "
                f"This confirms zero latency divergence under gross, catastrophic system breaches."
            )
        elif selected_inj_id == "out_drift_009":
            st.markdown("### Showcase 2: Incipient Thermal Drift (Early Warning vs. Sequence Lag)")
            st.markdown(
                f"Under gradual thermal drift (+0.03 °C/min), the Naive Baseline remains blind until upper limit crossing at "
                f"`{base_alarm_str}` (lead time: **{base_lead_val:.1f} min**). "
                f"Isolation Forest flags multivariate anomalies early at `{if_alarm_str}`, providing a "
                f"vital early warning advantage of **+{if_lead_val:.1f} minutes**. "
                f"In contrast, LSTM-Autoencoder triggers at `{lstm_alarm_str}` with a lead time of "
                f"**{lstm_lead_val:.1f} minutes** (a **{abs(lstm_lead_val):.1f}-minute lag** relative to baseline crossing), "
                f"illustrating autoencoder sequence inertia during creeping, low-slope drift."
            )
        elif selected_inj_id == "out_flatline_013":
            st.markdown("### Showcase 3: Flatline Within Normal Temperature Bounds (Baseline Blind Spot)")
            st.markdown(
                f"The sensor value freezes at ~37.3 °C, entirely inside normal operating temperatures. "
                f"Because the value never exceeds the clean threshold (`{clean_thresh:.2f} °C`), the Naive Baseline "
                f"**completely fails to alarm** (alarm: `{base_alarm_str}`). "
                f"Isolation Forest captures the unnatural collapse in rolling variance and alarms at `{if_alarm_str}`. "
                f"LSTM reconstruction error remains below threshold (`{lstm_thresh_val:.4f}`), resulting in "
                f"`{lstm_reason}`."
            )
        elif selected_inj_id == "in_drift_023":
            st.markdown("### Showcase 4: Inbound Thermal Drift (Multi-Model Validation)")
            st.markdown(
                f"Inbound sensor drift beginning at `{onset_ts}`. "
                f"Isolation Forest alarms early at `{if_alarm_str}` giving "
                f"**+{if_lead_val:.1f} minutes** early warning. "
                f"Both Naive Baseline and LSTM-Autoencoder trigger synchronously when temperature crosses the upper threshold at "
                f"`{base_alarm_str}` (lead time: **{base_lead_val:.1f} minutes**)."
            )

        st.divider()
        c_c1, c_c2, c_c3, c_c4 = st.columns(4)
        with c_c1:
            st.metric(
                label="Onset Time",
                value=onset_ts.strftime("%H:%M:%S"),
                delta=onset_ts.strftime("%Y-%m-%d"),
                delta_color="off",
                help=f"Full Anomaly Onset: {onset_ts.strftime('%Y-%m-%d %H:%M:%S')}",
            )
        with c_c2:
            st.metric(
                label="Anomaly Type",
                value=inj_type.capitalize(),
                help=f"Synthetic Anomaly Type: {inj_type.capitalize()}",
            )
        with c_c3:
            st.metric(
                label="Baseline Alarm",
                value=base_alarm_str.split(" ")[-1] if base_alarm_str != "None" else "No Alarm",
                help=f"Baseline Alarm Timestamp: {base_alarm_str}",
            )
        with c_c4:
            st.metric(
                label="IF Lead Time",
                value=f"{if_lead_val:+.1f} min" if if_lead_val is not None else "N/A",
                delta="Early warning" if (if_lead_val is not None and if_lead_val > 0) else None,
                help=f"Isolation Forest Lead Time: {if_lead_val:+.1f} min relative to baseline" if if_lead_val is not None else "Isolation Forest did not alarm",
            )
