"""
scripts/evaluate_pilstm.py
==========================
Evaluates the Physics-Informed LSTM-Autoencoder (PILSTM-AE, Proposal P2)
across the chronological test split (D6, D26).

Computes:
- Test-split classification performance (Precision, Recall, FPR, F1).
- Physical spike classification (SENSOR_ARTIFACT vs. TEMPERATURE_EXCURSION).
- Test injection lead-time replication comparison against baseline LSTM.
Saves:
- data/processed/pilstm_test_metrics.json
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

from src.twin_monitors import PILSTMMonitor


def evaluate_series(series: str):
    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"

    with open(processed_dir / "pilstm_eval_stats.json", "r") as f:
        stats = json.load(f)
    thresh = float(stats[series]["pilstm_threshold"])

    mon = PILSTMMonitor(
        series_name=series,
        model_path=models_dir / f"pilstm_{series.lower()}.pt",
        norm_stats_path=processed_dir / f"lstm_norm_stats_{series.lower()}.json",
        physics_params_path=processed_dir / f"physics_params_{series.lower()}.json",
        threshold=thresh,
        device="cpu",
    )

    labeled_csv = processed_dir / f"{series.lower()}_labeled.csv"
    df = pd.read_csv(labeled_csv, parse_dates=["ts"])
    df = df.dropna(subset=["gap_seconds"]).sort_values(["ts", "gap_seconds"], ascending=[True, False]).reset_index(drop=True)

    cutoff = pd.Timestamp("2018-10-29 11:10:48")
    test_mask = df["ts"] >= cutoff

    print(f"Streaming full series {series} ({len(df)} rows) through PILSTMMonitor...")
    ts_list = df["ts"].tolist()
    temp_list = df["temp_injected"].astype(float).tolist()
    gap_list = df["gap_seconds"].astype(float).tolist()

    for ts, temp, gap in zip(ts_list, temp_list, gap_list):
        ev = {
            "ts": ts,
            "temp_injected": temp,
            "gap_seconds": gap,
        }
        mon.process_event(ev)

    df_mon = pd.DataFrame(mon.alarm_records)
    df["pilstm_alarm"] = df_mon["alarm"].values
    df["pilstm_score"] = df_mon["score"].values
    df["pilstm_category"] = df_mon["alarm_category"].values

    test_df = df[test_mask].dropna(subset=["pilstm_score"]).copy()
    y_true = test_df["is_injected_anomaly"].values.astype(int)
    y_pred = test_df["pilstm_alarm"].values.astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    rec = recall_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    category_counts = test_df[test_df["pilstm_alarm"] == True]["pilstm_category"].value_counts().to_dict()

    return {
        "TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn),
        "FPR": float(fpr), "Precision": float(prec), "Recall": float(rec), "F1": float(f1),
        "threshold": thresh,
        "category_breakdown": category_counts,
    }


def main():
    all_metrics = {}
    for series in ["Out", "In"]:
        print(f"\n================ EVALUATING PILSTM ({series}) ================")
        m = evaluate_series(series)
        all_metrics[series] = m
        print(f"Results for PILSTM {series}:")
        print(f"  Recall:    {m['Recall']*100:.2f}%")
        print(f"  Precision: {m['Precision']*100:.2f}%")
        print(f"  FPR:       {m['FPR']*100:.2f}%")
        print(f"  F1:        {m['F1']:.4f}")
        print(f"  Alarm Categories: {m['category_breakdown']}")

    out_json = REPO_ROOT / "data" / "processed" / "pilstm_test_metrics.json"
    with open(out_json, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nSaved metrics to {out_json}")


if __name__ == "__main__":
    main()
