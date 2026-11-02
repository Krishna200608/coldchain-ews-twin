"""
scripts/evaluate_evidential_fusion.py
=====================================
Evaluates the Dempster-Shafer Evidential Deep Learning (EDL) multi-detector
fusion layer (Proposal P5) across the chronological test partition (D6, D26).

Computes:
- Test-split classification performance (Precision, Recall, FPR, F1, PR-AUC, ROC-AUC).
- Evidential uncertainty characteristics: mean vacuity u, mean conflict mass K.
- Test injection lead-time replication comparison against Baseline, IF, LSTM, and PILSTM.
Saves:
- data/processed/fusion_test_metrics.json
- data/processed/fusion_lead_times.json
"""

import json
import pathlib
import sys
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    precision_recall_curve,
    auc,
    roc_auc_score,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.twin_monitors import EvidentialFusionMonitor
from src.config import SEARCH_HORIZON_MINUTES


def evaluate_series(series: str):
    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"

    print(f"\nEvaluating Evidential Deep Learning Fusion on {series.upper()} series...")
    dataset_path = processed_dir / f"fusion_dataset_{series.lower()}.npz"
    data = np.load(dataset_path, allow_pickle=True)
    X = data["X"]
    y = data["y"]
    ts = pd.to_datetime(data["ts"])

    cutoff = pd.Timestamp("2018-10-29 11:10:48")
    test_mask = np.asarray(ts >= cutoff)

    X_test = X[test_mask]
    y_test = y[test_mask]
    ts_test = pd.Series(ts)[test_mask].reset_index(drop=True)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    mon = EvidentialFusionMonitor(
        series_name=series,
        model_path=models_dir / f"evidential_fusion_{series.lower()}.pt",
        stats_path=processed_dir / "fusion_eval_stats.json",
        prob_threshold=0.5,
        max_vacuity=0.85,
        device=device,
    )

    preds = []
    probs = []
    vacuities = []
    conflicts = []

    print(f"Streaming {len(X_test)} test-partition samples through EvidentialFusionMonitor...")
    for i in range(len(X_test)):
        rec = mon.process_event(
            event={"ts": ts_test.iloc[i]},
            feature_vector=X_test[i],
        )
        preds.append(int(rec["alarm"]))
        probs.append(float(rec["prob_alarm"]))
        vacuities.append(float(rec["vacuity"]))
        conflicts.append(float(rec["conflict_mass_K"]))

    y_pred = np.array(preds)
    y_prob = np.array(probs)
    vacuities = np.array(vacuities)
    conflicts = np.array(conflicts)

    cm = confusion_matrix(y_test, y_pred)
    tn, fp, fn, tp = cm.ravel()
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    p_curve, r_curve, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = auc(r_curve, p_curve)
    roc_auc = roc_auc_score(y_test, y_prob) if len(np.unique(y_test)) > 1 else 0.5

    pos_mask = (y_test == 1)
    neg_mask = (y_test == 0)

    mean_vacuity_pos = float(vacuities[pos_mask].mean()) if pos_mask.any() else 0.0
    mean_vacuity_neg = float(vacuities[neg_mask].mean()) if neg_mask.any() else 0.0
    mean_conflict_pos = float(conflicts[pos_mask].mean()) if pos_mask.any() else 0.0
    mean_conflict_neg = float(conflicts[neg_mask].mean()) if neg_mask.any() else 0.0

    print(f"[{series.upper()} Test Results (N={len(y_test)})]")
    print(f"  Precision: {prec * 100:.2f}% | Recall: {rec * 100:.2f}% | F1: {f1:.4f}")
    print(f"  FPR: {fpr * 100:.2f}% (FP={fp}, TP={tp}, FN={fn}, TN={tn})")
    print(f"  PR-AUC: {pr_auc:.4f} | ROC-AUC: {roc_auc:.4f}")
    print(f"  Vacuity (u): Anomaly={mean_vacuity_pos:.4f}, Normal={mean_vacuity_neg:.4f}")
    print(f"  Conflict (K): Anomaly={mean_conflict_pos:.4f}, Normal={mean_conflict_neg:.4f}")

    return {
        "series": series,
        "n_test_samples": int(len(y_test)),
        "n_positives": int(y_test.sum()),
        "confusion_matrix": {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)},
        "precision": float(prec),
        "recall": float(rec),
        "f1": float(f1),
        "fpr": float(fpr),
        "pr_auc": float(pr_auc),
        "roc_auc": float(roc_auc),
        "mean_vacuity_anomaly": mean_vacuity_pos,
        "mean_vacuity_normal": mean_vacuity_neg,
        "mean_conflict_anomaly": mean_conflict_pos,
        "mean_conflict_normal": mean_conflict_neg,
    }


