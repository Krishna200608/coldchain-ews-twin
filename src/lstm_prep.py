"""
src/lstm_prep.py
================
Prepares sliding window arrays and normalization parameters for the LSTM-Autoencoder
anomaly detector (Milestone 4a).

STRUCTURAL PROXY NOTICE
-----------------------
All data processed here originates from a generic IoT temperature sensor log (IOT-temp.csv),
NOT operational refrigerated-transport telemetry. All injected anomalies are synthetic
proxy constructs. Windows and normalization stats carry no food-safety significance.
See docs/AD_LOG.md (decisions D1, D2, D9, D10, D11).

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D9:  Count-based sliding windowing (LSTM_WINDOW_LENGTH = 30, LSTM_WINDOW_STRIDE = 5).
     Separate windowing per series (Out, In).
D10: Feature vector per timestep: [temp_injected_norm, log_gap_seconds_norm].
     Normalization mean/std computed EXCLUSIVELY from the full TRAIN split (ts < cutoff_ts),
     never from test rows.
D11: Chronological validation slice carved from the tail of the train split:
     LSTM_VAL_FRACTION = 0.1 (train_train = earliest 90%, val = latest 10%).
     Windows are formed strictly within train_train and val respectively (zero crossing).
     Test-period windows are strictly NOT constructed in this milestone (deferred to M4b).

OUTPUTS
-------
- data/processed/lstm_norm_stats_out.json
- data/processed/lstm_norm_stats_in.json
- data/processed/lstm_windows_out_train.npz   shape: (N_train, 30, 2)
- data/processed/lstm_windows_out_val.npz     shape: (N_val, 30, 2)
- data/processed/lstm_windows_in_train.npz    shape: (N_train, 30, 2)
- data/processed/lstm_windows_in_val.npz      shape: (N_val, 30, 2)
"""

from __future__ import annotations

import json
import logging
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from config import (
    LSTM_VAL_FRACTION,
    LSTM_WINDOW_LENGTH,
    LSTM_WINDOW_STRIDE,
    TRAIN_FRACTION,
)
from split_utils import compute_cutoff_ts, split_series

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT     = pathlib.Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

OUT_LABELED_CSV = PROCESSED_DIR / "out_labeled.csv"
IN_LABELED_CSV  = PROCESSED_DIR / "in_labeled.csv"


def extract_windows(
    arr: np.ndarray,
    window_length: int = LSTM_WINDOW_LENGTH,
    stride: int = LSTM_WINDOW_STRIDE,
) -> tuple[np.ndarray, list[tuple[int, int]]]:
    """
    Extract contiguous, non-crossing count-based sliding windows from a 2D array.

    Parameters
    ----------
    arr : np.ndarray
        Array of shape (n_samples, n_features).
    window_length : int
        Count of consecutive observations per window.
    stride : int
        Step size (count of observations) between window starts.

    Returns
    -------
    windows : np.ndarray
        Array of shape (n_windows, window_length, n_features).
    ranges : list[tuple[int, int]]
        List of (start_idx, end_idx) tuples representing inclusive row index spans.
    """
    n_samples = len(arr)
    windows = []
    ranges = []

    for start in range(0, n_samples - window_length + 1, stride):
        end = start + window_length  # slice is arr[start:end]
        windows.append(arr[start:end])
        ranges.append((start, end - 1))

    if not windows:
        return np.empty((0, window_length, arr.shape[1]), dtype=arr.dtype), []

    return np.array(windows, dtype=arr.dtype), ranges


