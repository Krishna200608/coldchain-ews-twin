"""
src/baseline_and_labels.py
==========================
Computes per-series baseline thresholds from CLEAN feature files only,
then evaluates each synthetic injection for baseline alarm and irreversibility.

STRUCTURAL PROXY NOTICE
-----------------------
Thresholds, alarm timestamps, and irreversibility timestamps are all
PROXY CONSTRUCTS on a non-cold-chain dataset. They are NOT food-safety claims.
See D4 in docs/AD_LOG.md and docs/data_profile.md.

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D4 (as of 2026-09-17 fix):
  - Baseline threshold = per-series mean + K_SIGMA * std, computed ONLY
    from the clean (non-injected) feature files.
  - Baseline alarm = FIRST single reading where temp_injected > threshold.
    No sustained-duration requirement.
  - Irreversibility = first onset point where temp_injected remains
    continuously > threshold for >= D_IRREV_MINUTES.
  - Baseline lead time = irreversibility_timestamp − baseline_alarm_timestamp.
  - Search scope is bounded to [onset_ts, injection_end_ts + SEARCH_HORIZON_MINUTES].
    Any alarm or irreversibility not found within this window is null. This prevents
    unrelated future real temperature excursions (days later) from being attributed
    to the injected event — a bug in the original unbounded version.
  - All are labelled "proxy constructs"; no spoilage-kinetics source exists
    for this dataset.

CONTAMINATION GUARD
-------------------
This script loads thresholds EXCLUSIVELY from out_features.csv and
in_features.csv (the clean files saved by preprocessing.py, before any
injection). It never touches out_labeled.csv or in_labeled.csv for threshold
computation. This is enforced by:
  1. An assertion that the clean files have no 'is_injected_anomaly' column.
  2. A code comment (see _compute_threshold) documenting which file was used.

USAGE
-----
    python src/baseline_and_labels.py

Inputs  (must exist):
    data/processed/out_features.csv    — clean Out series (threshold source)
    data/processed/in_features.csv     — clean In  series (threshold source)
    data/processed/out_labeled.csv     — Out series with injected values
    data/processed/in_labeled.csv      — In  series with injected values
    data/processed/injection_log.csv   — injection audit trail

Outputs:
    data/processed/injection_evaluation_baseline.csv
"""

from __future__ import annotations

import logging
import pathlib

import pandas as pd
import numpy as np

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ══ Named constants ════════════════════════════════════════════════════════════

# K_SIGMA: number of standard deviations above the mean for the alarm threshold.
# Value = 2 is a conventional heuristic (Chebyshev / 2-sigma rule); not tuned.
# This is an ARBITRARY DOCUMENTED DEFAULT, not a cold-chain regulatory limit.
K_SIGMA: float = 2.0

# D_IRREV_MINUTES: sustained exceedance duration for "irreversibility".
# Value = 10 minutes is a documented default, NOT derived from any real
# spoilage-kinetics source — no such source exists for this proxy dataset.
# See D4 in docs/AD_LOG.md.
D_IRREV_MINUTES: float = 10.0

# SEARCH_HORIZON_MINUTES: how far past the injection window end to search for
# alarm and irreversibility events. The search window is:
#   [onset_ts, injection_end_ts + SEARCH_HORIZON_MINUTES]
# Value = 60 minutes is an ARBITRARY DOCUMENTED DEFAULT — sized to give
# D_IRREV_MINUTES (10 min) room to accumulate after a short-lived injection ends,
# without reaching into unrelated future real data hours or days later.
# Not derived from cold-chain data. See D4 (fix note) in docs/AD_LOG.md.
SEARCH_HORIZON_MINUTES: float = 60.0

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
OUT_FEATURES_CSV   = PROCESSED_DIR / "out_features.csv"
IN_FEATURES_CSV    = PROCESSED_DIR / "in_features.csv"
OUT_LABELED_CSV    = PROCESSED_DIR / "out_labeled.csv"
IN_LABELED_CSV     = PROCESSED_DIR / "in_labeled.csv"
INJECTION_LOG_CSV  = PROCESSED_DIR / "injection_log.csv"
EVALUATION_CSV     = PROCESSED_DIR / "injection_evaluation_baseline.csv"


