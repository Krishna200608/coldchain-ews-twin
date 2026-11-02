"""
scripts/evaluate_tft.py
=======================
Evaluates the Multi-Horizon Quantile Temporal Forecaster (Proposal P3)
across the 6 test-side synthetic injections (D26 benchmark).

Computes:
- Pre-emptive early warning lead times against standard baseline thresholds.
- Comparison against Baseline, IF, LSTM, PILSTM, VLSTM, and Evidential Fusion.
Saves:
- data/processed/tft_lead_times.json
"""

import json
import pathlib
import sys
import pandas as pd
import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.twin_monitors import TFTForecastMonitor
from src.config import SEARCH_HORIZON_MINUTES


def evaluate_tft_lead_times():
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

    try:
        with open(processed_dir / "fusion_lead_times.json") as f:
            fusion_leads = json.load(f)
    except Exception:
        fusion_leads = {}

    # Thresholds for Out and In series
    thresholds = {
        "Out": 47.6993,  # Baseline clean mean + 2 sigma
        "In": 34.9301,   # Baseline clean mean + 2 sigma
    }

    merged = inj_log.merge(
        status_df[["injection_id", "train_test_status", "start_ts", "end_ts"]],
        on="injection_id",
    )
    test_injs = merged[merged["train_test_status"] == "test"]

    results = {}
    for _, row in test_injs.iterrows():
        inj_id = row["injection_id"]
        series = row["series"]
        onset_ts = pd.Timestamp(row["start_ts"])
        end_ts = pd.Timestamp(row["end_ts"])
        horizon_end = end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)

        thresh = thresholds[series]
        mon = TFTForecastMonitor(
            series_name=series,
            model_path=models_dir / f"tft_forecaster_{series.lower()}.pt",
            stats_path=processed_dir / "tft_eval_stats.json",
            threshold=thresh,
            horizon=10,
            device="cuda",
        )

        df_raw = pd.read_csv(processed_dir / f"{series.lower()}_labeled.csv", parse_dates=["ts"])
        df_clean = df_raw.dropna(subset=["gap_seconds"]).sort_values(["ts", "gap_seconds"]).reset_index(drop=True)

        win_start_ts = onset_ts - pd.Timedelta(hours=2)
        win_indices = df_clean[(df_clean["ts"] >= win_start_ts) & (df_clean["ts"] <= horizon_end + pd.Timedelta(hours=2))].index
        start_idx = win_indices[0]
        end_idx = win_indices[-1]

        # Pre-warm 30 readings
        for _, r in df_clean.iloc[max(0, start_idx - 30) : start_idx].iterrows():
            mon.process_event({
                "ts": r["ts"],
                "temp_injected": float(r["temp_injected"]),
                "gap_seconds": float(r["gap_seconds"]),
            })
        mon.alarm_records.clear()

        # Evaluate window
        for _, r in df_clean.iloc[start_idx : end_idx + 1].iterrows():
            mon.process_event({
                "ts": r["ts"],
                "temp_injected": float(r["temp_injected"]),
                "gap_seconds": float(r["gap_seconds"]),
            })

        df_eval = pd.DataFrame(mon.alarm_records)
        df_in_horizon = df_eval[(df_eval["ts"] >= onset_ts) & (df_eval["ts"] <= horizon_end)]
        fired = df_in_horizon[df_in_horizon["alarm"] == True]

        tw_match = three_way_df[three_way_df["injection_id"] == inj_id]
        lstm_lead = float(tw_match["lead_time_LSTM_min"].values[0]) if not tw_match.empty and pd.notna(tw_match["lead_time_LSTM_min"].values[0]) else None
        if_lead = float(tw_match["lead_time_IF_min"].values[0]) if not tw_match.empty and pd.notna(tw_match["lead_time_IF_min"].values[0]) else None
        base_lead = float(tw_match["baseline_lead_time_min"].values[0]) if not tw_match.empty and pd.notna(tw_match["baseline_lead_time_min"].values[0]) else None

        pi_lead = pilstm_leads.get(inj_id, {}).get("pilstm_lead_min")
        vl_lead = vlstm_leads.get(inj_id, {}).get("vlstm_lead_min")
        fu_lead = fusion_leads.get(inj_id, {}).get("fusion_lead_min")

        if not fired.empty:
            first_alarm = str(fired.iloc[0]["ts"])
            steps = int(fired.iloc[0]["steps_to_breach"]) if pd.notna(fired.iloc[0]["steps_to_breach"]) else 1
            max_p = float(fired.iloc[0]["max_forecast_temp"])
            tft_lead = (end_ts - pd.Timestamp(first_alarm)).total_seconds() / 60.0
        else:
            first_alarm = None
            steps = None
            max_p = None
            tft_lead = None

        results[inj_id] = {
            "series": series,
            "type": row["type"],
            "base_lead_min": base_lead,
            "if_lead_min": if_lead,
            "lstm_lead_min": lstm_lead,
            "pilstm_lead_min": pi_lead,
            "vlstm_lead_min": vl_lead,
            "fusion_lead_min": fu_lead,
            "tft_lead_min": tft_lead,
            "steps_to_breach": steps,
            "max_forecast_temp": max_p,
            "first_alarm_ts": first_alarm,
        }

    out_file = processed_dir / "tft_lead_times.json"
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Saved TFT lead times to {out_file}")

    print("\n" + "=" * 95)
    print("ALL 5 RESEARCH PROPOSALS — FULL BENCHMARK LEAD-TIME MATRIX (D26)")
    print("=" * 95)
    print(f"{'Injection ID':<18} {'Series':<6} {'Type':<9} {'Base':<8} {'IF':<8} {'LSTM':<8} {'P2-PILSTM':<10} {'P1-VLSTM':<10} {'P5-EDL':<10} {'P3-TFT':<10}")
    print("-" * 95)
    for inj_id, res in results.items():
        b_s = f"{res['base_lead_min']:+.1f}" if res['base_lead_min'] is not None else "N/A"
        if_s = f"{res['if_lead_min']:+.1f}" if res['if_lead_min'] is not None else "N/A"
        l_s = f"{res['lstm_lead_min']:+.1f}" if res['lstm_lead_min'] is not None else "N/A"
        pi_s = f"{res['pilstm_lead_min']:+.1f}" if res['pilstm_lead_min'] is not None else "N/A"
        vl_s = f"{res['vlstm_lead_min']:+.1f}" if res['vlstm_lead_min'] is not None else "N/A"
        fu_s = f"{res['fusion_lead_min']:+.1f}" if res['fusion_lead_min'] is not None else "N/A"
        tf_s = f"{res['tft_lead_min']:+.1f}" if res['tft_lead_min'] is not None else "N/A"
        print(f"{inj_id:<18} {res['series']:<6} {res['type']:<9} {b_s:<8} {if_s:<8} {l_s:<8} {pi_s:<10} {vl_s:<10} {fu_s:<10} {tf_s:<10}")
    print("=" * 95)

    return results


if __name__ == "__main__":
    evaluate_tft_lead_times()
