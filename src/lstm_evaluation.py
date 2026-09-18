"""
src/lstm_evaluation.py
======================
Evaluates the LSTM-Autoencoder trained in Milestone 4a on real Colab T4 weights.

STRUCTURAL PROXY NOTICE
-----------------------
All data derives from IOT-temp.csv — a generic IoT temperature sensor log,
NOT operational refrigerated-transport telemetry. All injections are synthetic.
No metric or threshold makes any food-safety claim.
See docs/AD_LOG.md (D13, D14, D15, D16).

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D13: Anomaly threshold = train-only causal-score mean + K_SIGMA * std (K_SIGMA=2.0).
     Computed exclusively from valid train_train+val causal scores. Never from test.

D14: Window-level aggregation used only for threshold calibration (offline, non-causal).
     Alarm_timestamp is always derived from causal per-row scoring only.

D16: CAUSAL single-window-per-row scoring.
     Row i -> window [i-29, i] (30 rows). All 30 rows must come from the SAME
     split-region (train_train, val, or test). No cross-region context.
     Normalization: SAVED train-only lstm_norm_stats_{out,in}.json (never recomputed).
     Score = MSE at the window's LAST timestep only.
     Rows without 29 full preceding same-region rows -> score = NaN (blind spot).

USAGE
-----
    python src/lstm_evaluation.py

Inputs (read-only):
    data/processed/out_labeled.csv
    data/processed/in_labeled.csv
    data/processed/lstm_norm_stats_{out,in}.json
    models/lstm_{out,in}.h5
    data/processed/injection_log.csv
    data/processed/injection_train_test_status.csv
    data/processed/injection_evaluation_baseline.csv

Outputs:
    data/processed/lstm_evaluation.csv
    data/processed/lstm_pr_curve_out.csv
    data/processed/lstm_pr_curve_in.csv
"""

from __future__ import annotations

