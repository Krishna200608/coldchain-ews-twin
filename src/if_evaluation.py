"""
src/if_evaluation.py
====================
Evaluates the Isolation Forest model trained in isolation_forest_model.py.

STRUCTURAL PROXY NOTICE
-----------------------
All metrics (precision, recall, AUC-PR, lead times) are computed on
SYNTHETIC PROXY CONSTRUCTS — not real cold-chain disruption events.
See D5-D8 in docs/AD_LOG.md.

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D7: Point-wise metrics use discrete predictions (contamination='auto').
    Separately computes the full precision-recall curve over continuous
    decision_function scores to expose threshold sensitivity.

D8: irreversibility_timestamp is REUSED from M2's
    injection_evaluation_baseline.csv — NOT recomputed.
    Only alarm_timestamp_IF is new (first IF-flagged row within the
    bounded search window [onset_ts, injection_end_ts + SEARCH_HORIZON_MINUTES]).
    lead_time_IF = irreversibility_timestamp - alarm_timestamp_IF.

D6: Lead times are computed ONLY for TEST-SIDE injections (status='test').
    Train-side and straddling injections are included in if_evaluation.csv
    with NaN lead times but with their status clearly reported.

USAGE
-----
    python src/if_evaluation.py

Inputs:
    data/processed/if_scores_out.csv        (isolation_forest_model.py output)
    data/processed/if_scores_in.csv
    data/processed/injection_log.csv        (M2 output, read-only)
    data/processed/injection_train_test_status.csv
    data/processed/injection_evaluation_baseline.csv  (M2 output, read-only)

Outputs:
    data/processed/if_evaluation.csv
    data/processed/if_pr_curve_out.csv
    data/processed/if_pr_curve_in.csv
"""

from __future__ import annotations

import logging
import pathlib
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from config import SEARCH_HORIZON_MINUTES

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

OUT_SCORES_CSV   = PROCESSED_DIR / "if_scores_out.csv"
IN_SCORES_CSV    = PROCESSED_DIR / "if_scores_in.csv"
INJECTION_LOG_CSV         = PROCESSED_DIR / "injection_log.csv"
STATUS_CSV                = PROCESSED_DIR / "injection_train_test_status.csv"
BASELINE_EVAL_CSV         = PROCESSED_DIR / "injection_evaluation_baseline.csv"

IF_EVAL_CSV      = PROCESSED_DIR / "if_evaluation.csv"
PR_CURVE_OUT_CSV = PROCESSED_DIR / "if_pr_curve_out.csv"
PR_CURVE_IN_CSV  = PROCESSED_DIR / "if_pr_curve_in.csv"


# ══ Point-wise metrics ════════════════════════════════════════════════════════

def compute_pointwise_metrics(df_test: pd.DataFrame, series_name: str) -> dict:
    """
    Compute precision/recall/F1/FPR and raw confusion counts on TEST rows.

    Ground truth : is_injected_anomaly (bool)
    Prediction   : if_anomaly (bool, discrete from contamination='auto')

    Returns dict of TP, FP, TN, FN + derived rates + AUC-PR.
    """
    y_true = df_test["is_injected_anomaly"].astype(int).values
    y_pred = df_test["if_anomaly"].astype(int).values
    # if_score from decision_function: lower = more anomalous → negate for sklearn convention
    y_score = -df_test["if_score"].values

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec  = float(recall_score(y_true, y_pred, zero_division=0))
    f1   = float(f1_score(y_true, y_pred, zero_division=0))
    fpr  = float(fp / (fp + tn)) if (fp + tn) > 0 else float("nan")
    ap   = float(average_precision_score(y_true, y_score))

    logger.info(
        "Series '%s' TEST point-wise metrics:\n"
        "  TP=%d  FP=%d  TN=%d  FN=%d\n"
        "  Precision=%.4f  Recall=%.4f  F1=%.4f  FPR=%.4f\n"
        "  AUC-PR (avg precision)=%.4f",
        series_name, tp, fp, tn, fn, prec, rec, f1, fpr, ap,
    )
    return {
        "series": series_name,
        "n_test_rows": len(df_test),
        "n_true_anomaly_rows": int(y_true.sum()),
        "TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn),
        "precision": prec, "recall": rec, "f1": f1, "fpr": fpr,
        "auc_pr": ap,
    }


def compute_pr_curve(df_test: pd.DataFrame, series_name: str) -> pd.DataFrame:
    """
    Compute full precision-recall curve over continuous if_score on TEST rows.
    if_score from decision_function is negated so that high score = anomalous.
    """
    y_true  = df_test["is_injected_anomaly"].astype(int).values
    y_score = -df_test["if_score"].values   # negate: higher → more anomalous
    precision, recall, thresholds = precision_recall_curve(y_true, y_score)
    # thresholds has len = len(precision) - 1; pad with NaN for alignment
    thresholds_padded = np.append(thresholds, np.nan)
    return pd.DataFrame({
        "series":    series_name,
        "threshold": thresholds_padded,
        "precision": precision,
        "recall":    recall,
    })


