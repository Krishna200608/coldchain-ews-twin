"""
src/preprocessing.py
====================
Loads the raw proxy dataset, deduplicates, splits into Out/In series,
adds within-series and cross-series features, and saves clean reference files.

STRUCTURAL PROXY NOTICE
-----------------------
IOT-temp.csv is a generic IoT temperature sensor log, NOT real
refrigerated-transport telemetry. See README.md and docs/data_profile.md.

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D1 (no resampling): All features are computed from real observed readings only.
    Fixed-count windows (ROLLING_WINDOW) over consecutive real readings — not
    fixed time spans, not interpolated grids.
D2 (independent series): "Out" and "In" are treated as two independent series.
    gap_seconds is computed WITHIN each series (time since the previous reading
    of the SAME tag). Cross-series matching uses merge_asof with a time cap;
    it is additive metadata, not resampling.

USAGE
-----
    python src/preprocessing.py

Outputs:
    data/processed/out_features.csv   — clean Out series (NEVER modify after save)
    data/processed/in_features.csv    — clean In  series (NEVER modify after save)
"""

from __future__ import annotations

import logging
import pathlib
import sys

import numpy as np
import pandas as pd

from config import ROLLING_WINDOW, MAX_MATCH_MINUTES

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW_CSV = REPO_ROOT / "data" / "raw" / "IOT-temp.csv"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
OUT_FEATURES_CSV = PROCESSED_DIR / "out_features.csv"
IN_FEATURES_CSV = PROCESSED_DIR / "in_features.csv"


# ══ Step 1: Load and clean ═════════════════════════════════════════════════════

def load_and_clean() -> pd.DataFrame:
    """
    Load IOT-temp.csv, parse timestamps (dayfirst=True — required by DD-MM-YYYY
    format), sort by timestamp, and drop exact duplicate rows.

    Expected transition: 97,606 → 97,605 rows (one exact duplicate confirmed
    in Milestone 1 EDA; see docs/data_profile.md §8).

    Returns
    -------
    pd.DataFrame
        Sorted, deduplicated DataFrame with 'ts' column added.
    """
    logger.info("Loading: %s", RAW_CSV)
    df = pd.read_csv(RAW_CSV)

    # CRITICAL: noted_date is DD-MM-YYYY HH:MM. Without dayfirst=True,
    # ~47,662 rows silently produce NaT (see docs/data_profile.md §5).
    df["ts"] = pd.to_datetime(df["noted_date"], dayfirst=True, errors="coerce")
    n_fail = df["ts"].isna().sum()
    if n_fail > 0:
        logger.warning("Timestamp parse failures: %d — check dayfirst=True", n_fail)

    df = df.sort_values("ts").reset_index(drop=True)

    n_before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    n_after = len(df)
    n_dropped = n_before - n_after
    logger.info(
        "Dedup: %d → %d rows (dropped %d exact duplicate(s))",
        n_before, n_after, n_dropped,
    )
    if n_after != 97_605:
        logger.warning(
            "Expected 97,605 rows after dedup but got %d — "
            "verify against docs/data_profile.md",
            n_after,
        )

    return df


# ══ Step 2: Within-series features ════════════════════════════════════════════

def add_within_series_features(df: pd.DataFrame, series_name: str) -> pd.DataFrame:
    """
    Add per-series features to a single-tag DataFrame (Out or In).

    All features are computed from REAL observed readings only (D1).
    gap_seconds uses .diff() within this series — it is NOT the global
    inter-row gap computed across all tags in Milestone 1's EDA (D2).

    Features added
    --------------
    gap_seconds  : seconds since the previous reading IN THIS SERIES.
                   First row is NaN (no preceding reading in this series).
    rolling_mean : rolling mean of 'temp' over the last ROLLING_WINDOW readings.
    rolling_std  : rolling std of 'temp' over the last ROLLING_WINDOW readings.
                   NaN for fewer than 2 readings in the window (min_periods=2).
    """
    df = df.sort_values("ts").reset_index(drop=True)

    # Within-series time gap (D2: only looks at readings with the same tag)
    df["gap_seconds"] = df["ts"].diff().dt.total_seconds()

    # Rolling stats on real temperature (D1: no interpolated fill)
    df["rolling_mean"] = (
        df["temp"].rolling(window=ROLLING_WINDOW, min_periods=1).mean()
    )
    df["rolling_std"] = (
        df["temp"].rolling(window=ROLLING_WINDOW, min_periods=2).std()
    )

    gap = df["gap_seconds"].dropna()
    logger.info(
        "Series '%s': %d rows | gap_seconds [min=%.0f s, median=%.0f s, "
        "mean=%.1f s, max=%.0f s]",
        series_name, len(df),
        gap.min(), gap.median(), gap.mean(), gap.max(),
    )
    return df


# ══ Step 3: Cross-series feature (in_out_diff) ════════════════════════════════

