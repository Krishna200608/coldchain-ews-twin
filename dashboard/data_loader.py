"""
dashboard/data_loader.py
========================
Cached dataset loaders, metadata tables, and D32 startup verification checks.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.constants import (
    DATA_DIR,
    K_SIGMA,
    MODELS_DIR,
    REPO_ROOT,
)


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
    return float(t.mean() + K_SIGMA * t.std())
