"""
src/isolation_forest_model.py
=============================
Trains per-series Isolation Forest models on TRAIN-split rows and scores
all rows (train + test) with a continuous anomaly score and a discrete
anomaly flag.

STRUCTURAL PROXY NOTICE
-----------------------
All labeled anomalies are SYNTHETIC PROXY CONSTRUCTS on a non-cold-chain
dataset. Isolation Forest results carry no food-safety implications.
See D5-D7 in docs/AD_LOG.md.

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D5: Rolling features are RECOMPUTED from temp_injected (not reused from the
    pre-injection stale columns already in out_labeled.csv/in_labeled.csv).
    gap_seconds does NOT need recomputation — it is timestamp-only.
    in_out_diff is OUT OF SCOPE for this milestone's feature set; cross-series
    recompute complexity is deferred. See D5 limitation note.

D6: Chronological train/test split. cutoff_ts = date_min + TRAIN_FRACTION *
    (date_max - date_min). SAME cutoff_ts applied to both series.
    IsolationForest is fit ONLY on rows where ts < cutoff_ts.
    Injections whose full window falls after cutoff_ts are TEST-eligible;
    injections fully before or straddling are reported separately.

D7: contamination='auto' (sklearn default, untuned). NOT set to the known
    injected-row fraction — that would leak test labels into the model's
    operating point. See D7 in docs/AD_LOG.md.

USAGE
-----
    python src/isolation_forest_model.py

Inputs:
    data/processed/out_labeled.csv     (M2 output, read-only)
    data/processed/in_labeled.csv      (M2 output, read-only)
    data/processed/injection_log.csv   (M2 output, read-only)

Outputs:
    models/isolation_forest_out.joblib
    models/isolation_forest_in.joblib
    data/processed/if_scores_out.csv    — all rows with IF score + discrete flag
    data/processed/if_scores_in.csv
    data/processed/injection_train_test_status.csv
"""

from __future__ import annotations

import logging
import pathlib
import sys

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

# Add src/ to path so config.py is importable when running from repo root
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from config import ROLLING_WINDOW, RANDOM_SEED, TRAIN_FRACTION, IF_RANDOM_STATE, SEARCH_HORIZON_MINUTES
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
MODELS_DIR    = REPO_ROOT / "models"

OUT_LABELED_CSV   = PROCESSED_DIR / "out_labeled.csv"
IN_LABELED_CSV    = PROCESSED_DIR / "in_labeled.csv"
INJECTION_LOG_CSV = PROCESSED_DIR / "injection_log.csv"

OUT_SCORES_CSV    = PROCESSED_DIR / "if_scores_out.csv"
IN_SCORES_CSV     = PROCESSED_DIR / "if_scores_in.csv"
STATUS_CSV        = PROCESSED_DIR / "injection_train_test_status.csv"

OUT_MODEL_PATH    = MODELS_DIR / "isolation_forest_out.joblib"
IN_MODEL_PATH     = MODELS_DIR / "isolation_forest_in.joblib"

# Feature columns for the IF model (D5: gap_seconds kept as-is; in_out_diff excluded)
FEATURE_COLS = ["temp_injected", "gap_seconds", "rolling_mean_if", "rolling_std_if"]


# ══ Feature engineering ════════════════════════════════════════════════════════

def recompute_rolling_features(df: pd.DataFrame, series_name: str) -> pd.DataFrame:
    """
    Recompute rolling_mean and rolling_std from temp_injected (D5).

    The existing rolling_mean / rolling_std columns in out_labeled.csv / in_labeled.csv
    were computed from 'temp' (the un-injected real temperature) during preprocessing.
    For the IF feature set we need features that reflect the INJECTED signal —
    otherwise the model sees a clean rolling mean even during injection windows,
    which would artificially flatten anomaly scores for step/drift injections.

    New columns: rolling_mean_if, rolling_std_if  (suffixed _if to avoid confusion)
    """
    df = df.sort_values("ts").reset_index(drop=True)
    df["rolling_mean_if"] = (
        df["temp_injected"].rolling(window=ROLLING_WINDOW, min_periods=1).mean()
    )
    df["rolling_std_if"] = (
        df["temp_injected"].rolling(window=ROLLING_WINDOW, min_periods=2).std()
    )
    logger.info(
        "Series '%s': recomputed rolling_mean_if/rolling_std_if from temp_injected "
        "(window=%d). Stale columns rolling_mean/rolling_std (from temp) NOT used.",
        series_name, ROLLING_WINDOW,
    )
    return df