def add_in_out_diff(
    df_target: pd.DataFrame,
    df_other: pd.DataFrame,
    target_name: str,
    other_name: str,
) -> tuple[pd.DataFrame, dict]:
    """
    Add 'in_out_diff' to df_target: the temperature difference between each
    target-series reading and the temporally nearest reading in df_other.

    Matching uses pd.merge_asof(direction='nearest') — nearest neighbour only,
    NO interpolation (D1). If the nearest reading in df_other exceeds
    MAX_MATCH_MINUTES, the diff is set to NaN.

    in_out_diff = df_target['temp'] − nearest df_other['temp']

    Returns
    -------
    df_target : pd.DataFrame with 'in_out_diff' column added
    stats     : dict with n_valid, n_nan, pct_valid, pct_nan
    """
    tolerance = pd.Timedelta(minutes=MAX_MATCH_MINUTES)

    left = (
        df_target.sort_values("ts")
        .reset_index(drop=True)[["ts", "temp"]]
        .rename(columns={"temp": "temp_target"})
    )
    right = (
        df_other.sort_values("ts")
        .reset_index(drop=True)[["ts", "temp"]]
        .rename(columns={"temp": "temp_other"})
    )

    # merge_asof requires both DataFrames sorted on the join key
    merged = pd.merge_asof(
        left,
        right,
        on="ts",
        direction="nearest",
        tolerance=tolerance,
    )

    diff = merged["temp_target"] - merged["temp_other"]
    n_total = len(diff)
    n_valid = int(diff.notna().sum())
    n_nan = int(diff.isna().sum())
    pct_valid = 100.0 * n_valid / n_total
    pct_nan   = 100.0 * n_nan   / n_total

    logger.info(
        "in_out_diff  '%s'→'%s': valid=%d (%.2f%%)  "
        "NaN (gap >%d min)=%d (%.2f%%)",
        target_name, other_name,
        n_valid, pct_valid,
        MAX_MATCH_MINUTES,
        n_nan, pct_nan,
    )

    # Re-align with df_target (already sorted by ts above)
    df_target = df_target.sort_values("ts").reset_index(drop=True)
    df_target["in_out_diff"] = diff.values

    stats = {
        "n_valid": n_valid, "n_nan": n_nan,
        "pct_valid": pct_valid, "pct_nan": pct_nan,
    }
    return df_target, stats


# ══ Main ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    logger.info("=== Cold Chain EWS — Preprocessing (Milestone 2) ===")
    logger.info(
        "PROXY NOTICE: IOT-temp.csv is a structural proxy, not real "
        "cold-chain telemetry. See README.md."
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # ── 1. Load & clean ───────────────────────────────────────────────────────
    df = load_and_clean()

    # ── 2. Split by tag (D2: independent series) ──────────────────────────────
    df_out = df[df["out/in"] == "Out"].copy()
    df_in  = df[df["out/in"] == "In"].copy()
    logger.info("Split → df_out: %d rows | df_in: %d rows", len(df_out), len(df_in))

    # ── 3. Within-series features ─────────────────────────────────────────────
    df_out = add_within_series_features(df_out, "Out")
    df_in  = add_within_series_features(df_in,  "In")

    # ── 4. Cross-series in_out_diff ───────────────────────────────────────────
    df_out, stats_out = add_in_out_diff(df_out, df_in,  "Out", "In")
    df_in,  stats_in  = add_in_out_diff(df_in,  df_out, "In",  "Out")

    # ── 5. Save CLEAN reference files ─────────────────────────────────────────
    # These files must NEVER be overwritten by anomaly_injection.py.
    # baseline_and_labels.py reads ONLY these files for threshold computation.
    df_out.to_csv(OUT_FEATURES_CSV, index=False)
    df_in.to_csv(IN_FEATURES_CSV,   index=False)
    logger.info("Saved (CLEAN): %s (%d rows)", OUT_FEATURES_CSV.name, len(df_out))
    logger.info("Saved (CLEAN): %s (%d rows)", IN_FEATURES_CSV.name,  len(df_in))

    # ── Summary ───────────────────────────────────────────────────────────────
    logger.info("=== Preprocessing complete ===")
    logger.info(
        "in_out_diff: Out→In: %.2f%% valid, %.2f%% NaN | In→Out: %.2f%% valid, %.2f%% NaN",
        stats_out["pct_valid"], stats_out["pct_nan"],
        stats_in["pct_valid"],  stats_in["pct_nan"],
    )

    # Show 3 example rows per series demonstrating within-series gap_seconds
    logger.info("--- Sample Out rows (gap_seconds is within-Out-series) ---")
    print(df_out[["ts", "temp", "gap_seconds", "rolling_mean", "in_out_diff"]].iloc[1:4].to_string())
    logger.info("--- Sample In rows (gap_seconds is within-In-series) ---")
    print(df_in[["ts", "temp", "gap_seconds", "rolling_mean", "in_out_diff"]].iloc[1:4].to_string())


if __name__ == "__main__":
    main()