def process_series(
    df_raw: pd.DataFrame,
    series_name: str,
    cutoff_ts: pd.Timestamp,
) -> dict:
    """
    Process one series (Out or In):
    1. Drop initial NaN row (gap_seconds)
    2. Chronologically split into train and test
    3. Carve train_train (90%) and val (10%) from train
    4. Compute train-only normalization stats
    5. Construct strictly non-crossing sliding windows for train_train and val
    6. Save JSON stats and .npz window arrays
    """
    logger.info("=================================================================")
    logger.info("Processing Series: '%s'", series_name)
    logger.info("=================================================================")

    # 1. Drop NaN edge cases (same as M3: gap_seconds NaN at index 0)
    n_init = len(df_raw)
    df = df_raw.dropna(subset=["gap_seconds"]).reset_index(drop=True).copy()
    logger.info("Dropped initial NaN rows: %d → %d rows", n_init, len(df))

    # Add log1p(gap_seconds)
    df["log_gap_seconds"] = np.log1p(df["gap_seconds"])

    # 2. Chronological train/test split (D6)
    df_train, df_test = split_series(df, cutoff_ts, series_name)
    n_train = len(df_train)
    n_test  = len(df_test)

    # 3. Carve validation slice from TAIL of train period (D11)
    n_val = int(round(n_train * LSTM_VAL_FRACTION))
    df_train_train = df_train.iloc[:-n_val].copy().reset_index(drop=True)
    df_val         = df_train.iloc[-n_val:].copy().reset_index(drop=True)

    logger.info(
        "Row breakdown: train_train=%d (%.1f%%) | val=%d (%.1f%%) | test=%d (%.1f%%) [Total train=%d]",
        len(df_train_train), 100.0 * len(df_train_train) / n_train,
        len(df_val), 100.0 * len(df_val) / n_train,
        n_test, 100.0 * n_test / len(df),
        n_train,
    )

    # 4. Normalization statistics from FULL TRAIN SPLIT (train_train + val)
    # NOTE: These statistics are computed EXCLUSIVELY on historical training telemetry.
    # The test split is NEVER observed or included in mean/std calculations.
    norm_stats = {
        "series": series_name,
        "n_train_rows_total": int(n_train),
        "n_train_train_rows": int(len(df_train_train)),
        "n_val_rows": int(len(df_val)),
        "n_test_rows": int(n_test),
        "cutoff_ts": str(cutoff_ts),
        "temp_injected_mean": float(df_train["temp_injected"].mean()),
        "temp_injected_std": float(df_train["temp_injected"].std()),
        "log_gap_seconds_mean": float(df_train["log_gap_seconds"].mean()),
        "log_gap_seconds_std": float(df_train["log_gap_seconds"].std()),
    }

    stats_file = PROCESSED_DIR / f"lstm_norm_stats_{series_name.lower()}.json"
    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(norm_stats, f, indent=2)
    logger.info("Saved train-only normalization stats to: %s", stats_file.name)
    logger.info(
        "  temp_injected   : mean=%.4f, std=%.4f",
        norm_stats["temp_injected_mean"], norm_stats["temp_injected_std"],
    )
    logger.info(
        "  log_gap_seconds : mean=%.4f, std=%.4f",
        norm_stats["log_gap_seconds_mean"], norm_stats["log_gap_seconds_std"],
    )

    # Apply z-score normalization using full-train stats
    t_mean, t_std = norm_stats["temp_injected_mean"], norm_stats["temp_injected_std"]
    g_mean, g_std = norm_stats["log_gap_seconds_mean"], norm_stats["log_gap_seconds_std"]

    def z_score_features(d: pd.DataFrame) -> np.ndarray:
        t_z = (d["temp_injected"].values - t_mean) / t_std
        g_z = (d["log_gap_seconds"].values - g_mean) / g_std
        return np.column_stack([t_z, g_z])

    X_train_train = z_score_features(df_train_train)
    X_val         = z_score_features(df_val)

    # 5. Extract non-crossing sliding windows
    windows_train, ranges_train = extract_windows(X_train_train)
    windows_val,   ranges_val   = extract_windows(X_val)

    logger.info(
        "Windows generated: train_train=%d windows (shape: %s) | val=%d windows (shape: %s)",
        len(windows_train), windows_train.shape,
        len(windows_val), windows_val.shape,
    )

    # Spot check first and last window ranges to verify no boundary crossing
    logger.info(
        "  train_train boundary check: first window rows [%d, %d] | last window rows [%d, %d] (max valid: %d)",
        ranges_train[0][0], ranges_train[0][1],
        ranges_train[-1][0], ranges_train[-1][1],
        len(df_train_train) - 1,
    )
    assert ranges_train[-1][1] < len(df_train_train), "Train window crossed train_train boundary!"

    logger.info(
        "  val boundary check:         first window rows [%d, %d] | last window rows [%d, %d] (max valid: %d)",
        ranges_val[0][0], ranges_val[0][1],
        ranges_val[-1][0], ranges_val[-1][1],
        len(df_val) - 1,
    )
    assert ranges_val[-1][1] < len(df_val), "Val window crossed val boundary!"

    # 6. Save .npz files
    train_npz_path = PROCESSED_DIR / f"lstm_windows_{series_name.lower()}_train.npz"
    val_npz_path   = PROCESSED_DIR / f"lstm_windows_{series_name.lower()}_val.npz"

    np.savez_compressed(train_npz_path, windows=windows_train)
    np.savez_compressed(val_npz_path,   windows=windows_val)

    logger.info("Saved: %s (%d windows)", train_npz_path.name, len(windows_train))
    logger.info("Saved: %s (%d windows)", val_npz_path.name, len(windows_val))

    return {
        "norm_stats": norm_stats,
        "train_windows_shape": windows_train.shape,
        "val_windows_shape": windows_val.shape,
        "train_first_range": ranges_train[0],
        "train_last_range": ranges_train[-1],
        "val_first_range": ranges_val[0],
        "val_last_range": ranges_val[-1],
    }


def main() -> None:
    logger.info("=== Cold Chain EWS — LSTM Data Prep (Milestone 4a) ===")
    logger.info(
        "PROXY NOTICE: All windows and normalization stats are computed on SYNTHETIC PROXY telemetry."
    )
    logger.info(
        "D9: Count-based windowing: length=%d, stride=%d",
        LSTM_WINDOW_LENGTH, LSTM_WINDOW_STRIDE,
    )
    logger.info(
        "D10: Features [temp_injected, log1p(gap_seconds)], train-only normalization."
    )
    logger.info(
        "D11: Validation fraction=%.2f carved from train tail. Test period untouched.",
        LSTM_VAL_FRACTION,
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    df_out = pd.read_csv(OUT_LABELED_CSV, parse_dates=["ts"])
    df_in  = pd.read_csv(IN_LABELED_CSV,  parse_dates=["ts"])

    # Compute cutoff_ts from loaded data
    cutoff_ts = compute_cutoff_ts(df_out, df_in)
    logger.info("M4a cutoff_ts: %s", cutoff_ts)

    # Process Out and In series
    out_results = process_series(df_out, "Out", cutoff_ts)
    in_results  = process_series(df_in,  "In",  cutoff_ts)

    logger.info("=== LSTM Data Preparation Complete ===")
    logger.info("NOTE: No test windows were generated (deferred to Milestone 4b scoring).")
    logger.info("NOTE: No local/CPU training executed (deferred to Colab GPU T4 session).")


if __name__ == "__main__":
    main()
