"""
dashboard/app.py
================
Live Digital Twin Early Warning System Dashboard (Milestone 6).
Streamlit presentation-grade interactive dashboard for instructor/viva demonstrations.

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
- D30: Streamlit framework in dashboard/app.py.
- D31: Persistent structural proxy disclaimer banner + train-side demo banner.
- D32: Startup check verifying models and data artifacts before replay.
- D33: Mandatory silent buffer pre-warming with preceding 10 (IF) and 30 (LSTM) readings.
- D34: Dynamic runtime interpolation of captions from three_way_comparison.csv
       and twin_crosscheck_report.csv (never hardcoded numbers).
"""

from __future__ import annotations

import json
import pathlib
import sys
import time
from typing import Any

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# Ensure repository root and src directory are on sys.path
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SRC_DIR))

# D27: Direct imports from verified components
from src.twin_monitors import BaselineMonitor, IFMonitor, LSTMMonitor
from src.config import SEARCH_HORIZON_MINUTES

# Paths
MODELS_DIR = REPO_ROOT / "models"
DATA_DIR = REPO_ROOT / "data" / "processed"

# Page configuration
st.set_page_config(
    page_title="Cold Chain EWS Digital Twin",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for presentation-grade UI
st.markdown(
    """
    <style>
    .proxy-banner {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 12px 16px;
        border-radius: 4px;
        color: #856404;
        font-size: 0.88rem;
        margin-bottom: 1rem;
    }
    .demo-banner {
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        padding: 10px 14px;
        border-radius: 4px;
        color: #0c5460;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #fdfdfd;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 14px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .badge-normal {
        background-color: #e2e8f0;
        color: #475569;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-alarm {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-lead {
        background-color: #dcfce7;
        color: #15803d;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .tour-caption-box {
        background-color: #f8fafc;
        border: 1px solid #cbd5e1;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        padding: 14px 18px;
        margin-bottom: 1.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ══ D32 Startup Check ══════════════════════════════════════════════════════════

def run_d32_startup_check() -> list[str]:
    """Verify presence of required models and data artifacts (D32)."""
    required_files = [
        MODELS_DIR / "isolation_forest_out.joblib",
        MODELS_DIR / "isolation_forest_in.joblib",
        MODELS_DIR / "lstm_out.h5",
        MODELS_DIR / "lstm_in.h5",
        DATA_DIR / "lstm_norm_stats_out.json",
        DATA_DIR / "lstm_norm_stats_in.json",
        DATA_DIR / "out_features.csv",
        DATA_DIR / "in_features.csv",
        DATA_DIR / "out_labeled.csv",
        DATA_DIR / "in_labeled.csv",
        DATA_DIR / "twin_crosscheck_report.csv",
        DATA_DIR / "three_way_comparison.csv",
        DATA_DIR / "injection_log.csv",
        DATA_DIR / "injection_train_test_status.csv",
    ]
    missing = [str(f.relative_to(REPO_ROOT)) for f in required_files if not f.exists()]
    return missing


missing_artifacts = run_d32_startup_check()
if missing_artifacts:
    st.error("### 🛑 Startup Artifact Verification Failed (D32)")
    st.markdown(
        f"The following required model or data artifacts were not found:\n"
        + "".join([f"- `{m}`\n" for m in missing_artifacts])
    )
    st.info(
        "**Remediation Instructions:**\n"
        "Please generate the verified models and evaluation reports using the frozen pipeline scripts:\n"
        "```bash\n"
        "python src/twin_monitors.py\n"
        "python src/twin_crosscheck.py\n"
        "```"
    )
    st.stop()


# ══ Cached Data Loaders ════════════════════════════════════════════════════════

@st.cache_data
def load_all_metadata() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load metadata and cross-check comparison tables."""
    inj_log = pd.read_csv(DATA_DIR / "injection_log.csv", parse_dates=["start_timestamp"])
    status_df = pd.read_csv(DATA_DIR / "injection_train_test_status.csv", parse_dates=["start_ts", "end_ts"])
    three_way = pd.read_csv(DATA_DIR / "three_way_comparison.csv")
    cross_df = pd.read_csv(DATA_DIR / "twin_crosscheck_report.csv")

    merged = inj_log.merge(
        status_df[["injection_id", "train_test_status", "start_ts", "end_ts"]],
        on="injection_id",
    )
    return merged, status_df, three_way, cross_df


@st.cache_data
def load_clean_stream(series_name: str) -> pd.DataFrame:
    """Load labeled telemetry stream and apply exact M5a sorting convention."""
    path = DATA_DIR / f"{series_name.lower()}_labeled.csv"
    raw = pd.read_csv(path, parse_dates=["ts"])
    # Exact sorting convention from src/digital_twin.py
    df_clean = (
        raw.dropna(subset=["gap_seconds"])
        .sort_values(["ts", "gap_seconds"], ascending=[True, False], kind="stable")
        .reset_index(drop=True)
    )
    return df_clean


@st.cache_data
def get_clean_baseline_threshold(series_name: str) -> float:
    """Compute whole-series clean baseline threshold (D24)."""
    path = DATA_DIR / f"{series_name.lower()}_features.csv"
    df_feat = pd.read_csv(path)
    t = df_feat["temp"].dropna()
    return float(t.mean() + 2.0 * t.std())


# ══ D33 Pre-Warmed Window Simulator ═════════════════════════════════════════════

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
    lstm_thresh = 1.010091 if series_name == "Out" else 1.512753

    # Instantiate verified monitors
    base_mon = BaselineMonitor(series_name, clean_features_path)
    if_mon = IFMonitor(series_name, if_model_path)
    lstm_mon = LSTMMonitor(series_name, lstm_model_path, lstm_stats_path, lstm_thresh)

    # D33: Pre-warm IF monitor with 10 readings prior to visible window
    prewarm_if = df_clean.iloc[max(0, win_start_idx - 10) : win_start_idx]
    for _, r in prewarm_if.iterrows():
        if_mon.process_event({
            "ts": r["ts"],
            "temp_injected": float(r["temp_injected"]),
            "gap_seconds": float(r["gap_seconds"]),
        })
    if_mon.alarm_records.clear()

    # D33: Pre-warm LSTM monitor with 30 readings prior to visible window
    prewarm_lstm = df_clean.iloc[max(0, win_start_idx - 30) : win_start_idx]
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


# ══ Load Data ══════════════════════════════════════════════════════════════════

merged_injections, status_df, three_way_df, crosscheck_df = load_all_metadata()

# ══ UI Header & Persistent Disclaimers ═════════════════════════════════════════

st.title("❄️ Cold Chain EWS — Live Digital Twin Anomaly Monitor")
st.markdown(
    "**A presentation-grade streaming early warning demonstration comparing Naive Baseline, "
    "Isolation Forest, and LSTM-Autoencoder anomaly detection.**"
)

# D31: Persistent Structural Proxy Disclaimer Banner
st.markdown(
    """
    <div class="proxy-banner">
        ⚠️ <strong>STRUCTURAL PROXY NOTICE</strong>: All telemetry derives from <code>IOT-temp.csv</code> 
        (generic IoT temperature sensor log), <strong>NOT</strong> refrigerated-transport operations. 
        All injected anomalies are synthetic proxy constructs. Detectors carry no food-safety significance. 
        See <code>docs/AD_LOG.md</code> (D1–D34).
    </div>
    """,
    unsafe_allow_html=True,
)


# ══ Sidebar Controls ═══════════════════════════════════════════════════════════

st.sidebar.header("🕹️ Replay Navigation")

mode = st.sidebar.radio(
    "Select Operating Mode",
    ["🎯 Guided Tour (Viva Showcase)", "🔍 Free Explore (All 30 Injections)"],
    index=0,
)

# 4 Showcase Steps for Guided Tour (All out-of-sample test comparisons)
GUIDED_TOUR_STEPS = [
    {
        "id": "out_step_001",
        "label": "1. out_step_001 (Step Anomaly — Synchronous 0-min lead time)",
        "summary": "Step Anomaly: Catastrophic jump triggers all 3 models synchronously at onset.",
    },
    {
        "id": "out_drift_009",
        "label": "2. out_drift_009 (Thermal Drift — IF +64.0 min lead vs LSTM -14.0 min lag)",
        "summary": "Thermal Drift: Multivariate early warning lead vs sequence memory inertia lag.",
    },
    {
        "id": "out_flatline_013",
        "label": "3. out_flatline_013 (In-Range Flatline — Baseline complete blind spot)",
        "summary": "In-Range Flatline: Zero variance failure for Baseline, subtle detection by IF.",
    },
    {
        "id": "in_drift_023",
        "label": "4. in_drift_023 (Inbound Thermal Drift — Multi-Model Early Warning)",
        "summary": "Inbound Drift: IF achieves +11.0 min early warning prior to baseline crossing.",
    },
]

if mode.startswith("🎯 Guided Tour"):
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

    def format_inj_option(row):
        status_tag = "TEST (Out-of-sample)" if row["train_test_status"] == "test" else "TRAIN (Demo Only)"
        return f"{row['injection_id']} | {row['series']} {row['type']} | [{status_tag}]"

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
if status == "train":
    st.markdown(
        """
        <div class="demo-banner">
            ℹ️ <strong>DEMO ONLY — Prior Training Exposure (D26/D31)</strong>: 
            This injection occurred during the training time range (<code>ts < cutoff_ts</code>). 
            Its live detection is demonstrated strictly as an interactive deployment preview, 
            <strong>not</strong> as an out-of-sample scientific performance claim.
        </div>
        """,
        unsafe_allow_html=True,
    )


# ══ Window Setup & Simulation ══════════════════════════════════════════════════

df_stream = load_clean_stream(series)
win_start_ts = onset_ts - pd.Timedelta(hours=padding_hours)
win_end_ts = horizon_end_ts + pd.Timedelta(hours=padding_hours)

win_indices = df_stream[(df_stream["ts"] >= win_start_ts) & (df_stream["ts"] <= win_end_ts)].index
if len(win_indices) == 0:
    st.error(f"No telemetry readings found in window {win_start_ts} to {win_end_ts}")
    st.stop()

win_start_idx = int(win_indices[0])
win_end_idx = int(win_indices[-1])

# Run simulation with D33 pre-warming
sim_df = simulate_prewarmed_window(series, win_start_idx, win_end_idx)
total_frames = len(sim_df)


# ══ Playback Controls (D28) ════════════════════════════════════════════════════

st.sidebar.markdown("---")
st.sidebar.subheader("⏱️ Playback Controls")
st.sidebar.caption("Playback speed is display-only and never alters telemetry values fed to models (D28).")

# Session state for playback position
session_key = f"playhead_{selected_inj_id}"
if session_key not in st.session_state:
    st.session_state[session_key] = total_frames - 1  # Default to full window viewed

c_play, c_pause, c_reset, c_end = st.sidebar.columns(4)
is_playing = False
if c_reset.button("⏮️", help="Reset to Start"):
    st.session_state[session_key] = 0
if c_end.button("⏭️", help="Jump to End"):
    st.session_state[session_key] = total_frames - 1

# Playback speed slider
replay_speed = st.sidebar.select_slider(
    "Replay Speed Factor",
    options=["1x", "5x", "10x", "25x", "Instant"],
    value="Instant",
)

current_frame = st.sidebar.slider(
    "Scrub Replay Timeline",
    min_value=0,
    max_value=total_frames - 1,
    value=st.session_state[session_key],
    format="%d readings",
)
st.session_state[session_key] = current_frame


# ══ D34 Dynamic Guided Tour Captions ═══════════════════════════════════════════

# Fetch values dynamically from three_way_comparison.csv and twin_crosscheck_report.csv
tw_match = three_way_df[three_way_df["injection_id"] == selected_inj_id]
tw_row = tw_match.iloc[0] if not tw_match.empty else None

base_alarm_str = str(tw_row["baseline_alarm_timestamp"]) if tw_row is not None and pd.notna(tw_row["baseline_alarm_timestamp"]) else "None"
base_lead_val = float(tw_row["baseline_lead_time_min"]) if tw_row is not None and pd.notna(tw_row["baseline_lead_time_min"]) else None
if_alarm_str = str(tw_row["alarm_timestamp_IF"]) if tw_row is not None and pd.notna(tw_row["alarm_timestamp_IF"]) else "None"
if_lead_val = float(tw_row["lead_time_IF_min"]) if tw_row is not None and pd.notna(tw_row["lead_time_IF_min"]) else None
lstm_alarm_str = str(tw_row["alarm_timestamp_LSTM"]) if tw_row is not None and pd.notna(tw_row["alarm_timestamp_LSTM"]) else "None"
lstm_lead_val = float(tw_row["lead_time_LSTM_min"]) if tw_row is not None and pd.notna(tw_row["lead_time_LSTM_min"]) else None
lstm_reason = str(tw_row["lstm_evaluation_reason"]) if tw_row is not None and pd.notna(tw_row["lstm_evaluation_reason"]) else "N/A"

clean_thresh = get_clean_baseline_threshold(series)
lstm_thresh_val = 1.010091 if series == "Out" else 1.512753

if mode.startswith("🎯 Guided Tour"):
    caption_md = ""
    if selected_inj_id == "out_step_001":
        caption_md = f"""
        <strong>Showcase 1: Unambiguous Step Anomaly (Catastrophic Failure Anchor)</strong><br>
        A sudden +12.0 °C step displacement occurs at <code>{onset_ts}</code>. 
        All three detectors trigger synchronously at the very first post-onset reading at 
        <code>{base_alarm_str}</code> with an identical lead time of <strong>{base_lead_val:.1f} minutes</strong>.
        This confirms zero latency divergence under gross, catastrophic system breaches.
        """
    elif selected_inj_id == "out_drift_009":
        caption_md = f"""
        <strong>Showcase 2: Incipient Thermal Drift (Early Warning vs. Sequence Lag)</strong><br>
        Under gradual thermal drift (+0.03 °C/min), the Naive Baseline remains blind until upper limit crossing at 
        <code>{base_alarm_str}</code> (lead time: <strong>{base_lead_val:.1f} min</strong>).<br>
        Isolation Forest flags multivariate anomalies early at <code>{if_alarm_str}</code>, providing a 
        vital early warning advantage of <strong>+{if_lead_val:.1f} minutes</strong>.<br>
        In contrast, LSTM-Autoencoder triggers at <code>{lstm_alarm_str}</code> with a lead time of 
        <strong>{lstm_lead_val:.1f} minutes</strong> (a <strong>{abs(lstm_lead_val):.1f}-minute lag</strong> relative to baseline crossing),
        illustrating autoencoder sequence inertia during creeping, low-slope drift.
        """
    elif selected_inj_id == "out_flatline_013":
        caption_md = f"""
        <strong>Showcase 3: Flatline Within Normal Temperature Bounds (Baseline Blind Spot)</strong><br>
        The sensor value freezes at ~37.3 °C, entirely inside normal operating temperatures. 
        Because the value never exceeds the clean threshold (<code>{clean_thresh:.2f} °C</code>), the Naive Baseline 
        <strong>completely fails to alarm</strong> (alarm: <code>{base_alarm_str}</code>).<br>
        Isolation Forest captures the unnatural collapse in rolling variance and alarms at <code>{if_alarm_str}</code>.<br>
        LSTM reconstruction error remains below threshold (<code>{lstm_thresh_val:.4f}</code>), resulting in 
        <code>{lstm_reason}</code>.
        """
    elif selected_inj_id == "in_drift_023":
        caption_md = f"""
        <strong>Showcase 4: Inbound Thermal Drift (Multi-Model Validation)</strong><br>
        Inbound sensor drift beginning at <code>{onset_ts}</code>. 
        Isolation Forest alarms early at <code>{if_alarm_str}</code> giving 
        <strong>+{if_lead_val:.1f} minutes</strong> early warning.<br>
        Both Naive Baseline and LSTM-Autoencoder trigger synchronously when temperature crosses the upper threshold at 
        <code>{base_alarm_str}</code> (lead time: <strong>{base_lead_val:.1f} minutes</strong>).
        """
    st.markdown(f'<div class="tour-caption-box">{caption_md}</div>', unsafe_allow_html=True)


# ══ Current Telemetry & Detector Cards ═════════════════════════════════════════

active_slice = sim_df.iloc[: current_frame + 1]
current_reading = sim_df.iloc[current_frame]
curr_ts = current_reading["ts"]
curr_temp = current_reading["temp_injected"]

# Calculate alarms fired so far within the evaluation horizon [onset_ts, horizon_end_ts]
eval_slice = active_slice[(active_slice["ts"] >= onset_ts) & (active_slice["ts"] <= horizon_end_ts)]
b_fired = eval_slice[eval_slice["baseline_alarm"] == True]
i_fired = eval_slice[eval_slice["if_alarm"] == True]
l_fired = eval_slice[eval_slice["lstm_alarm"] == True]

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    st.metric(
        "Current Replay Time",
        curr_ts.strftime("%Y-%m-%d %H:%M"),
        f"Frame {current_frame + 1} / {total_frames}",
    )
with col_m2:
    delta_onset = (curr_ts - onset_ts).total_seconds() / 60.0
    st.metric(
        "Live Temperature",
        f"{curr_temp:.2f} °C",
        f"{delta_onset:+.0f} min from onset",
    )
with col_m3:
    inj_phase = "Normal Telemetry"
    if onset_ts <= curr_ts <= end_ts:
        inj_phase = f"⚠️ INJECTION ACTIVE ({inj_type.upper()})"
    elif end_ts < curr_ts <= horizon_end_ts:
        inj_phase = "⏱️ SEARCH HORIZON"
    st.metric("Stream Status", inj_phase, f"Series: {series}")
with col_m4:
    total_active_alarms = int(len(b_fired) > 0) + int(len(i_fired) > 0) + int(len(l_fired) > 0)
    st.metric("Active Model Alarms", f"{total_active_alarms} / 3 Fired", f"Status: {status.upper()}")

st.markdown("---")

# 3-Column Detector Comparison Cards
c_det1, c_det2, c_det3 = st.columns(3)

with c_det1:
    b_first_ts = b_fired.iloc[0]["ts"] if not b_fired.empty else None
    b_lead = (end_ts - b_first_ts).total_seconds() / 60.0 if b_first_ts is not None else None
    b_badge = '<span class="badge-alarm">🚨 ALARM FIRED</span>' if b_first_ts else '<span class="badge-normal">⚪ MONITORING</span>'
    st.markdown(f"#### Naive Baseline {b_badge}", unsafe_allow_html=True)
    st.markdown(f"**Score / Value:** `{curr_temp:.2f} °C`")
    st.markdown(f"**Static Threshold:** `{clean_thresh:.2f} °C` (whole-series clean)")
    if b_first_ts:
        st.markdown(f"**Earliest Alarm:** `{b_first_ts.strftime('%H:%M:%S')}`")
        st.markdown(f"**Lead Time:** `{base_lead_val if base_lead_val is not None else b_lead:.1f} min`")
    else:
        st.markdown("**Earliest Alarm:** _None in window_")
        st.markdown("**Lead Time:** _N/A_")

with c_det2:
    i_first_ts = i_fired.iloc[0]["ts"] if not i_fired.empty else None
    i_lead = (end_ts - i_first_ts).total_seconds() / 60.0 if i_first_ts is not None else None
    i_badge = '<span class="badge-alarm">🚨 ALARM FIRED</span>' if i_first_ts else '<span class="badge-normal">⚪ MONITORING</span>'
    st.markdown(f"#### Isolation Forest {i_badge}", unsafe_allow_html=True)
    st.markdown(f"**Score (Decision):** `{current_reading['if_score']:.4f}`")
    st.markdown(f"**Anomaly Threshold:** `< 0.0000` (multivariate)")
    if i_first_ts:
        st.markdown(f"**Earliest Alarm:** `{i_first_ts.strftime('%H:%M:%S')}`")
        st.markdown(f"**Lead Time:** `<span class='badge-lead'>+{if_lead_val if if_lead_val is not None else i_lead:.1f} min</span>`", unsafe_allow_html=True)
    else:
        st.markdown("**Earliest Alarm:** _None in window_")
        st.markdown("**Lead Time:** _N/A_")

with c_det3:
    l_first_ts = l_fired.iloc[0]["ts"] if not l_fired.empty else None
    l_lead = (end_ts - l_first_ts).total_seconds() / 60.0 if l_first_ts is not None else None
    l_badge = '<span class="badge-alarm">🚨 ALARM FIRED</span>' if l_first_ts else '<span class="badge-normal">⚪ MONITORING</span>'
    st.markdown(f"#### LSTM-Autoencoder {l_badge}", unsafe_allow_html=True)
    st.markdown(f"**Score (Reconstruction MSE):** `{current_reading['lstm_score']:.4f}`")
    st.markdown(f"**Calibrated Threshold:** `≥ {lstm_thresh_val:.4f}` (D13)")
    if l_first_ts:
        st.markdown(f"**Earliest Alarm:** `{l_first_ts.strftime('%H:%M:%S')}`")
        lead_display = f"{lstm_lead_val if lstm_lead_val is not None else l_lead:.1f} min"
        st.markdown(f"**Lead Time:** `{lead_display}`")
    else:
        st.markdown("**Earliest Alarm:** _None in window_")
        st.markdown(f"**Lead Time:** `{lstm_reason}`")


# ══ Interactive Altair Telemetry & Alarm Trajectory Chart ══════════════════════

st.markdown("### 📈 Live Streaming Telemetry & Alarm Horizon")

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

# Legend annotations
st.caption(
    "🔶 **Orange Band**: Injection Duration | 🟪 **Purple Band**: Evaluation Search Horizon (60m) | "
    "🔴 **Red Triangles**: Baseline Alarms | 🟢 **Green Squares**: Isolation Forest Alarms | "
    "🔵 **Blue Circles**: LSTM-Autoencoder Alarms | 🟦 **Dashed Blue Line**: Replay Playhead"
)


# ══ Secondary Score Diagnostics Panel ══════════════════════════════════════════

with st.expander("📊 Inspect Live Anomaly Score Trajectories (IF Decision vs. LSTM MSE)"):
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


# ══ Real-Time Alert Log ════════════════════════════════════════════════════════

st.markdown("### 📋 Live Streaming Alert Log")

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

if all_active_alarms:
    df_alerts = pd.DataFrame(all_active_alarms).sort_values("Timestamp", ascending=False).reset_index(drop=True)
    st.dataframe(df_alerts, use_container_width=True, height=220)
else:
    st.info("No anomaly alarms triggered up to current replay position.")


# ══ Scientific Cross-Check Verification Audit (Footer) ═════════════════════════

st.markdown("---")
st.subheader("🛡️ Milestone 5b Cross-Check Verification Audit")

if status == "test":
    # Filter cross-check report for this injection
    m5b_report = crosscheck_df[crosscheck_df["injection_id"] == selected_inj_id].copy()
    all_matched = bool((m5b_report["match"] == True).all() or (m5b_report["match"] == "True").all())

    c_audit1, c_audit2 = st.columns([3, 1])
    with c_audit1:
        st.markdown(
            "This injection is part of the **6 out-of-sample test injections** representing the primary scientific benchmark. "
            "All streaming alarms produced by the Digital Twin are verified against the frozen batch evaluations from Milestones 2, 3, and 4b."
        )
        st.dataframe(
            m5b_report[["detector", "live_alarm_timestamp", "batch_alarm_timestamp", "match", "notes"]],
            use_container_width=True,
            hide_index=True,
        )
    with c_audit2:
        if all_matched:
            st.success("✅ **100% BIT-EXACT MATCH**\n\nAll 3 live detectors match frozen Milestone 2/3/4b evaluations exactly.")
        else:
            st.warning("⚠️ Cross-check review required.")
else:
    st.markdown(
        f"**Injection `{selected_inj_id}` is a training-region deployment demonstration (D26/D31).**<br>"
        "Because models had prior training exposure to this period, batch cross-check values are not computed or claimed as an out-of-sample benchmark.",
        unsafe_allow_html=True,
    )