import json
import logging
import pathlib
import sys

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
)

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from config import (
    K_SIGMA,
    LSTM_VAL_FRACTION,
    LSTM_WINDOW_LENGTH,
    SEARCH_HORIZON_MINUTES,
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
MODELS_DIR    = REPO_ROOT / "models"

OUT_LABELED_CSV  = PROCESSED_DIR / "out_labeled.csv"
IN_LABELED_CSV   = PROCESSED_DIR / "in_labeled.csv"
INJECTION_LOG_CSV         = PROCESSED_DIR / "injection_log.csv"
STATUS_CSV                = PROCESSED_DIR / "injection_train_test_status.csv"
BASELINE_EVAL_CSV         = PROCESSED_DIR / "injection_evaluation_baseline.csv"

LSTM_EVAL_CSV       = PROCESSED_DIR / "lstm_evaluation.csv"
PR_CURVE_OUT_CSV    = PROCESSED_DIR / "lstm_pr_curve_out.csv"
PR_CURVE_IN_CSV     = PROCESSED_DIR / "lstm_pr_curve_in.csv"


# ══ D16 Causal Scoring ═════════════════════════════════════════════════════════

def causal_score_rows(
    df: pd.DataFrame,
    model: tf.keras.Model,
    t_mean: float,
    t_std: float,
    g_mean: float,
    g_std: float,
    window_length: int = LSTM_WINDOW_LENGTH,
    region_label: str = "unknown",
) -> np.ndarray:
    """
    D16: Causal single-window-per-row scoring for a SINGLE split-region DataFrame.

    For row at local index i (0-indexed within this region's df):
      - Requires exactly `window_length - 1` preceding rows from the SAME region.
      - Rows 0..window_length-2 get score = NaN (blind spot — not enough context).
      - For row i >= window_length-1:
        * Build window = rows [i-window_length+1, i] (inclusive).
        * Normalize both features with SAVED train-only stats.
        * Run LSTM autoencoder forward pass.
        * score_i = MSE between predicted and actual at the LAST timestep (index -1) only.

    Parameters
    ----------
    df         : DataFrame for one split-region. Must have 'temp_injected', 'gap_seconds'.
    model      : Loaded Keras LSTM-Autoencoder.
    t_mean/std : Train-only normalization stats for temp_injected.
    g_mean/std : Train-only normalization stats for log1p(gap_seconds).
    window_length : Window size (LSTM_WINDOW_LENGTH = 30).
    region_label  : Label for logging only.

    Returns
    -------
    scores : np.ndarray of shape (len(df),), with NaN for blind-spot rows.
    """
    n = len(df)
    scores = np.full(n, np.nan, dtype=np.float64)

    # Precompute normalized features for the full region
    log_gap = np.log1p(df["gap_seconds"].values)
    temp_z  = (df["temp_injected"].values - t_mean) / t_std
    gap_z   = (log_gap - g_mean) / g_std
    features = np.column_stack([temp_z, gap_z])  # (n, 2)

    blind_count = 0
    # Collect all valid windows in one batch for efficiency
    valid_indices = []
    windows_batch = []

    for i in range(n):
        if i < window_length - 1:
            # D16: not enough preceding same-region rows -> NaN (blind spot)
            blind_count += 1
            continue
        start = i - window_length + 1
        window = features[start: i + 1]  # shape (window_length, 2)
        valid_indices.append(i)
        windows_batch.append(window)

    if windows_batch:
        X_batch = np.array(windows_batch, dtype=np.float32)  # (M, 30, 2)
        X_pred  = model.predict(X_batch, verbose=0)           # (M, 30, 2)

        # score_i = MSE at the LAST timestep only (D16)
        diff_last    = X_pred[:, -1, :] - X_batch[:, -1, :]  # (M, 2)
        mse_last     = np.mean(diff_last ** 2, axis=1)        # (M,)

        for idx, score in zip(valid_indices, mse_last):
            scores[idx] = float(score)

    valid_count = int(np.sum(~np.isnan(scores)))
    logger.info(
        "D16 causal scoring [%s]: %d total rows | %d valid scores | %d NaN (blind spot)",
        region_label, n, valid_count, blind_count,
    )
    return scores


def score_series(
    df_region: pd.DataFrame,
    model: tf.keras.Model,
    norm_stats: dict,
    region_label: str,
) -> np.ndarray:
    """Score one region of one series (train_train, val, or test)."""
    return causal_score_rows(
        df_region,
        model,
        t_mean=norm_stats["temp_injected_mean"],
        t_std=norm_stats["temp_injected_std"],
        g_mean=norm_stats["log_gap_seconds_mean"],
        g_std=norm_stats["log_gap_seconds_std"],
        region_label=region_label,
    )


# ══ D13 Threshold ══════════════════════════════════════════════════════════════

def compute_threshold(
    scores_train: np.ndarray,
    series_name: str,
) -> tuple[float, float, float]:
    """
    D13: threshold = mean(valid train scores) + K_SIGMA * std(valid train scores).
    NaN scores are excluded (blind-spot rows at region boundaries).
    Returns (threshold, mean, std).
    """
    valid = scores_train[~np.isnan(scores_train)]
    if len(valid) == 0:
        raise ValueError(f"Series '{series_name}': No valid train scores — cannot compute threshold!")
    mu    = float(np.mean(valid))
    sigma = float(np.std(valid))
    thr   = mu + K_SIGMA * sigma
    logger.info(
        "D13 threshold [%s]: %d valid train+val scores | mean=%.6f | std=%.6f | "
        "threshold (mean+%.1f*std)=%.6f",
        series_name, len(valid), mu, sigma, K_SIGMA, thr,
    )
    return thr, mu, sigma


# ══ Point-wise metrics ═════════════════════════════════════════════════════════

def compute_pointwise_metrics(
    df_test_valid: pd.DataFrame,
    series_name: str,
    n_excluded: int,
) -> dict:
    """
    Confusion counts + precision/recall/F1/FPR on test rows WITH valid scores only.
    NaN-score rows are explicitly excluded from both denominator and numerator.

    Parameters
    ----------
    df_test_valid : test rows where lstm_anomaly is True/False (not NaN).
    n_excluded    : count of test rows excluded due to NaN score.
    """
    y_true  = df_test_valid["is_injected_anomaly"].astype(int).values
    y_pred  = df_test_valid["lstm_anomaly"].astype(int).values
    y_score = df_test_valid["lstm_score"].values  # higher -> more anomalous for PR curve

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()

    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec  = float(recall_score(y_true, y_pred, zero_division=0))
    f1   = float(f1_score(y_true, y_pred, zero_division=0))
    fpr  = float(fp / (fp + tn)) if (fp + tn) > 0 else float("nan")
    ap   = float(average_precision_score(y_true, y_score))

    logger.info(
        "Series '%s' TEST point-wise metrics (valid-score rows only, %d excluded):\n"
        "  TP=%-6d FP=%-6d TN=%-6d FN=%-6d\n"
        "  Precision=%.4f  Recall=%.4f  F1=%.4f  FPR=%.4f  AUC-PR=%.4f",
        series_name, n_excluded, tp, fp, tn, fn, prec, rec, f1, fpr, ap,
    )
    return {
        "series": series_name,
        "n_test_rows_total": len(df_test_valid) + n_excluded,
        "n_test_rows_valid_score": len(df_test_valid),
        "n_test_rows_excluded_nan": n_excluded,
        "n_true_anomaly_rows": int(y_true.sum()),
        "TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn),
        "precision": prec, "recall": rec, "f1": f1, "fpr": fpr,
        "auc_pr": ap,
    }


def compute_pr_curve(df_test_valid: pd.DataFrame, series_name: str) -> pd.DataFrame:
    """Precision-recall curve on valid-score test rows."""
    y_true  = df_test_valid["is_injected_anomaly"].astype(int).values
    y_score = df_test_valid["lstm_score"].values  # higher -> more anomalous
    precision, recall, thresholds = precision_recall_curve(y_true, y_score)
    thresholds_padded = np.append(thresholds, np.nan)
    return pd.DataFrame({
        "series":    series_name,
        "threshold": thresholds_padded,
        "precision": precision,
        "recall":    recall,
    })


# ══ Per-injection blind-spot check and alarm search ════════════════════════════

def check_blind_spot(
    df_test_scored: pd.DataFrame,
    onset_ts: pd.Timestamp,
    end_ts: pd.Timestamp,
    inj_id: str,
) -> dict:
    """
    D16: For a given injection window [onset_ts, end_ts + SEARCH_HORIZON_MINUTES],
    check whether the onset_ts row itself falls in the NaN (blind-spot) zone,
    and whether ANY row in the window has NaN score.

    Returns a dict with:
      onset_nan       : bool — onset_ts row has NaN score
      n_window_rows   : int — total rows in the window
      n_nan_in_window : int — rows with NaN score in the window
    """
    horizon_end = end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)
    window_df   = df_test_scored[
        (df_test_scored["ts"] >= onset_ts) & (df_test_scored["ts"] <= horizon_end)
    ]

    # Find onset row
    onset_rows = window_df[window_df["ts"] == onset_ts]
    if onset_rows.empty:
        # Try nearest row at or after onset
        candidates = window_df[window_df["ts"] >= onset_ts]
        onset_nan = bool(candidates.iloc[0]["lstm_score_nan"]) if not candidates.empty else True
    else:
        onset_nan = bool(onset_rows.iloc[0]["lstm_score_nan"])

    n_window_rows   = len(window_df)
    n_nan_in_window = int(window_df["lstm_score_nan"].sum())

    logger.info(
        "Blind-spot check [%s]: window rows=%d | NaN rows in window=%d | onset NaN=%s",
        inj_id, n_window_rows, n_nan_in_window, onset_nan,
    )
    return {
        "onset_nan":       onset_nan,
        "n_window_rows":   n_window_rows,
        "n_nan_in_window": n_nan_in_window,
    }


