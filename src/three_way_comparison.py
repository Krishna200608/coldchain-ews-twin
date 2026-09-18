"""
src/three_way_comparison.py
============================
Merges Baseline, Isolation Forest, and LSTM-Autoencoder evaluation results
into a single three-way comparison table.

STRUCTURAL PROXY NOTICE
-----------------------
All results are on SYNTHETIC PROXY CONSTRUCTS — not real cold-chain events.
See docs/AD_LOG.md (D6, D8, D13–D16).

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D8:  irreversibility_timestamp reused from M2 baseline, never recomputed.
D6:  Lead times only for test-side (status='test') injections.

NOTE: The naive threshold baseline (M2) is NOT evaluated as a point-wise
classifier here (no precision/recall reported for it). It was never
evaluated as a classifier — only as a single-reading threshold alarm.
Inventing precision/recall for it would be methodologically unsound.
The metrics comparison table covers IF vs LSTM only.

USAGE
-----
    python src/three_way_comparison.py

Inputs (read-only):
    data/processed/injection_evaluation_baseline.csv
    data/processed/if_evaluation.csv
    data/processed/lstm_evaluation.csv

Outputs:
    data/processed/three_way_comparison.csv
"""

from __future__ import annotations

import logging
import pathlib
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))

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

BASELINE_EVAL_CSV = PROCESSED_DIR / "injection_evaluation_baseline.csv"
IF_EVAL_CSV       = PROCESSED_DIR / "if_evaluation.csv"
LSTM_EVAL_CSV     = PROCESSED_DIR / "lstm_evaluation.csv"

THREE_WAY_CSV = PROCESSED_DIR / "three_way_comparison.csv"