# ══ Per-injection IF alarm timestamp and lead time ════════════════════════════

def find_if_alarm_timestamp(
    df_scored: pd.DataFrame,
    start_ts: pd.Timestamp,
    end_ts: pd.Timestamp,
) -> pd.Timestamp | None:
    """
    Find the FIRST IF-flagged row (if_anomaly=True) within the bounded window
    [start_ts, end_ts + SEARCH_HORIZON_MINUTES], per D8.
    """
    horizon_end = end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)
    window = df_scored[
        (df_scored["ts"] >= start_ts) & (df_scored["ts"] <= horizon_end)
    ]
    flagged = window[window["if_anomaly"]]
    if flagged.empty:
        return None
    return flagged.iloc[0]["ts"]


def build_evaluation_table(
    inj_log: pd.DataFrame,
    status_df: pd.DataFrame,
    baseline_eval: pd.DataFrame,
    scored_dfs: dict[str, pd.DataFrame],
    labeled_dfs: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Build the full if_evaluation.csv (all 30 injections, per D6/D8).

    Columns:
      injection_id, series, type, train_test_status,
      alarm_timestamp_IF, lead_time_IF_min,
      alarm_timestamp_baseline, lead_time_baseline_min,
      irreversibility_timestamp
    """
    # Merge injection log with status
    merged = inj_log.merge(
        status_df[["injection_id", "train_test_status", "start_ts", "end_ts"]],
        on="injection_id",
    )
    # Merge with baseline evaluation for irrev_ts and baseline alarm
    merged = merged.merge(
        baseline_eval[[
            "injection_id",
            "baseline_alarm_timestamp",
            "baseline_lead_time_min",
            "irreversibility_timestamp",
        ]],
        on="injection_id",
        how="left",
    )

    rows = []
    for _, inj in merged.iterrows():
        series   = inj["series"]
        status   = inj["train_test_status"]
        start_ts = inj["start_ts"]
        end_ts   = inj["end_ts"]
        irrev_ts = inj["irreversibility_timestamp"]   # reused from M2 (D8)

        # Only compute IF alarm for test-side injections (D6)
        if status == "test":
            alarm_if_ts = find_if_alarm_timestamp(scored_dfs[series], start_ts, end_ts)
            if alarm_if_ts is not None and pd.notna(irrev_ts):
                lead_if = (
                    pd.Timestamp(irrev_ts) - alarm_if_ts
                ).total_seconds() / 60.0
            else:
                lead_if = float("nan")
        else:
            alarm_if_ts = pd.NaT
            lead_if     = float("nan")

        rows.append({
            "injection_id":              inj["injection_id"],
            "series":                    series,
            "type":                      inj["type"],
            "alarm_timestamp_IF":        alarm_if_ts,
            "lead_time_IF_min":          round(lead_if, 2) if not np.isnan(lead_if) else float("nan"),
            "alarm_timestamp_baseline":  inj["baseline_alarm_timestamp"],
            "lead_time_baseline_min":    inj["baseline_lead_time_min"],
            "irreversibility_timestamp": irrev_ts,
            "train_test_status":         status,
        })

    return pd.DataFrame(rows)


# ══ Main ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    logger.info("=== Cold Chain EWS — IF Evaluation (Milestone 3) ===")
    logger.info(
        "PROXY NOTICE: All results are on SYNTHETIC PROXY CONSTRUCTS. "
        "No food-safety claims."
    )
    logger.info(
        "D8: irreversibility_timestamp REUSED from M2 baseline eval — not recomputed."
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load inputs ────────────────────────────────────────────────────────────
    df_out = pd.read_csv(OUT_SCORES_CSV, parse_dates=["ts"])
    df_in  = pd.read_csv(IN_SCORES_CSV,  parse_dates=["ts"])
    inj_log       = pd.read_csv(INJECTION_LOG_CSV,  parse_dates=["start_timestamp"])
    status_df     = pd.read_csv(STATUS_CSV,          parse_dates=["start_ts", "end_ts"])
    baseline_eval = pd.read_csv(BASELINE_EVAL_CSV,
                                parse_dates=["baseline_alarm_timestamp",
                                             "irreversibility_timestamp",
                                             "start_timestamp"])

    logger.info(
        "Loaded scored rows: Out=%d  In=%d | injection_log=%d | status=%d | baseline_eval=%d",
        len(df_out), len(df_in), len(inj_log), len(status_df), len(baseline_eval),
    )

    scored_dfs  = {"Out": df_out, "In": df_in}
    labeled_dfs = {"Out": df_out, "In": df_in}  # already contains is_injected_anomaly

    # ── Point-wise metrics on TEST rows only ───────────────────────────────────
    cutoff_ts = status_df["start_ts"].min()   # lowest start_ts of any injection
    # Re-derive cutoff from scored rows — find the split point
    # The scored DFs have the train/test structure; re-derive from status 'test' injections
    # Use the minimum start_ts of test-side injections as proxy, but more robustly:
    # read cutoff_ts indirectly — the model was trained on ts < cutoff_ts,
    # test rows are ts >= cutoff_ts. We can infer from status_df.
    test_ids  = set(status_df[status_df["train_test_status"] == "test"]["injection_id"])
    train_ids = set(status_df[status_df["train_test_status"] == "train"]["injection_id"])
    strad_ids = set(status_df[status_df["train_test_status"] == "straddling"]["injection_id"])
    logger.info(
        "Injection status counts: test=%d  train=%d  straddling=%d",
        len(test_ids), len(train_ids), len(strad_ids),
    )

    # Get test-side end_ts minimum to find approximate cutoff
    test_status = status_df[status_df["train_test_status"] == "test"]
    if not test_status.empty:
        cutoff_approx = test_status["start_ts"].min()
    else:
        cutoff_approx = None

    logger.info("Approximate cutoff_ts (min start_ts of test injections): %s", cutoff_approx)

    # For point-wise metrics we need TEST-SPLIT rows, not just test-injection rows.
    # We derive cutoff from saved scored DFs by reading the cutoff indirectly:
    # use the same formula as isolation_forest_model.py on the actual data.
    all_ts   = pd.concat([df_out["ts"], df_in["ts"]])
    from config import TRAIN_FRACTION
    date_min = all_ts.min()
    date_max = all_ts.max()
    cutoff_ts = date_min + TRAIN_FRACTION * (date_max - date_min)
    logger.info("Re-derived cutoff_ts for evaluation: %s", cutoff_ts)

    df_out_test = df_out[df_out["ts"] >= cutoff_ts]
    df_in_test  = df_in[df_in["ts"]  >= cutoff_ts]
    logger.info(
        "Test-split rows: Out=%d  In=%d",
        len(df_out_test), len(df_in_test),
    )

    metrics_out = compute_pointwise_metrics(df_out_test, "Out")
    metrics_in  = compute_pointwise_metrics(df_in_test,  "In")

    logger.info("=== POINT-WISE METRICS SUMMARY ===")
    for m in [metrics_out, metrics_in]:
        logger.info(
            "  %-3s: TP=%-5d FP=%-5d TN=%-6d FN=%-5d "
            "prec=%.3f  rec=%.3f  F1=%.3f  FPR=%.3f  AUC-PR=%.3f",
            m["series"], m["TP"], m["FP"], m["TN"], m["FN"],
            m["precision"], m["recall"], m["f1"], m["fpr"], m["auc_pr"],
        )

    # ── Precision-recall curves ────────────────────────────────────────────────
    pr_out = compute_pr_curve(df_out_test, "Out")
    pr_in  = compute_pr_curve(df_in_test,  "In")
    pr_out.to_csv(PR_CURVE_OUT_CSV, index=False)
    pr_in.to_csv(PR_CURVE_IN_CSV,   index=False)
    logger.info("Saved: %s (%d points)", PR_CURVE_OUT_CSV.name, len(pr_out))
    logger.info("Saved: %s (%d points)", PR_CURVE_IN_CSV.name,  len(pr_in))

    # ── Per-injection evaluation table ────────────────────────────────────────
    eval_df = build_evaluation_table(
        inj_log, status_df, baseline_eval, scored_dfs, labeled_dfs
    )
    eval_df.to_csv(IF_EVAL_CSV, index=False)
    logger.info("Saved: %s (%d rows)", IF_EVAL_CSV.name, len(eval_df))

    # ── Per-injection lead time comparison ────────────────────────────────────
    test_eval = eval_df[eval_df["train_test_status"] == "test"]
    logger.info("=== LEAD TIME COMPARISON (test-side injections only, D6/D8) ===")
    logger.info(
        "IF alarm null: %d/%d test injections (no IF flag within bounded window)",
        test_eval["alarm_timestamp_IF"].isna().sum(), len(test_eval),
    )
    logger.info(
        "Baseline alarm null (same injections): %d/%d",
        test_eval["alarm_timestamp_baseline"].isna().sum(), len(test_eval),
    )
    for _, r in test_eval.iterrows():
        lead_if   = r["lead_time_IF_min"]
        lead_base = r["lead_time_baseline_min"]
        lead_if_s   = f"{lead_if:.1f} min"   if not pd.isna(lead_if)   else "null"
        lead_base_s = f"{lead_base:.1f} min" if not pd.isna(lead_base) else "null"
        logger.info(
            "  %-20s [%s/%s]  IF=%s  baseline=%s",
            r["injection_id"], r["series"], r["type"], lead_if_s, lead_base_s,
        )

    logger.info("=== IF Evaluation complete ===")


if __name__ == "__main__":
    main()