def drop_nan_rows(df: pd.DataFrame, series_name: str) -> pd.DataFrame:
    """Drop rows with any NaN in FEATURE_COLS (first-row edge cases from rolling)."""
    n_before = len(df)
    df = df.dropna(subset=FEATURE_COLS).reset_index(drop=True)
    n_dropped = n_before - len(df)
    logger.info(
        "Series '%s': dropped %d NaN rows from feature set (%d → %d rows).",
        series_name, n_dropped, n_before, len(df),
    )
    return df


# ══ Injection classification ══════════════════════════════════════════════════

def classify_injections(
    inj_log: pd.DataFrame,
    labeled_dfs: dict[str, pd.DataFrame],
    cutoff_ts: pd.Timestamp,
) -> pd.DataFrame:
    """
    Classify each injection as 'train', 'test', or 'straddling' per D6:

      - 'train'      : injection end_idx timestamp < cutoff_ts (fully before split)
      - 'test'       : injection start_idx timestamp >= cutoff_ts (fully after split)
      - 'straddling' : start before, end on/after cutoff_ts

    Uses the actual row timestamps from the labeled DataFrames (not the
    start_timestamp column from injection_log, which only captures onset).
    """
    rows = []
    for _, inj in inj_log.iterrows():
        series    = inj["series"]
        df_lbl    = labeled_dfs[series]
        start_idx = int(inj["start_idx"])
        end_idx   = int(inj["end_idx"])

        start_ts = df_lbl.iloc[start_idx]["ts"]
        end_ts   = df_lbl.iloc[end_idx]["ts"]

        if end_ts < cutoff_ts:
            status = "train"
        elif start_ts >= cutoff_ts:
            status = "test"
        else:
            status = "straddling"

        rows.append({
            "injection_id": inj["injection_id"],
            "series":       series,
            "type":         inj["type"],
            "start_ts":     start_ts,
            "end_ts":       end_ts,
            "train_test_status": status,
        })

    status_df = pd.DataFrame(rows)

    # Summary
    counts = status_df["train_test_status"].value_counts()
    for s in ["train", "test", "straddling"]:
        n = int(counts.get(s, 0))
        ids = status_df[status_df["train_test_status"] == s]["injection_id"].tolist()
        logger.info("Injection status '%s': %d  → %s", s, n, ids)

    return status_df


# ══ Model fit and scoring ══════════════════════════════════════════════════════

def fit_and_score(
    df_full: pd.DataFrame,
    df_train: pd.DataFrame,
    series_name: str,
    model_path: pathlib.Path,
) -> tuple[pd.DataFrame, IsolationForest]:
    """
    Fit IsolationForest on TRAIN rows only (D6/D7).
    Score ALL rows (train+test) with decision_function (continuous) and
    predict (discrete: -1 → anomaly=True, 1 → anomaly=False).

    contamination='auto' per D7 — sklearn default, NOT set to the known
    injected-row fraction (that would leak test labels).

    n_estimators=100, max_samples='auto' — sklearn defaults, not tuned.
    """
    X_train = df_train[FEATURE_COLS].values
    X_all   = df_full[FEATURE_COLS].values

    logger.info(
        "Series '%s': fitting IsolationForest(contamination='auto', "
        "random_state=%d, n_estimators=100) on %d train rows …",
        series_name, IF_RANDOM_STATE, len(X_train),
    )
    model = IsolationForest(
        contamination="auto",
        random_state=IF_RANDOM_STATE,
        n_estimators=100,       # sklearn default
        max_samples="auto",     # sklearn default
    )
    model.fit(X_train)

    # Score all rows
    df_full = df_full.copy()
    df_full["if_score"]     = model.decision_function(X_all)   # higher = more normal
    df_full["if_anomaly"]   = model.predict(X_all) == -1       # True = IF says anomaly

    logger.info(
        "Series '%s': scored %d rows | IF-flagged anomaly rows: %d (%.2f%%)",
        series_name, len(df_full),
        int(df_full["if_anomaly"].sum()),
        100.0 * df_full["if_anomaly"].mean(),
    )

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    logger.info("Model saved: %s", model_path)

    return df_full, model