def main() -> None:
    logger.info("=== Cold Chain EWS — Three-Way Comparison (Milestone 4b) ===")
    logger.info(
        "PROXY NOTICE: All results are on SYNTHETIC PROXY CONSTRUCTS. "
        "No food-safety claims."
    )

    # ── Load evaluation tables ─────────────────────────────────────────────────
    baseline_eval = pd.read_csv(
        BASELINE_EVAL_CSV,
        parse_dates=["baseline_alarm_timestamp", "irreversibility_timestamp", "start_timestamp"],
    )
    if_eval  = pd.read_csv(IF_EVAL_CSV,   parse_dates=["alarm_timestamp_IF",   "irreversibility_timestamp"])
    lstm_eval= pd.read_csv(LSTM_EVAL_CSV, parse_dates=["alarm_timestamp_LSTM", "irreversibility_timestamp"])

    logger.info(
        "Loaded: baseline=%d rows | IF=%d rows | LSTM=%d rows",
        len(baseline_eval), len(if_eval), len(lstm_eval),
    )

    # ── Merge into one three-way table (all 30 injections) ────────────────────
    # Start from LSTM evaluation (most complete — has lstm_evaluation_reason)
    merged = lstm_eval[[
        "injection_id", "series", "type", "train_test_status",
        "alarm_timestamp_LSTM", "lead_time_LSTM_min",
        "irreversibility_timestamp", "lstm_evaluation_reason",
    ]].copy()

    # Join IF columns
    merged = merged.merge(
        if_eval[["injection_id", "alarm_timestamp_IF", "lead_time_IF_min"]],
        on="injection_id",
        how="left",
    )

    # Join baseline columns
    merged = merged.merge(
        baseline_eval[[
            "injection_id",
            "baseline_alarm_timestamp",
            "baseline_lead_time_min",
        ]],
        on="injection_id",
        how="left",
    )

    # Reorder columns
    merged = merged[[
        "injection_id", "series", "type", "train_test_status",
        "irreversibility_timestamp",
        "baseline_alarm_timestamp", "baseline_lead_time_min",
        "alarm_timestamp_IF",       "lead_time_IF_min",
        "alarm_timestamp_LSTM",     "lead_time_LSTM_min",
        "lstm_evaluation_reason",
    ]]

    merged.to_csv(THREE_WAY_CSV, index=False)
    logger.info("Saved: %s (%d rows)", THREE_WAY_CSV.name, len(merged))

    # ── Test-side summary ──────────────────────────────────────────────────────
    test_df = merged[merged["train_test_status"] == "test"].copy()
    logger.info(
        "\n=== THREE-WAY LEAD TIME COMPARISON (test-side injections only) ===\n"
        "NOTE: Baseline is NOT evaluated point-wise (no classifier threshold).\n"
        "      Precision/Recall/F1 are ONLY reported for IF vs LSTM.\n"
    )
    logger.info(
        "%-25s %-5s %-10s %10s %10s %10s %s",
        "injection_id", "ser", "type",
        "base(min)", "IF(min)", "LSTM(min)", "lstm_reason",
    )
    logger.info("-" * 90)
    for _, r in test_df.iterrows():
        b = f"{r['baseline_lead_time_min']:.1f}" if pd.notna(r["baseline_lead_time_min"]) else "null"
        i = f"{r['lead_time_IF_min']:.1f}"       if pd.notna(r["lead_time_IF_min"])       else "null"
        l = f"{r['lead_time_LSTM_min']:.1f}"     if pd.notna(r["lead_time_LSTM_min"])     else "null"
        logger.info(
            "%-25s %-5s %-10s %10s %10s %10s %s",
            r["injection_id"], r["series"], r["type"], b, i, l, r["lstm_evaluation_reason"],
        )

    # Per-type analysis
    logger.info("\n=== PER-TYPE TEST INJECTION SUMMARY ===")
    for anom_type in ["step", "drift", "flatline"]:
        sub = test_df[test_df["type"] == anom_type]
        if sub.empty:
            continue
        def fmt_lead(col):
            valid = sub[col].dropna()
            if valid.empty:
                return "all null"
            return f"mean={valid.mean():.1f} min (n={len(valid)}/{len(sub)})"
        logger.info(
            "  %s: baseline=%s | IF=%s | LSTM=%s",
            anom_type,
            fmt_lead("baseline_lead_time_min"),
            fmt_lead("lead_time_IF_min"),
            fmt_lead("lead_time_LSTM_min"),
        )

    # Head-to-head: where LSTM beats IF and vice versa
    logger.info("\n=== HEAD-TO-HEAD: LSTM vs IF (test-side lead times) ===")
    has_both = test_df.dropna(subset=["lead_time_LSTM_min", "lead_time_IF_min"])
    for _, r in has_both.iterrows():
        lstm_lt = r["lead_time_LSTM_min"]
        if_lt   = r["lead_time_IF_min"]
        delta   = lstm_lt - if_lt
        winner  = "LSTM" if delta > 0 else ("IF" if delta < 0 else "TIE")
        logger.info(
            "  %-25s | LSTM=%.1f | IF=%.1f | delta=%.1f | winner=%s",
            r["injection_id"], lstm_lt, if_lt, delta, winner,
        )

    only_lstm_alarm = test_df[test_df["lead_time_LSTM_min"].notna() & test_df["lead_time_IF_min"].isna()]
    only_if_alarm   = test_df[test_df["lead_time_IF_min"].notna()   & test_df["lead_time_LSTM_min"].isna()]
    both_null       = test_df[test_df["lead_time_IF_min"].isna()    & test_df["lead_time_LSTM_min"].isna()]

    if not only_lstm_alarm.empty:
        logger.info("LSTM-only alarm (IF null): %s", only_lstm_alarm["injection_id"].tolist())
    if not only_if_alarm.empty:
        logger.info("IF-only alarm (LSTM null): %s",   only_if_alarm["injection_id"].tolist())
    if not both_null.empty:
        logger.info("Both null (neither alerted): %s", both_null["injection_id"].tolist())

    logger.info("=== Three-Way Comparison complete ===")


if __name__ == "__main__":
    main()
