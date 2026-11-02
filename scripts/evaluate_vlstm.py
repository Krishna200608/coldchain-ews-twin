"""
scripts/evaluate_vlstm.py
=========================
Evaluates the Variational LSTM-Autoencoder (VLSTM-AE, Proposal P1)
across the chronological test split (D6, D26).

Computes:
- Test-split classification performance (Precision, Recall, FPR, F1).
- Uncertainty distribution: aleatoric, epistemic, and confidence percentage.
- Confidence breakdown: HIGH vs. MODERATE vs. LOW confidence alarms.
- Test injection lead-time replication comparison against Baseline LSTM and PILSTM.
Saves:
- data/processed/vlstm_test_metrics.json
- data/processed/vlstm_lead_times.json
"""

import json
import pathlib
import sys
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.twin_monitors import VLSTMMonitor
from src.config import SEARCH_HORIZON_MINUTES


def evaluate_series(series: str):
    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"

    with open(processed_dir / "vlstm_eval_stats.json", "r") as f:
        stats = json.load(f)
    thresh = float(stats[series]["tau_aleatoric"])

    device = "cuda" if torch.cuda.is_available() else "cpu"
    mon = VLSTMMonitor(
        series_name=series,
        model_path=models_dir / f"vlstm_{series.lower()}.pt",
        norm_stats_path=processed_dir / f"lstm_norm_stats_{series.lower()}.json",
        threshold=thresh,
        n_mc_samples=15,
        device=device,
    )

    labeled_csv = processed_dir / f"{series.lower()}_labeled.csv"
    df = pd.read_csv(labeled_csv, parse_dates=["ts"])
    df = df.dropna(subset=["gap_seconds"]).sort_values(["ts", "gap_seconds"], ascending=[True, False]).reset_index(drop=True)

    cutoff = pd.Timestamp("2018-10-29 11:10:48")
    test_mask = df["ts"] >= cutoff

    print(f"Streaming full series {series} ({len(df)} rows) through VLSTMMonitor...")
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
    df["vlstm_alarm"] = df_mon["alarm"].values
    df["vlstm_score"] = df_mon["score"].values
    df["vlstm_aleatoric"] = df_mon["score_aleatoric"].values
    df["vlstm_epistemic"] = df_mon["score_epistemic"].values
    df["vlstm_uncertainty_pct"] = df_mon["uncertainty_pct"].values
    df["vlstm_category"] = df_mon["alarm_category"].values

    test_df = df[test_mask].dropna(subset=["vlstm_score"]).copy()
    y_true = test_df["is_injected_anomaly"].values.astype(int)
    y_pred = test_df["vlstm_alarm"].values.astype(int)

    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    rec = recall_score(y_true, y_pred, zero_division=0)
    prec = precision_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    category_counts = test_df[test_df["vlstm_alarm"] == True]["vlstm_category"].value_counts().to_dict()

    return {
        "TP": int(tp), "FP": int(fp), "TN": int(tn), "FN": int(fn),
        "FPR": float(fpr), "Precision": float(prec), "Recall": float(rec), "F1": float(f1),
        "threshold": thresh,
        "mean_aleatoric": float(test_df["vlstm_aleatoric"].mean()),
        "mean_epistemic": float(test_df["vlstm_epistemic"].mean()),
        "mean_uncertainty_pct": float(test_df["vlstm_uncertainty_pct"].mean()),
        "category_breakdown": category_counts,
    }