# ══ Threshold computation ══════════════════════════════════════════════════════

def _load_clean_series(path: pathlib.Path) -> pd.DataFrame:
    """
    Load a clean feature CSV and assert it has not been contaminated by
    anomaly injection (i.e., it has no 'is_injected_anomaly' column).

    This function is the enforcement mechanism for D4's contamination guard:
    threshold statistics are computed ONLY from this return value.
    """
    df = pd.read_csv(path, parse_dates=["ts"])

    # CONTAMINATION GUARD: if this column exists, the file was overwritten
    # by anomaly_injection.py — which violates D3/D4.
    assert "is_injected_anomaly" not in df.columns, (
        f"CONTAMINATION ERROR: {path.name} contains 'is_injected_anomaly' column. "
        "The clean feature file was overwritten by injection code. "
        "Re-run preprocessing.py to restore it."
    )
    logger.info(
        "Clean file loaded: %s (%d rows) — no injected labels present.",
        path.name, len(df),
    )
    return df


def compute_threshold(df_clean: pd.DataFrame, series_name: str) -> dict:
    """
    Compute per-series baseline threshold from CLEAN temperature values.

    threshold = mean(temp) + K_SIGMA * std(temp)

    The 'temp' column used here is the REAL unperturbed temperature from the
    clean feature file — never temp_injected from the labeled file.

    Returns a dict with: mean, std, threshold, series_name, n_rows.
    """
    t = df_clean["temp"].dropna()
    mean = float(t.mean())
    std  = float(t.std())
    threshold = mean + K_SIGMA * std

    logger.info(
        "Threshold [%s]: mean=%.4f  std=%.4f  "
        "threshold=mean+%.0f*std=%.4f  (K_SIGMA=%g, arbitrary default)",
        series_name, mean, std, K_SIGMA, threshold, K_SIGMA,
    )
    return {
        "series_name": series_name,
        "n_rows":      len(t),
        "mean":        mean,
        "std":         std,
        "threshold":   threshold,
    }


# ══ Alarm and irreversibility detection ═══════════════════════════════════════

def find_baseline_alarm(
    post_onset: pd.DataFrame,
    threshold: float,
) -> pd.Timestamp | None:
    """
    Find the FIRST reading post-onset where temp_injected > threshold.

    Per D4: no sustained-duration requirement — a single reading crossing
    the threshold fires the alarm.

    Returns None if the threshold is never crossed post-onset.
    """
    crossed = post_onset[post_onset["temp_injected"] > threshold]
    if crossed.empty:
        return None
    return crossed.iloc[0]["ts"]


def find_irreversibility(
    post_onset: pd.DataFrame,
    threshold: float,
    d_irrev_minutes: float,
) -> pd.Timestamp | None:
    """
    Find the FIRST timestamp T (post-onset) such that temp_injected remains
    continuously > threshold from T until T + D_IRREV_MINUTES.

    Approach:
    - Walk through post_onset rows in time order.
    - Track the start of each "above-threshold" streak.
    - If a streak reaches d_irrev_minutes, return the streak's start timestamp.
    - A single reading at or below threshold resets the streak.

    'Continuously' is defined over real (unevenly spaced) readings:
    the streak is only broken if a reading falls AT or BELOW threshold.
    Gaps between readings do not break the streak (there is no grid to check).

    Returns None if no qualifying streak exists.

    D_IRREV_MINUTES = 10 (ARBITRARY DOCUMENTED DEFAULT — not data-derived).
    """
    streak_start: pd.Timestamp | None = None

    for _, row in post_onset.iterrows():
        if row["temp_injected"] > threshold:
            if streak_start is None:
                streak_start = row["ts"]
            elapsed_min = (row["ts"] - streak_start).total_seconds() / 60.0
            if elapsed_min >= d_irrev_minutes:
                return streak_start   # start of qualifying streak
        else:
            streak_start = None       # reset streak

    return None