def find_lstm_alarm(
    df_test_scored: pd.DataFrame,
    onset_ts: pd.Timestamp,
    end_ts: pd.Timestamp,
    inj_id: str,
) -> tuple[pd.Timestamp | None, str]:
    """
    Find first lstm_anomaly=True AND valid score row within
    [onset_ts, end_ts + SEARCH_HORIZON_MINUTES].

    Returns (alarm_ts, reason):
      reason: 'ok' | 'blind_spot' | 'never_flagged'
    """
    horizon_end = end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)
    window_df   = df_test_scored[
        (df_test_scored["ts"] >= onset_ts) & (df_test_scored["ts"] <= horizon_end)
    ]

    if window_df.empty:
        return None, "never_flagged"

    # Must have valid score AND be flagged
    valid_flagged = window_df[
        (~window_df["lstm_score_nan"]) & (window_df["lstm_anomaly"] == True)
    ]

    if valid_flagged.empty:
        # Distinguish: were ALL rows NaN, or just none flagged?
        all_nan = window_df["lstm_score_nan"].all()
        reason  = "blind_spot" if all_nan else "never_flagged"
        return None, reason

    alarm_ts = valid_flagged.iloc[0]["ts"]
    return alarm_ts, "ok"


# ══ Evaluation table ═══════════════════════════════════════════════════════════