def evaluate_lead_times():
    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"
    inj_log = pd.read_csv(processed_dir / "injection_log.csv")
    status_df = pd.read_csv(processed_dir / "injection_train_test_status.csv")
    three_way_df = pd.read_csv(processed_dir / "three_way_comparison.csv")

    with open(processed_dir / "vlstm_eval_stats.json") as f:
        stats = json.load(f)

    merged = inj_log.merge(status_df[["injection_id", "train_test_status", "start_ts", "end_ts"]], on="injection_id")
    test_injs = merged[merged["train_test_status"] == "test"]

    results = {}
    for _, row in test_injs.iterrows():
        inj_id = row["injection_id"]
        series = row["series"]
        onset_ts = pd.Timestamp(row["start_ts"])
        end_ts = pd.Timestamp(row["end_ts"])
        horizon_end = end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)

        thresh = float(stats[series]["tau_aleatoric"])
        device = "cuda" if torch.cuda.is_available() else "cpu"
        mon = VLSTMMonitor(
            series,
            models_dir / f"vlstm_{series.lower()}.pt",
            processed_dir / f"lstm_norm_stats_{series.lower()}.json",
            thresh,
            n_mc_samples=15,
            device=device,
        )

        df_raw = pd.read_csv(processed_dir / f"{series.lower()}_labeled.csv", parse_dates=["ts"])
        df_clean = df_raw.dropna(subset=["gap_seconds"]).sort_values(["ts", "gap_seconds"]).reset_index(drop=True)

        win_start_ts = onset_ts - pd.Timedelta(hours=2)
        win_indices = df_clean[(df_clean["ts"] >= win_start_ts) & (df_clean["ts"] <= horizon_end + pd.Timedelta(hours=2))].index
        start_idx = win_indices[0]
        end_idx = win_indices[-1]

        for _, r in df_clean.iloc[max(0, start_idx-30):start_idx].iterrows():
            mon.process_event({"ts": r["ts"], "temp_injected": float(r["temp_injected"]), "gap_seconds": float(r["gap_seconds"])})
        mon.alarm_records.clear()

        for _, r in df_clean.iloc[start_idx:end_idx+1].iterrows():
            mon.process_event({"ts": r["ts"], "temp_injected": float(r["temp_injected"]), "gap_seconds": float(r["gap_seconds"])})

        df_eval = pd.DataFrame(mon.alarm_records)
        df_in_horizon = df_eval[(df_eval["ts"] >= onset_ts) & (df_eval["ts"] <= horizon_end)]
        fired = df_in_horizon[df_in_horizon["alarm"] == True]

        tw_match = three_way_df[three_way_df["injection_id"] == inj_id]
        lstm_lead = float(tw_match["lead_time_LSTM_min"].values[0]) if not tw_match.empty and pd.notna(tw_match["lead_time_LSTM_min"].values[0]) else None

        if not fired.empty:
            first_alarm = str(fired.iloc[0]["ts"])
            cat = str(fired.iloc[0]["alarm_category"])
            unc_pct = float(fired.iloc[0]["uncertainty_pct"])
            vlstm_lead = (end_ts - pd.Timestamp(first_alarm)).total_seconds() / 60.0
        else:
            first_alarm = None
            cat = "NO_ALARM"
            unc_pct = None
            vlstm_lead = None

        results[inj_id] = {
            "series": series,
            "type": row["type"],
            "lstm_lead_min": lstm_lead,
            "vlstm_lead_min": vlstm_lead,
            "alarm_category": cat,
            "uncertainty_pct": unc_pct,
            "first_alarm_ts": first_alarm,
        }

    out_file = processed_dir / "vlstm_lead_times.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved test injection lead-time comparison to {out_file}")


def main():
    all_metrics = {}
    for series in ["Out", "In"]:
        print(f"\n================ EVALUATING VLSTM ({series}) ================")
        m = evaluate_series(series)
        all_metrics[series] = m
        print(f"Results for VLSTM {series}:")
        print(f"  Recall:               {m['Recall']*100:.2f}%")
        print(f"  Precision:            {m['Precision']*100:.2f}%")
        print(f"  FPR:                  {m['FPR']*100:.2f}%")
        print(f"  F1:                   {m['F1']:.4f}")
        print(f"  Mean Aleatoric Score: {m['mean_aleatoric']:.4f}")
        print(f"  Mean Epistemic Score: {m['mean_epistemic']:.4f}")
        print(f"  Mean Uncertainty %:   {m['mean_uncertainty_pct']:.2f}%")
        print(f"  Alarm Categories:     {m['category_breakdown']}")

    out_json = REPO_ROOT / "data" / "processed" / "vlstm_test_metrics.json"
    with open(out_json, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"\nSaved metrics to {out_json}")

    print("\nEvaluating test injection lead times...")
    evaluate_lead_times()


if __name__ == "__main__":
    main()