# ══ Main ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    logger.info("=== Cold Chain EWS — Baseline Alarm & Labels (Milestone 2) ===")
    logger.info(
        "PROXY NOTICE: All alarm timestamps and irreversibility timestamps are "
        "SYNTHETIC PROXY CONSTRUCTS, not real food-safety events."
    )
    logger.info(
        "D_IRREV_MINUTES=%.0f — ARBITRARY DOCUMENTED DEFAULT, not derived from "
        "real spoilage-kinetics data (no such data exists for this proxy dataset).",
        D_IRREV_MINUTES,
    )

    # ── 1. Load CLEAN feature files for threshold computation (D4 guard) ──────
    # PROOF OF CONTAMINATION-FREEDOM:
    # _load_clean_series() asserts the file has no 'is_injected_anomaly' column.
    # Only out_features.csv and in_features.csv are used here — never the labeled files.
    df_out_clean = _load_clean_series(OUT_FEATURES_CSV)
    df_in_clean  = _load_clean_series(IN_FEATURES_CSV)

    stats_out = compute_threshold(df_out_clean, "Out")
    stats_in  = compute_threshold(df_in_clean,  "In")
    thresholds = {"Out": stats_out["threshold"], "In": stats_in["threshold"]}

    # ── 2. Load labeled files (for alarm evaluation only) ─────────────────────
    df_out_labeled = pd.read_csv(OUT_LABELED_CSV, parse_dates=["ts"])
    df_in_labeled  = pd.read_csv(IN_LABELED_CSV,  parse_dates=["ts"])
    labeled = {"Out": df_out_labeled, "In": df_in_labeled}

    # ── 3. Load injection log ─────────────────────────────────────────────────
    inj_log = pd.read_csv(INJECTION_LOG_CSV, parse_dates=["start_timestamp"])
    logger.info("Injection log: %d rows", len(inj_log))

    # ── 4. Evaluate each injection ────────────────────────────────────────────
    logger.info(
        "Search window: injection window + %.0f-min horizon (SEARCH_HORIZON_MINUTES, arbitrary default)",
        SEARCH_HORIZON_MINUTES,
    )
    eval_rows = []
    null_alarm_count  = 0
    null_irrev_count  = 0

    for _, row in inj_log.iterrows():
        series    = row["series"]
        df_lbl    = labeled[series]
        threshold = thresholds[series]
        start_idx = int(row["start_idx"])
        end_idx   = int(row["end_idx"])

        # Derive onset and injection-end timestamps from the labeled DataFrame.
        # end_idx is the last row INDEX of the injection window (inclusive).
        onset_ts      = df_lbl.iloc[start_idx]["ts"]
        inj_end_ts    = df_lbl.iloc[end_idx]["ts"]
        horizon_end   = inj_end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)

        # BOUNDED search window: [onset_ts, inj_end_ts + SEARCH_HORIZON_MINUTES]
        # This prevents unrelated real temperature excursions (hours/days later)
        # from being attributed to the injected event.
        # Any alarm or irreversibility not found within this window is null.
        post_onset = df_lbl[
            (df_lbl["ts"] >= onset_ts) & (df_lbl["ts"] <= horizon_end)
        ].copy()

        # (a) Baseline alarm: first single crossing within the bounded window
        alarm_ts = find_baseline_alarm(post_onset, threshold)

        # (b) Irreversibility: first sustained crossing >= D_IRREV_MINUTES (bounded)
        irrev_ts = find_irreversibility(post_onset, threshold, D_IRREV_MINUTES)

        # (c) Lead time = irrev_ts - alarm_ts (both in same direction)
        if alarm_ts is not None and irrev_ts is not None:
            lead_time_s   = (irrev_ts - alarm_ts).total_seconds()
            lead_time_min = lead_time_s / 60.0
        else:
            lead_time_s   = float("nan")
            lead_time_min = float("nan")

        if alarm_ts is None:
            null_alarm_count += 1
            logger.warning(
                "  [%s] %s: BASELINE ALARM = null "
                "(threshold not crossed within bounded window [%s, %s])",
                row["injection_id"], row["type"],
                onset_ts, horizon_end,
            )
        if irrev_ts is None:
            null_irrev_count += 1
            logger.warning(
                "  [%s] %s: IRREVERSIBILITY = null "
                "(sustained %.0f-min exceedance not reached within bounded window)",
                row["injection_id"], row["type"], D_IRREV_MINUTES,
            )

        eval_rows.append({
            "injection_id":               row["injection_id"],
            "series":                     series,
            "type":                       row["type"],
            "start_idx":                  start_idx,
            "start_timestamp":            row["start_timestamp"],
            "duration":                   row["duration"],
            "magnitude":                  row.get("magnitude", float("nan")),
            "final_magnitude":            row.get("final_magnitude", float("nan")),
            "frozen_at":                  row.get("frozen_at", float("nan")),
            "threshold":                  round(threshold, 4),
            "baseline_alarm_timestamp":   alarm_ts,
            "irreversibility_timestamp":  irrev_ts,
            "baseline_lead_time_s":       round(lead_time_s, 1)   if not pd.isna(lead_time_s)   else float("nan"),
            "baseline_lead_time_min":     round(lead_time_min, 2) if not pd.isna(lead_time_min) else float("nan"),
        })

    eval_df = pd.DataFrame(eval_rows)
    eval_df.to_csv(EVALUATION_CSV, index=False)
    logger.info("Saved: %s (%d rows)", EVALUATION_CSV.name, len(eval_df))

    # ── 5. Summary ─────────────────────────────────────────────────────────────
    logger.info("=== Evaluation summary ===")
    logger.info("  Total injections evaluated    : %d", len(eval_df))
    logger.info("  Baseline alarm = null          : %d (not crossed within bounded window)", null_alarm_count)
    logger.info("  Irreversibility = null         : %d (sustained exceedance not reached within bounded window)", null_irrev_count)

    by_type = eval_df.groupby("type").agg(
        n=("injection_id", "count"),
        alarm_null=("baseline_alarm_timestamp", lambda x: x.isna().sum()),
        irrev_null=("irreversibility_timestamp", lambda x: x.isna().sum()),
        mean_lead_min=("baseline_lead_time_min", "mean"),
    )
    logger.info("Per-type summary:\n%s", by_type.to_string())

    logger.info("=== Baseline and labels complete ===")
    print("\nPer-series thresholds:")
    for sname, s in [("Out", stats_out), ("In", stats_in)]:
        print(
            f"  {sname}: mean={s['mean']:.4f}  std={s['std']:.4f}  "
            f"threshold=mean+{K_SIGMA:.0f}*std={s['threshold']:.4f}"
        )
    print(f"\nD_IRREV_MINUTES       = {D_IRREV_MINUTES} (arbitrary documented default)")
    print(f"K_SIGMA               = {K_SIGMA} (arbitrary documented default)")
    print(f"SEARCH_HORIZON_MINUTES= {SEARCH_HORIZON_MINUTES} (arbitrary documented default)")
    print(f"\nNull alarm count       : {null_alarm_count}")
    print(f"Null irreversibility   : {null_irrev_count}")
    print("\nEvaluation table:")
    print(
        eval_df[
            ["injection_id", "type", "series", "threshold",
             "baseline_alarm_timestamp", "irreversibility_timestamp",
             "baseline_lead_time_min"]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
