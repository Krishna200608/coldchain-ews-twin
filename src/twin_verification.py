"""
src/twin_verification.py
========================
Row-by-row verification of the SimPy digital twin replay output against
the original labeled CSV source data (Milestone 5a).

STRUCTURAL PROXY NOTICE
-----------------------
All data derives from IOT-temp.csv — synthetic proxy telemetry.
See docs/AD_LOG.md (D1–D19).

VERIFICATION LOGIC
------------------
For each series (Out and In):

  1. ROW COUNT CHECK
     twin_replay_log_{out,in}.csv must have exactly (N − 1) rows, where N
     is the row count of out/in_labeled.csv.  (One row is dropped per series
     for the initial NaN gap_seconds — same as in digital_twin.py and M3/M4.)

  2. COLUMN VALUE MATCH (exact, not approximate)
     For every row, verify:
       - temp_injected         (float; compared via np.isclose, rtol=0, atol=1e-9)
       - is_injected_anomaly   (bool)
       - injection_type        (string)
     Report exact mismatch counts.  If any mismatch exists, report the first
     10 offending rows in detail.

  3. SIM_TIME CONSISTENCY CHECK
     For row i, compute:
       delta_sim  = sim_time_received[i] - sim_time_received[0]
       delta_real = (ts[i] - ts[0]).total_seconds()
     max |delta_sim - delta_real| must be ~0 (floating-point epsilon only)
     when TRANSIT_LATENCY_SECONDS = 0.0.
     Report the maximum absolute discrepancy found, per series.
     DO NOT assume it is ~0 — measure and report the actual value.

USAGE
-----
    python src/twin_verification.py

Inputs (read-only):
    data/processed/out_labeled.csv
    data/processed/in_labeled.csv
    data/processed/twin_replay_log_out.csv
    data/processed/twin_replay_log_in.csv
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

OUT_LABELED_CSV     = PROCESSED_DIR / "out_labeled.csv"
IN_LABELED_CSV      = PROCESSED_DIR / "in_labeled.csv"
REPLAY_LOG_OUT_CSV  = PROCESSED_DIR / "twin_replay_log_out.csv"
REPLAY_LOG_IN_CSV   = PROCESSED_DIR / "twin_replay_log_in.csv"


# ══ Per-series verification ════════════════════════════════════════════════════

def verify_series(
    df_source_full: pd.DataFrame,
    df_replay: pd.DataFrame,
    series_name: str,
) -> dict:
    """
    Run all three verification checks for one series.
    Returns a dict summarising all findings.  Never silently passes mismatches.
    """
    logger.info("=" * 65)
    logger.info("Verifying Series: '%s'", series_name)
    logger.info("=" * 65)

    # ── Prepare source reference (drop initial NaN-gap row, same as digital_twin.py) ──
    # Sort by (ts ASC, gap_seconds DESC) with kind='stable' to match digital_twin.py's
    # order: the non-zero inter-minute gap occurs at the minute boundary.
    df_source = (
        df_source_full
        .dropna(subset=["gap_seconds"])
        .copy()
        .sort_values(["ts", "gap_seconds"], ascending=[True, False], kind="stable")
        .reset_index(drop=True)
    )
    # df_replay is already in emission order from digital_twin.py
    df_replay = df_replay.copy().reset_index(drop=True)

    n_source = len(df_source)
    n_replay = len(df_replay)
    n_source_full = len(df_source_full)

    logger.info(
        "Source: %d original rows → %d after dropping 1 NaN-gap row",
        n_source_full, n_source,
    )
    logger.info("Replay: %d rows", n_replay)

    # ── CHECK 1: Row count ─────────────────────────────────────────────────────
    row_count_match = (n_source == n_replay)
    if row_count_match:
        logger.info("CHECK 1 — Row count: PASS (%d == %d)", n_source, n_replay)
    else:
        logger.error(
            "CHECK 1 — Row count: FAIL (%d source vs %d replay) ← MISMATCH",
            n_source, n_replay,
        )

    if n_source != n_replay:
        # Cannot proceed with row-by-row checks if row counts differ
        return {
            "series": series_name,
            "row_count_source": n_source,
            "row_count_replay": n_replay,
            "row_count_match": False,
            "temp_injected_mismatches": None,
            "is_injected_anomaly_mismatches": None,
            "injection_type_mismatches": None,
            "max_abs_time_delta_discrepancy_s": None,
            "all_checks_passed": False,
        }

    # ── CHECK 2: Column value match (row-by-row, exact) ────────────────────────

    # temp_injected — float comparison with floating-point tolerance
    temp_source = df_source["temp_injected"].values
    temp_replay = df_replay["temp_injected"].values
    temp_close  = np.isclose(temp_source, temp_replay, rtol=0.0, atol=1e-9)
    n_temp_mismatch = int((~temp_close).sum())

    # is_injected_anomaly — bool
    bool_source = df_source["is_injected_anomaly"].astype(bool).values
    bool_replay = df_replay["is_injected_anomaly"].astype(bool).values
    bool_match  = (bool_source == bool_replay)
    n_bool_mismatch = int((~bool_match).sum())

    # injection_type — string (NaN-safe: treat NaN==NaN as equal)
    # Both source and replay store float NaN for non-injected rows;
    # string comparison NaN != NaN so we fill with a sentinel first.
    _NAN_SENTINEL = "__NO_INJECTION__"
    itype_source = df_source["injection_type"].fillna(_NAN_SENTINEL).astype(str).str.strip().values
    itype_replay = df_replay["injection_type"].fillna(_NAN_SENTINEL).astype(str).str.strip().values
    itype_match  = (itype_source == itype_replay)
    n_itype_mismatch = int((~itype_match).sum())

    for col, n_mis, label in [
        ("temp_injected",       n_temp_mismatch,  "float, atol=1e-9"),
        ("is_injected_anomaly", n_bool_mismatch,  "bool exact"),
        ("injection_type",      n_itype_mismatch, "str exact"),
    ]:
        status = "PASS" if n_mis == 0 else "FAIL"
        logger.info(
            "CHECK 2 — %-22s [%s]: %s — %d mismatch(es) / %d rows",
            col, label, status, n_mis, n_source,
        )

    # Detail on mismatches if any
    any_value_mismatch = n_temp_mismatch + n_bool_mismatch + n_itype_mismatch
    if any_value_mismatch > 0:
        combined_bad = (~temp_close) | (~bool_match) | (~itype_match)
        bad_idx = np.where(combined_bad)[0][:10]
        logger.error(
            "First up to 10 mismatch rows (source vs replay) for series '%s':",
            series_name,
        )
        for i in bad_idx:
            logger.error(
                "  row %d: src_temp=%.6f vs rep_temp=%.6f | "
                "src_bool=%s vs rep_bool=%s | "
                "src_type='%s' vs rep_type='%s'",
                i,
                temp_source[i], temp_replay[i],
                bool_source[i], bool_replay[i],
                itype_source[i], itype_replay[i],
            )

    # ── CHECK 3: SimTime consistency ───────────────────────────────────────────
    # delta_sim[i]  = sim_time_received[i] - sim_time_received[0]
    # delta_real[i] = (ts[i] - ts[0]).total_seconds()
    # When TRANSIT_LATENCY_SECONDS=0, these must be identical up to float precision.
    ts_source    = pd.to_datetime(df_source["ts"])
    ts_replay    = pd.to_datetime(df_replay["ts"])
    sim_times    = df_replay["sim_time_received"].values

    delta_sim  = sim_times - sim_times[0]
    delta_real = (ts_source - ts_source.iloc[0]).dt.total_seconds().values

    abs_discrepancy = np.abs(delta_sim - delta_real)
    max_abs_disc    = float(np.max(abs_discrepancy))
    mean_abs_disc   = float(np.mean(abs_discrepancy))

    time_check_label = "PASS (≤ float epsilon)" if max_abs_disc < 1e-6 else "WARN (> 1e-6 s)"
    logger.info(
        "CHECK 3 — SimTime consistency: %s — max |Δsim − Δreal| = %.2e s | "
        "mean |Δsim − Δreal| = %.2e s",
        time_check_label, max_abs_disc, mean_abs_disc,
    )

    if max_abs_disc >= 1e-6:
        # Find the worst row
        worst_idx = int(np.argmax(abs_discrepancy))
        logger.warning(
            "Worst row %d: delta_sim=%.6f s, delta_real=%.6f s, diff=%.2e s",
            worst_idx, delta_sim[worst_idx], delta_real[worst_idx],
            abs_discrepancy[worst_idx],
        )

    # ── Overall pass/fail ──────────────────────────────────────────────────────
    all_passed = (
        row_count_match and
        any_value_mismatch == 0 and
        max_abs_disc < 1e-6
    )

    logger.info(
        "Series '%s' OVERALL: %s",
        series_name, "ALL CHECKS PASSED ✓" if all_passed else "ONE OR MORE CHECKS FAILED ✗",
    )

    return {
        "series": series_name,
        "row_count_source": n_source,
        "row_count_replay": n_replay,
        "row_count_match": row_count_match,
        "temp_injected_mismatches": n_temp_mismatch,
        "is_injected_anomaly_mismatches": n_bool_mismatch,
        "injection_type_mismatches": n_itype_mismatch,
        "max_abs_time_delta_discrepancy_s": max_abs_disc,
        "mean_abs_time_delta_discrepancy_s": mean_abs_disc,
        "all_checks_passed": all_passed,
    }


# ══ Main ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    logger.info("=== Cold Chain EWS — Twin Verification (Milestone 5a) ===")
    logger.info(
        "PROXY NOTICE: Verifying synthetic proxy telemetry replay. "
        "No food-safety claims."
    )

    # Load source (read-only M2 outputs)
    df_out_src = pd.read_csv(OUT_LABELED_CSV, parse_dates=["ts"])
    df_in_src  = pd.read_csv(IN_LABELED_CSV,  parse_dates=["ts"])

    # Load replay logs (M5a outputs)
    df_out_rep = pd.read_csv(REPLAY_LOG_OUT_CSV, parse_dates=["ts"])
    df_in_rep  = pd.read_csv(REPLAY_LOG_IN_CSV,  parse_dates=["ts"])

    logger.info(
        "Source loaded: Out=%d rows | In=%d rows",
        len(df_out_src), len(df_in_src),
    )
    logger.info(
        "Replay loaded: Out=%d rows | In=%d rows",
        len(df_out_rep), len(df_in_rep),
    )

    results_out = verify_series(df_out_src, df_out_rep, "Out")
    results_in  = verify_series(df_in_src,  df_in_rep,  "In")

    # ── Final summary ──────────────────────────────────────────────────────────
    logger.info("")
    logger.info("=" * 65)
    logger.info("VERIFICATION SUMMARY")
    logger.info("=" * 65)
    for r in [results_out, results_in]:
        logger.info(
            "Series %-3s | rows=%d/%d match=%s | "
            "temp_mis=%s | bool_mis=%s | type_mis=%s | "
            "max_t_disc=%.2e s | ALL_PASS=%s",
            r["series"],
            r["row_count_replay"], r["row_count_source"], r["row_count_match"],
            r["temp_injected_mismatches"],
            r["is_injected_anomaly_mismatches"],
            r["injection_type_mismatches"],
            r["max_abs_time_delta_discrepancy_s"] if r["max_abs_time_delta_discrepancy_s"] is not None else float("nan"),
            r["all_checks_passed"],
        )

    overall = results_out["all_checks_passed"] and results_in["all_checks_passed"]
    logger.info("")
    logger.info(
        "OVERALL VERDICT: %s",
        "ALL CHECKS PASSED FOR BOTH SERIES ✓" if overall else "VERIFICATION FAILED — SEE DETAILS ABOVE ✗",
    )
    logger.info("=== Twin Verification complete ===")

    return results_out, results_in


if __name__ == "__main__":
    main()