def evaluate_lead_times():
    processed_dir = REPO_ROOT / "data" / "processed"
    models_dir = REPO_ROOT / "models"

    inj_log = pd.read_csv(processed_dir / "injection_log.csv")
    status_df = pd.read_csv(processed_dir / "injection_train_test_status.csv")
    three_way_df = pd.read_csv(processed_dir / "three_way_comparison.csv")

    try:
        with open(processed_dir / "pilstm_lead_times.json") as f:
            pilstm_leads = json.load(f)
    except Exception:
        pilstm_leads = {}

    try:
        with open(processed_dir / "vlstm_lead_times.json") as f:
            vlstm_leads = json.load(f)
    except Exception:
        vlstm_leads = {}

    merged = inj_log.merge(
        status_df[["injection_id", "train_test_status", "start_ts", "end_ts"]],
        on="injection_id",
    )
    test_injs = merged[merged["train_test_status"] == "test"]

    device = "cuda" if torch.cuda.is_available() else "cpu"
    results = {}

    for _, row in test_injs.iterrows():
        inj_id = row["injection_id"]
        series = row["series"]
        onset_ts = pd.Timestamp(row["start_ts"])
        end_ts = pd.Timestamp(row["end_ts"])
        horizon_end = end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)

        dataset_path = processed_dir / f"fusion_dataset_{series.lower()}.npz"
        data = np.load(dataset_path, allow_pickle=True)
        X = data["X"]
        ts_all = pd.to_datetime(data["ts"])

        mon = EvidentialFusionMonitor(
            series_name=series,
            model_path=models_dir / f"evidential_fusion_{series.lower()}.pt",
            stats_path=processed_dir / "fusion_eval_stats.json",
            prob_threshold=0.5,
            max_vacuity=0.85,
            device=device,
        )

        # Slice around injection window for fast evaluation
        ts_s = pd.Series(pd.to_datetime(data["ts"]))
        win_start_ts = onset_ts - pd.Timedelta(hours=2)
        win_end_ts = horizon_end + pd.Timedelta(hours=2)
        idx_mask = (ts_s >= win_start_ts) & (ts_s <= win_end_ts)
        X_slice = X[idx_mask.values]
        ts_slice = ts_s[idx_mask].reset_index(drop=True)

        for i in range(len(X_slice)):
            mon.process_event(
                event={"ts": ts_slice.iloc[i]},
                feature_vector=X_slice[i],
            )

        df_eval = pd.DataFrame(mon.alarm_records)
        df_in_horizon = df_eval[(df_eval["ts"] >= onset_ts) & (df_eval["ts"] <= horizon_end)]
        fired = df_in_horizon[df_in_horizon["alarm"] == True]

        tw_match = three_way_df[three_way_df["injection_id"] == inj_id]
        if not tw_match.empty and pd.notna(tw_match["lead_time_LSTM_min"].values[0]):
            lstm_lead = float(tw_match["lead_time_LSTM_min"].values[0])
        else:
            lstm_lead = None

        if not tw_match.empty and pd.notna(tw_match["lead_time_IF_min"].values[0]):
            if_lead = float(tw_match["lead_time_IF_min"].values[0])
        else:
            if_lead = None

        pi_lead = pilstm_leads.get(inj_id, {}).get("pilstm_lead_min")
        vl_lead = vlstm_leads.get(inj_id, {}).get("vlstm_lead_min")

        if not fired.empty:
            first_alarm = str(fired.iloc[0]["ts"])
            cat = str(fired.iloc[0]["alarm_category"])
            prob_alarm = float(fired.iloc[0]["prob_alarm"])
            vac = float(fired.iloc[0]["vacuity"])
            k_conf = float(fired.iloc[0]["conflict_mass_K"])
            fusion_lead = (end_ts - pd.Timestamp(first_alarm)).total_seconds() / 60.0
        else:
            first_alarm = None
            cat = "NO_ALARM"
            prob_alarm = None
            vac = None
            k_conf = None
            fusion_lead = None

        results[inj_id] = {
            "series": series,
            "type": row["type"],
            "if_lead_min": if_lead,
            "lstm_lead_min": lstm_lead,
            "pilstm_lead_min": pi_lead,
            "vlstm_lead_min": vl_lead,
            "fusion_lead_min": fusion_lead,
            "prob_alarm": prob_alarm,
            "vacuity": vac,
            "conflict_mass_K": k_conf,
            "alarm_category": cat,
            "first_alarm_ts": first_alarm,
        }

    out_file = processed_dir / "fusion_lead_times.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved test injection lead-time comparison to {out_file}")
    return results


def main():
    metrics = {
        "Out": evaluate_series("Out"),
        "In": evaluate_series("In"),
    }
    metrics_file = REPO_ROOT / "data" / "processed" / "fusion_test_metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"\nSaved full fusion test metrics to {metrics_file}")

    leads = evaluate_lead_times()
    print("\n" + "=" * 80)
    print("DEMPSTER-SHAFER EVIDENTIAL FUSION (P5) — TEST INJECTION LEAD TIMES (D26)")
    print("=" * 80)
    print(f"{'Injection ID':<18} {'Series':<6} {'Type':<10} {'IF Lead':<10} {'LSTM Lead':<10} {'PILSTM':<10} {'VLSTM':<10} {'Fusion Lead':<12}")
    print("-" * 80)
    for inj_id, res in leads.items():
        if_s = f"{res['if_lead_min']:+.1f}" if res['if_lead_min'] is not None else "N/A"
        l_s = f"{res['lstm_lead_min']:+.1f}" if res['lstm_lead_min'] is not None else "N/A"
        pi_s = f"{res['pilstm_lead_min']:+.1f}" if res['pilstm_lead_min'] is not None else "N/A"
        vl_s = f"{res['vlstm_lead_min']:+.1f}" if res['vlstm_lead_min'] is not None else "N/A"
        fu_s = f"{res['fusion_lead_min']:+.1f} min" if res['fusion_lead_min'] is not None else "NO_ALARM"
        print(f"{inj_id:<18} {res['series']:<6} {res['type']:<10} {if_s:<10} {l_s:<10} {pi_s:<10} {vl_s:<10} {fu_s:<12}")
    print("=" * 80)


if __name__ == "__main__":
    main()