def build_evaluation_table(
    inj_log: pd.DataFrame,
    status_df: pd.DataFrame,
    baseline_eval: pd.DataFrame,
    scored_test_dfs: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """
    Build lstm_evaluation.csv (all 30 injections), mirroring if_evaluation.csv structure.

    Extra column: lstm_evaluation_reason
      'ok'                        : test injection, valid alarm found
      'blind_spot'                : all window rows NaN (no valid score in window)
      'never_flagged'             : valid scores exist but none crossed threshold
      'train_or_straddling_excluded' : non-test injection (train/straddling), lead time N/A
    """
    merged = inj_log.merge(
        status_df[["injection_id", "train_test_status", "start_ts", "end_ts"]],
        on="injection_id",
    )
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
        inj_id   = inj["injection_id"]
        series   = inj["series"]
        status   = inj["train_test_status"]
        start_ts = pd.Timestamp(inj["start_ts"])
        end_ts   = pd.Timestamp(inj["end_ts"])
        irrev_ts = inj["irreversibility_timestamp"]
        if pd.notna(irrev_ts):
            irrev_ts = pd.Timestamp(irrev_ts)

        if status == "test":
            alarm_ts, reason = find_lstm_alarm(
                scored_test_dfs[series], start_ts, end_ts, inj_id
            )
            if alarm_ts is not None and pd.notna(irrev_ts):
                lead_lstm = (irrev_ts - alarm_ts).total_seconds() / 60.0
            else:
                lead_lstm = float("nan")
        else:
            alarm_ts  = pd.NaT
            lead_lstm = float("nan")
            reason    = "train_or_straddling_excluded"

        rows.append({
            "injection_id":              inj_id,
            "series":                    series,
            "type":                      inj["type"],
            "alarm_timestamp_LSTM":      alarm_ts,
            "lead_time_LSTM_min":        round(lead_lstm, 2) if not np.isnan(lead_lstm) else float("nan"),
            "alarm_timestamp_baseline":  inj["baseline_alarm_timestamp"],
            "lead_time_baseline_min":    inj["baseline_lead_time_min"],
            "irreversibility_timestamp": irrev_ts,
            "train_test_status":         status,
            "lstm_evaluation_reason":    reason,
        })

    return pd.DataFrame(rows)


# ══ Main ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    logger.info("=== Cold Chain EWS — LSTM Evaluation (Milestone 4b) ===")
    logger.info(
        "PROXY NOTICE: All results are on SYNTHETIC PROXY CONSTRUCTS. "
        "No food-safety claims. No retraining executed — inference-only (CPU)."
    )
    logger.info(
        "D16: Causal single-window-per-row scoring. "
        "D13: Threshold = train-only mean + %.1f * std.", K_SIGMA
    )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load labeled CSVs ─────────────────────────────────────────────────────
    logger.info("Loading labeled CSVs...")
    df_out_raw = pd.read_csv(OUT_LABELED_CSV, parse_dates=["ts"])
    df_in_raw  = pd.read_csv(IN_LABELED_CSV,  parse_dates=["ts"])
    logger.info("  Out: %d rows | In: %d rows", len(df_out_raw), len(df_in_raw))

    # ── Load norm stats ────────────────────────────────────────────────────────
    with open(PROCESSED_DIR / "lstm_norm_stats_out.json", encoding="utf-8") as f:
        norm_out = json.load(f)
    with open(PROCESSED_DIR / "lstm_norm_stats_in.json", encoding="utf-8") as f:
        norm_in  = json.load(f)
    logger.info("Loaded train-only normalization stats (Out and In).")

    # ── Load trained LSTM models ───────────────────────────────────────────────
    logger.info("Loading trained LSTM models (inference-only, CPU, no retraining)...")
    model_out = tf.keras.models.load_model(str(MODELS_DIR / "lstm_out.h5"), compile=False)
    model_in  = tf.keras.models.load_model(str(MODELS_DIR / "lstm_in.h5"),  compile=False)
    logger.info("Models loaded: lstm_out.h5, lstm_in.h5")

    # ── Load auxiliary CSVs ────────────────────────────────────────────────────
    inj_log       = pd.read_csv(INJECTION_LOG_CSV, parse_dates=["start_timestamp"])
    status_df     = pd.read_csv(STATUS_CSV,         parse_dates=["start_ts", "end_ts"])
    baseline_eval = pd.read_csv(
        BASELINE_EVAL_CSV,
        parse_dates=["baseline_alarm_timestamp", "irreversibility_timestamp", "start_timestamp"],
    )

    # ── Reproduce exact M4a split ──────────────────────────────────────────────
    # Replicate lstm_prep.py's split logic exactly — same cutoff_ts, same val fraction.
    cutoff_ts = compute_cutoff_ts(df_out_raw, df_in_raw)
    logger.info("M4b split: cutoff_ts=%s  LSTM_VAL_FRACTION=%.2f", cutoff_ts, LSTM_VAL_FRACTION)

    scored_test_dfs: dict[str, pd.DataFrame] = {}
    metrics_list:    list[dict] = []

    for series_name, df_raw, norm_stats, model in [
        ("Out", df_out_raw, norm_out, model_out),
        ("In",  df_in_raw,  norm_in,  model_in),
    ]:
        logger.info("=" * 65)
        logger.info("Processing Series: '%s'", series_name)
        logger.info("=" * 65)

        # Drop initial NaN row (gap_seconds) — identical to lstm_prep.py (D16)
        df = df_raw.dropna(subset=["gap_seconds"]).reset_index(drop=True).copy()
        logger.info("Dropped initial NaN rows: %d → %d", len(df_raw), len(df))

        # Reproduce train/test split
        df_train, df_test = split_series(df, cutoff_ts, series_name)

        # Reproduce train_train / val split (same formula as lstm_prep.py)
        n_train        = len(df_train)
        n_val          = int(round(n_train * LSTM_VAL_FRACTION))
        df_train_train = df_train.iloc[:-n_val].copy().reset_index(drop=True)
        df_val         = df_train.iloc[-n_val:].copy().reset_index(drop=True)
        df_test_reset  = df_test.reset_index(drop=True)

        logger.info(
            "Row split: train_train=%d | val=%d | test=%d",
            len(df_train_train), len(df_val), len(df_test_reset),
        )

        # ── D16 causal scoring — train_train ──────────────────────────────────
        scores_tt = score_series(df_train_train, model, norm_stats, f"{series_name}/train_train")
        # ── D16 causal scoring — val ──────────────────────────────────────────
        scores_val = score_series(df_val, model, norm_stats, f"{series_name}/val")

        # Combine for D13 threshold calibration (train_train + val)
        scores_calib = np.concatenate([scores_tt, scores_val])
        n_nan_calib  = int(np.sum(np.isnan(scores_calib)))
        n_valid_calib = int(np.sum(~np.isnan(scores_calib)))
        logger.info(
            "Calibration scores (train_train+val): total=%d | valid=%d | NaN=%d",
            len(scores_calib), n_valid_calib, n_nan_calib,
        )

        # ── D13 threshold ────────────────────────────────────────────────────
        threshold, thr_mean, thr_std = compute_threshold(scores_calib, series_name)

        # ── D16 causal scoring — test ─────────────────────────────────────────
        scores_test = score_series(df_test_reset, model, norm_stats, f"{series_name}/test")
        n_nan_test   = int(np.sum(np.isnan(scores_test)))
        n_valid_test = int(np.sum(~np.isnan(scores_test)))
        logger.info(
            "Test scores: total=%d | valid=%d | NaN (blind spot)=%d",
            len(scores_test), n_valid_test, n_nan_test,
        )

        # ── Attach scores and flags to test df ────────────────────────────────
        df_test_scored = df_test_reset.copy()
        df_test_scored["lstm_score"]    = scores_test
        df_test_scored["lstm_score_nan"]= np.isnan(scores_test)
        # NaN-score rows get NaN anomaly flag (NOT False — excluded from metrics)
        df_test_scored["lstm_anomaly"]  = np.where(
            df_test_scored["lstm_score_nan"],
            np.nan,
            (scores_test >= threshold).astype(float),
        )
        # Convert float NaN / 0.0 / 1.0 -> nullable boolean for clarity in outputs
        df_test_scored["lstm_anomaly"] = df_test_scored["lstm_anomaly"].apply(
            lambda x: None if pd.isna(x) else bool(x)
        )

        # ── Point-wise metrics on valid-score test rows ────────────────────────
        df_test_valid = df_test_scored[~df_test_scored["lstm_score_nan"]].copy()
        df_test_valid["lstm_anomaly"] = df_test_valid["lstm_anomaly"].astype(bool)
        metrics = compute_pointwise_metrics(df_test_valid, series_name, n_nan_test)
        metrics_list.append(metrics)

        # ── PR curve (valid-score test rows only) ─────────────────────────────
        pr_df = compute_pr_curve(df_test_valid, series_name)
        pr_path = PR_CURVE_OUT_CSV if series_name == "Out" else PR_CURVE_IN_CSV
        pr_df.to_csv(pr_path, index=False)
        logger.info("Saved PR curve: %s (%d points)", pr_path.name, len(pr_df))

        # ── Blind-spot check for test-side injections ─────────────────────────
        test_injections = status_df[
            (status_df["series"] == series_name) &
            (status_df["train_test_status"] == "test")
        ]
        logger.info("=== Blind-spot checks for test-side injections (%s) ===", series_name)
        for _, inj in test_injections.iterrows():
            inj_id   = inj["injection_id"]
            start_ts = pd.Timestamp(inj["start_ts"])
            end_ts   = pd.Timestamp(inj["end_ts"])
            bs_info  = check_blind_spot(df_test_scored, start_ts, end_ts, inj_id)
            logger.info(
                "  %-25s | onset_NaN=%-5s | window_rows=%d | NaN_in_window=%d",
                inj_id,
                str(bs_info["onset_nan"]),
                bs_info["n_window_rows"],
                bs_info["n_nan_in_window"],
            )

        scored_test_dfs[series_name] = df_test_scored

    # ── Point-wise metrics summary ─────────────────────────────────────────────
    logger.info("=== POINT-WISE METRICS SUMMARY (test valid-score rows) ===")
    for m in metrics_list:
        logger.info(
            "  %-3s: TP=%-5d FP=%-6d TN=%-6d FN=%-5d "
            "prec=%.3f  rec=%.3f  F1=%.3f  FPR=%.3f  AUC-PR=%.3f  "
            "[excluded NaN=%d]",
            m["series"], m["TP"], m["FP"], m["TN"], m["FN"],
            m["precision"], m["recall"], m["f1"], m["fpr"], m["auc_pr"],
            m["n_test_rows_excluded_nan"],
        )

    # ── Build and save lstm_evaluation.csv ────────────────────────────────────
    eval_df = build_evaluation_table(
        inj_log, status_df, baseline_eval, scored_test_dfs
    )
    eval_df.to_csv(LSTM_EVAL_CSV, index=False)
    logger.info("Saved: %s (%d rows)", LSTM_EVAL_CSV.name, len(eval_df))

    # ── Lead time log (test-side only) ────────────────────────────────────────
    test_eval = eval_df[eval_df["train_test_status"] == "test"]
    logger.info("=== LEAD TIME COMPARISON (test-side injections) ===")
    for _, r in test_eval.iterrows():
        lead_lstm = r["lead_time_LSTM_min"]
        lead_base = r["lead_time_baseline_min"]
        lead_lstm_s = f"{lead_lstm:.1f} min" if not pd.isna(lead_lstm) else f"null ({r['lstm_evaluation_reason']})"
        lead_base_s = f"{lead_base:.1f} min" if not pd.isna(lead_base) else "null"
        logger.info(
            "  %-25s [%s/%s]  LSTM=%s  baseline=%s",
            r["injection_id"], r["series"], r["type"], lead_lstm_s, lead_base_s,
        )

    logger.info("=== LSTM Evaluation complete (Milestone 4b) ===")
    logger.info("CONFIRMED: No retraining. No NaN score fill-in. No SimPy code. CPU inference only.")


if __name__ == "__main__":
    main()