# ══ Main ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    logger.info("=== Cold Chain EWS — Isolation Forest Model (Milestone 3) ===")
    logger.info(
        "PROXY NOTICE: All labeled anomalies are SYNTHETIC PROXY CONSTRUCTS. "
        "IF results carry no food-safety implications."
    )
    logger.info(
        "D5: Rolling features recomputed from temp_injected. "
        "in_out_diff excluded (deferred, noted as limitation)."
    )
    logger.info(
        "D6: Chronological split, TRAIN_FRACTION=%.1f. "
        "D7: contamination='auto' (sklearn default, untuned).",
        TRAIN_FRACTION,
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load labeled files (M2 outputs — read-only) ────────────────────────────
    df_out = pd.read_csv(OUT_LABELED_CSV, parse_dates=["ts"])
    df_in  = pd.read_csv(IN_LABELED_CSV,  parse_dates=["ts"])
    inj_log = pd.read_csv(INJECTION_LOG_CSV, parse_dates=["start_timestamp"])
    logger.info(
        "Loaded: out_labeled (%d rows) | in_labeled (%d rows) | injection_log (%d rows)",
        len(df_out), len(df_in), len(inj_log),
    )

    # Save copies of raw labeled DataFrames before dropping NaNs for index lookup
    df_out_orig = df_out.copy()
    df_in_orig  = df_in.copy()

    # ── D5: Recompute rolling features from temp_injected ─────────────────────
    df_out = recompute_rolling_features(df_out, "Out")
    df_in  = recompute_rolling_features(df_in,  "In")

    # Drop NaN rows (first-window edge cases)
    df_out = drop_nan_rows(df_out, "Out")
    df_in  = drop_nan_rows(df_in,  "In")

    # ── D6: Compute cutoff_ts and split ───────────────────────────────────────
    cutoff_ts = compute_cutoff_ts(df_out, df_in)

    df_out_train, df_out_test = split_series(df_out, cutoff_ts, "Out")
    df_in_train,  df_in_test  = split_series(df_in,  cutoff_ts, "In")

    # ── Classify injections ───────────────────────────────────────────────────
    # Use df_*_orig so that start_idx and end_idx correspond to original row positions
    labeled_dfs = {"Out": df_out_orig, "In": df_in_orig}
    status_df   = classify_injections(inj_log, labeled_dfs, cutoff_ts)
    status_df.to_csv(STATUS_CSV, index=False)
    logger.info("Saved: %s (%d rows)", STATUS_CSV.name, len(status_df))

    # ── Fit and score ─────────────────────────────────────────────────────────
    df_out_scored, model_out = fit_and_score(df_out, df_out_train, "Out", OUT_MODEL_PATH)
    df_in_scored,  model_in  = fit_and_score(df_in,  df_in_train,  "In",  IN_MODEL_PATH)

    # ── Save scored DataFrames ────────────────────────────────────────────────
    df_out_scored.to_csv(OUT_SCORES_CSV, index=False)
    df_in_scored.to_csv(IN_SCORES_CSV,   index=False)
    logger.info("Saved: %s (%d rows)", OUT_SCORES_CSV.name, len(df_out_scored))
    logger.info("Saved: %s (%d rows)", IN_SCORES_CSV.name,  len(df_in_scored))

    # ── Summary ───────────────────────────────────────────────────────────────
    logger.info("=== Isolation Forest model training complete ===")
    logger.info("cutoff_ts     : %s", cutoff_ts)
    logger.info("TRAIN_FRACTION: %.1f (arbitrary documented default, D6)", TRAIN_FRACTION)
    logger.info("IF params     : contamination='auto', random_state=%d, n_estimators=100, max_samples='auto'",
                IF_RANDOM_STATE)
    logger.info("NOTE: in_out_diff excluded from feature set (D5 scope limitation).")


if __name__ == "__main__":
    main()
