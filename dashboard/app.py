"""
dashboard/app.py
================
Live Digital Twin Early Warning System Dashboard (Milestone 6.3).
Thin presentation-grade application entry point and layout orchestration.

STRUCTURAL PROXY NOTICE (D31):
------------------------------
All telemetry derives from IOT-temp.csv (generic IoT temperature sensor log),
NOT refrigerated-transport operations. All injected anomalies are synthetic
proxy constructs. Detectors carry no food-safety significance.
See docs/AD_LOG.md (D1–D34).

DESIGN DECISIONS HONORED:
- D27: Direct imports of verified BaselineMonitor, IFMonitor, LSTMMonitor from
       src.twin_monitors and exact sorting from src.digital_twin.
- D28: Accelerated replay; playback speed is display-only and never alters telemetry.
- D29: Two modes: Guided Tour (4 test-side showcase steps) and Free Explore (all 30 injections).
- D30: Streamlit framework in modular dashboard/ architecture.
- D31: Persistent structural proxy disclaimer banner + train-side demo banner.
- D32: Startup check verifying models and data artifacts before replay.
- D33: Mandatory silent buffer pre-warming with preceding 10 (IF) and 30 (LSTM) readings.
- D34: Dynamic runtime interpolation of captions from three_way_comparison.csv
       and twin_crosscheck_report.csv (never hardcoded numbers).
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.constants import (
    GUIDED_TOUR_STEPS,
    ICON_APP,
    ICON_ERROR,
    ICON_EXPLORE,
    ICON_FIRST_PAGE,
    ICON_INFO,
    ICON_LAST_PAGE,
    ICON_NAV,
    ICON_SPEED,
    ICON_TOUR,
    LSTM_THRESH_IN,
    LSTM_THRESH_OUT,
    REPLAY_SPEED_OPTIONS,
    SEARCH_HORIZON_MINUTES,
)
from dashboard.data_loader import (
    get_clean_baseline_threshold,
    load_all_metadata,
    load_clean_stream,
    run_d32_startup_check,
)
from dashboard.replay_engine import (
    get_active_telemetry_slice,
    simulate_prewarmed_window,
)
from dashboard.components.alert_log import render_alert_log
from dashboard.components.banners import (
    render_header_and_disclaimers,
    render_train_demo_banner,
)
from dashboard.components.crosscheck_audit import render_crosscheck_audit
from dashboard.components.detector_cards import (
    render_detector_cards,
    render_telemetry_metrics_row,
)
from dashboard.components.showcase import render_showcase_banner
from dashboard.components.telemetry_chart import (
    render_score_diagnostics,
    render_telemetry_chart,
)

# ══ Page Configuration ═════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Cold Chain EWS Digital Twin",
    page_icon=ICON_APP,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══ D32 Startup Check ══════════════════════════════════════════════════════════

missing_artifacts = run_d32_startup_check()
if missing_artifacts:
    st.error("Startup Artifact Verification Failed (D32)", icon=ICON_ERROR)
    st.markdown(
        "The following required model or data artifacts were not found:\n"
        + "".join([f"- `{m}`\n" for m in missing_artifacts])
    )
    st.info(
        "**Remediation Instructions:**\n"
        "Please generate the verified models and evaluation reports using the frozen pipeline scripts:\n"
        "```bash\n"
        "python src/twin_monitors.py\n"
        "python src/twin_crosscheck.py\n"
        "```",
        icon=ICON_INFO,
    )
    st.stop()

# ══ Cached Metadata Loading ════════════════════════════════════════════════════

merged_injections, status_df, three_way_df, crosscheck_df = load_all_metadata()

# ══ UI Header & Persistent Disclaimers (D31) ═══════════════════════════════════

render_header_and_disclaimers()

# ══ Sidebar Replay Navigation ══════════════════════════════════════════════════

st.sidebar.header("Replay Navigation", icon=ICON_NAV)

mode = st.sidebar.radio(
    "Select Operating Mode",
    [f"{ICON_TOUR} Guided Tour (Viva Showcase)", f"{ICON_EXPLORE} Free Explore (All 30 Injections)"],
    index=0,
)

if "Guided Tour" in mode:
    step_labels = [s["label"] for s in GUIDED_TOUR_STEPS]
    selected_label = st.sidebar.selectbox("Guided Tour Showcase Step", step_labels, index=0)
    selected_step = next(s for s in GUIDED_TOUR_STEPS if s["label"] == selected_label)
    selected_inj_id = selected_step["id"]
    padding_hours = 2.0
else:
    series_filter = st.sidebar.selectbox("Series", ["All", "Out", "In"], index=0)
    filtered_injs = merged_injections.copy()
    if series_filter != "All":
        filtered_injs = filtered_injs[filtered_injs["series"] == series_filter]

    def format_inj_option(row: pd.Series) -> str:
        status_tag = "TEST" if row["train_test_status"] == "test" else "TRAIN DEMO"
        return f"{row['injection_id']} | {row['series']} {row['type']} [{status_tag}]"

    inj_options = list(filtered_injs["injection_id"])
    selected_inj_id = st.sidebar.selectbox(
        "Select Synthetic Injection",
        inj_options,
        format_func=lambda i_id: format_inj_option(filtered_injs[filtered_injs["injection_id"] == i_id].iloc[0]),
        index=0,
    )
    padding_hours = st.sidebar.slider("Replay Window Padding (± Hours)", min_value=0.5, max_value=6.0, value=2.0, step=0.5)

# Retrieve selected injection metadata
inj_row = merged_injections[merged_injections["injection_id"] == selected_inj_id].iloc[0]
series = inj_row["series"]
inj_type = inj_row["type"]
status = inj_row["train_test_status"]
onset_ts = pd.Timestamp(inj_row["start_ts"])
end_ts = pd.Timestamp(inj_row["end_ts"])
horizon_end_ts = end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)

# D31: Demo banner for train-side injections
render_train_demo_banner(status)

# ══ Window Setup & Simulation Loop (D33) ═══════════════════════════════════════

df_stream = load_clean_stream(series)
win_start_ts = onset_ts - pd.Timedelta(hours=padding_hours)
win_end_ts = horizon_end_ts + pd.Timedelta(hours=padding_hours)

win_indices = df_stream[(df_stream["ts"] >= win_start_ts) & (df_stream["ts"] <= win_end_ts)].index
if len(win_indices) == 0:
    st.error(f"No telemetry readings found in window {win_start_ts} to {win_end_ts}", icon=ICON_ERROR)
    st.stop()

win_start_idx = int(win_indices[0])
win_end_idx = int(win_indices[-1])

sim_df = simulate_prewarmed_window(series, win_start_idx, win_end_idx)
total_frames = len(sim_df)

# ══ Playback Controls (D28) ════════════════════════════════════════════════════

st.sidebar.markdown("---")
st.sidebar.subheader("Playback Controls", icon=ICON_SPEED)

session_key = f"playhead_{selected_inj_id}"
if session_key not in st.session_state:
    st.session_state[session_key] = total_frames - 1

c_reset, c_end = st.sidebar.columns(2)
if c_reset.button("Start", icon=ICON_FIRST_PAGE, use_container_width=True, help="Reset to Start of Window"):
    st.session_state[session_key] = 0
if c_end.button("End", icon=ICON_LAST_PAGE, use_container_width=True, help="Jump to End of Window"):
    st.session_state[session_key] = total_frames - 1

replay_speed = st.sidebar.select_slider(
    "Replay Speed Factor",
    options=REPLAY_SPEED_OPTIONS,
    value="Instant",
    help="Playback speed is display-only and never alters telemetry values fed to models (D28).",
)

current_frame = st.sidebar.slider(
    "Scrub Replay Timeline",
    min_value=0,
    max_value=total_frames - 1,
    value=st.session_state[session_key],
    format="%d readings",
)
st.session_state[session_key] = current_frame

# ══ Scientific Context & Thresholds ════════════════════════════════════════════

clean_thresh = get_clean_baseline_threshold(series)
lstm_thresh_val = LSTM_THRESH_OUT if series == "Out" else LSTM_THRESH_IN

# ══ D34 Showcase Narrative & Metadata Row ══════════════════════════════════════

render_showcase_banner(
    mode=mode,
    selected_inj_id=selected_inj_id,
    inj_type=inj_type,
    onset_ts=onset_ts,
    three_way_df=three_way_df,
    clean_thresh=clean_thresh,
    lstm_thresh_val=lstm_thresh_val,
)

# ══ Active Telemetry Slice & Detector Alarms ═══════════════════════════════════

active_slice, current_reading, eval_slice, b_fired, i_fired, l_fired = get_active_telemetry_slice(
    sim_df=sim_df,
    current_frame=current_frame,
    onset_ts=onset_ts,
    horizon_end_ts=horizon_end_ts,
)
curr_ts = current_reading["ts"]
curr_temp = current_reading["temp_injected"]

# ══ Telemetry Metrics Bar ══════════════════════════════════════════════════════

render_telemetry_metrics_row(
    curr_ts=curr_ts,
    current_frame=current_frame,
    total_frames=total_frames,
    curr_temp=curr_temp,
    onset_ts=onset_ts,
    end_ts=end_ts,
    horizon_end_ts=horizon_end_ts,
    inj_type=inj_type,
    series=series,
    status=status,
    b_fired=b_fired,
    i_fired=i_fired,
    l_fired=l_fired,
)

# ══ Three-Way Detector Comparison Cards ════════════════════════════════════════

tw_match = three_way_df[three_way_df["injection_id"] == selected_inj_id]
tw_row = tw_match.iloc[0] if not tw_match.empty else None

base_lead_val = float(tw_row["baseline_lead_time_min"]) if tw_row is not None and pd.notna(tw_row["baseline_lead_time_min"]) else None
if_lead_val = float(tw_row["lead_time_IF_min"]) if tw_row is not None and pd.notna(tw_row["lead_time_IF_min"]) else None
lstm_lead_val = float(tw_row["lead_time_LSTM_min"]) if tw_row is not None and pd.notna(tw_row["lead_time_LSTM_min"]) else None
lstm_reason = str(tw_row["lstm_evaluation_reason"]) if tw_row is not None and pd.notna(tw_row["lstm_evaluation_reason"]) else "N/A"

render_detector_cards(
    curr_temp=curr_temp,
    clean_thresh=clean_thresh,
    end_ts=end_ts,
    b_fired=b_fired,
    base_lead_val=base_lead_val,
    current_reading=current_reading,
    i_fired=i_fired,
    if_lead_val=if_lead_val,
    lstm_thresh_val=lstm_thresh_val,
    l_fired=l_fired,
    lstm_lead_val=lstm_lead_val,
    lstm_reason=lstm_reason,
)

# ══ Interactive Altair Telemetry & Alarm Trajectory Chart ══════════════════════

playhead_rule = render_telemetry_chart(
    sim_df=sim_df,
    clean_thresh=clean_thresh,
    onset_ts=onset_ts,
    end_ts=end_ts,
    horizon_end_ts=horizon_end_ts,
    inj_type=inj_type,
    curr_ts=curr_ts,
    b_fired=b_fired,
    i_fired=i_fired,
    l_fired=l_fired,
)

render_score_diagnostics(
    sim_df=sim_df,
    playhead_rule=playhead_rule,
    lstm_thresh_val=lstm_thresh_val,
)

# ══ Real-Time Alert Log ════════════════════════════════════════════════════════

render_alert_log(
    active_slice=active_slice,
    clean_thresh=clean_thresh,
    onset_ts=onset_ts,
    horizon_end_ts=horizon_end_ts,
    lstm_thresh_val=lstm_thresh_val,
)

# ══ Scientific Cross-Check Verification Audit (Footer) ═════════════════════════

render_crosscheck_audit(
    status=status,
    selected_inj_id=selected_inj_id,
    crosscheck_df=crosscheck_df,
)
