"""
scripts/evaluate_adaptive_threshold.py
======================================
Evaluates the online Kalman + CUSUM adaptive threshold (Proposal P4) against
fixed baseline thresholds on the test split (D6, D26).

Computes point-wise FPR, Precision, Recall, and F1 before vs after adaptive thresholding.
Saves:
  data/processed/adaptive_threshold_log_out.csv
  data/processed/adaptive_threshold_log_in.csv
  data/processed/adaptive_threshold_metrics.json
"""

import json
import pathlib
import sys
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.config import (
    LSTM_THRESH_OUT,
    LSTM_THRESH_IN,
)
from src.split_utils import compute_cutoff_ts
from src.twin_monitors import IFMonitor, LSTMMonitor


def evaluate_series(series: str):
    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"
    
    labeled_csv = processed_dir / f"{series.lower()}_labeled.csv"
    df = pd.read_csv(labeled_csv, parse_dates=["ts"])
    df = df.dropna(subset=["gap_seconds"]).sort_values(["ts", "gap_seconds"], ascending=[True, False]).reset_index(drop=True)
    
    # Chronological partition (D6)
    cutoff = pd.Timestamp("2018-10-29 11:10:48")
    train_mask = df["ts"] < cutoff
    test_mask = ~train_mask
    
    # Initialize monitors
    if_model_path = models_dir / f"isolation_forest_{series.lower()}.joblib"
    lstm_model_path = models_dir / f"lstm_{series.lower()}.h5"
    lstm_norm_path = processed_dir / f"lstm_norm_stats_{series.lower()}.json"
    fixed_lstm_thresh = LSTM_THRESH_OUT if series.lower() == "out" else LSTM_THRESH_IN
    
    if_mon = IFMonitor(series, if_model_path)
    lstm_mon = LSTMMonitor(series, lstm_model_path, lstm_norm_path, fixed_lstm_thresh)
    
    print(f"Streaming full series {series} ({len(df)} rows) through IF and LSTM monitors...")
    
    # Continuous stream (D23) across train to calibrate / warm up Kalman adapter
    for idx, row in df.iterrows():
        ev = {
            "ts": row["ts"],
            "temp_injected": float(row["temp_injected"]),
            "gap_seconds": float(row["gap_seconds"]),
        }
        if_mon.process_event(ev)
        lstm_mon.process_event(ev)
    
    df_if = pd.DataFrame(if_mon.alarm_records)
    df_lstm = pd.DataFrame(lstm_mon.alarm_records)
    
    # Align with ground truth
    df["if_alarm_fixed"] = df_if["alarm"].values
    df["if_alarm_adapt"] = df_if["adaptive_alarm"].values
    df["if_cusum_alarm"] = df_if["cusum_alarm"].values
    df["if_adapt_thresh"] = df_if["adaptive_threshold"].values
    df["if_score"] = df_if["score"].values
    
    df["lstm_alarm_fixed"] = df_lstm["alarm"].values
    df["lstm_alarm_adapt"] = df_lstm["adaptive_alarm"].values
    df["lstm_cusum_alarm"] = df_lstm["cusum_alarm"].values
    df["lstm_adapt_thresh"] = df_lstm["adaptive_threshold"].values
    df["lstm_score"] = df_lstm["score"].values
    
    # Save per-reading adaptive log (D26: test partition or full series)
    log_cols = [
        "ts", "temp_injected", "gap_seconds", "is_injected_anomaly",
        "if_score", "if_alarm_fixed", "if_adapt_thresh", "if_alarm_adapt", "if_cusum_alarm",
        "lstm_score", "lstm_alarm_fixed", "lstm_adapt_thresh", "lstm_alarm_adapt", "lstm_cusum_alarm"
    ]
    df[log_cols].to_csv(processed_dir / f"adaptive_threshold_log_{series.lower()}.csv", index=False)
    print(f"Saved data/processed/adaptive_threshold_log_{series.lower()}.csv")
    
    # Compute test-set metrics (D6, D26)
    test_df = df[test_mask].dropna(subset=["lstm_score"]).copy()
    y_true = test_df["is_injected_anomaly"].values.astype(int)
    
    metrics = {}
    for model_name, col_fixed, col_adapt in [
        ("Isolation_Forest", "if_alarm_fixed", "if_alarm_adapt"),
        ("LSTM_Autoencoder", "lstm_alarm_fixed", "lstm_alarm_adapt"),
    ]:
        for mode, col in [("Fixed", col_fixed), ("Adaptive", col_adapt)]:
            y_pred = test_df[col].values.astype(int)
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
            fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
            rec = recall_score(y_true, y_pred, zero_division=0)
            prec = precision_score(y_true, y_pred, zero_division=0)
            f1 = f1_score(y_true, y_pred, zero_division=0)
            
            metrics[f"{model_name}_{mode}"] = {
                "TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn),
                "FPR": float(fpr), "Precision": float(prec), "Recall": float(rec), "F1": float(f1)
            }
            
    return metrics


def main():
    all_metrics = {}
    for series in ["Out", "In"]:
        print(f"\n================ EVALUATING {series} SERIES ================")
        m = evaluate_series(series)
        all_metrics[series] = m
        
        print("\n" + "="*70)
        print(f"RESULTS FOR {series.upper()} SERIES (Test Split)")
        print("="*70)
        print(f"{'Model':<20} | {'Mode':<10} | {'Recall':<8} | {'Precision':<10} | {'FPR':<8} | {'F1':<8}")
        print("-" * 70)
        for model in ["Isolation_Forest", "LSTM_Autoencoder"]:
            f_m = m[f"{model}_Fixed"]
            a_m = m[f"{model}_Adaptive"]
            print(f"{model:<20} | {'Fixed':<10} | {f_m['Recall']*100:6.2f}% | {f_m['Precision']*100:9.2f}% | {f_m['FPR']*100:6.2f}% | {f_m['F1']:6.4f}")
            print(f"{model:<20} | {'Adaptive':<10} | {a_m['Recall']*100:6.2f}% | {a_m['Precision']*100:9.2f}% | {a_m['FPR']*100:6.2f}% | {a_m['F1']:6.4f}")
            print("-" * 70)

    out_json = REPO_ROOT / "data" / "processed" / "adaptive_threshold_metrics.json"
    with open(out_json, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nSaved metrics to {out_json}")


if __name__ == "__main__":
    main()
