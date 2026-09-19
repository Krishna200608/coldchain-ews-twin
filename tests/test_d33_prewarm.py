"""
tests/test_d33_prewarm.py
=========================
Automated test suite verifying Milestone 6 implementation requirements:
- D33 Pre-warm verification: 18/18 exact matches against twin_crosscheck_report.csv
  for all 6 test-side injections across all 3 monitors (Baseline, IF, LSTM).
- D32 Startup check verification: verifies validation passes when files exist,
  and raises appropriate errors/instructions when artifacts are missing.

STRUCTURAL PROXY NOTICE
-----------------------
All telemetry derives from IOT-temp.csv (generic IoT temperature sensor log),
NOT refrigerated-transport operations. All injected anomalies are synthetic
proxy constructs. Detectors carry no food-safety significance.
See docs/AD_LOG.md (D1–D34).
"""

import pathlib
import sys
import unittest
import pandas as pd

# Add repo root and src to path
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.twin_monitors import BaselineMonitor, IFMonitor, LSTMMonitor
from src.config import SEARCH_HORIZON_MINUTES


def verify_d32_startup(models_dir: pathlib.Path, processed_dir: pathlib.Path) -> tuple[bool, list[str]]:
    """
    Validation logic for D32 Startup Check.
    Returns (is_valid, list_of_missing_files).
    """
    required_files = [
        models_dir / "isolation_forest_out.joblib",
        models_dir / "isolation_forest_in.joblib",
        models_dir / "lstm_out.h5",
        models_dir / "lstm_in.h5",
        processed_dir / "lstm_norm_stats_out.json",
        processed_dir / "lstm_norm_stats_in.json",
        processed_dir / "out_features.csv",
        processed_dir / "in_features.csv",
        processed_dir / "out_labeled.csv",
        processed_dir / "in_labeled.csv",
        processed_dir / "twin_crosscheck_report.csv",
        processed_dir / "three_way_comparison.csv",
    ]
    missing = [str(f) for f in required_files if not f.exists()]
    return len(missing) == 0, missing


class TestMilestone6(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models_dir = REPO_ROOT / "models"
        cls.processed_dir = REPO_ROOT / "data" / "processed"
        cls.inj_log = pd.read_csv(cls.processed_dir / "injection_log.csv")
        cls.status_df = pd.read_csv(cls.processed_dir / "injection_train_test_status.csv")
        cls.cross_df = pd.read_csv(cls.processed_dir / "twin_crosscheck_report.csv")

    def test_d32_startup_check_existing_files(self):
        """Verify D32 passes when all required model and data artifacts exist."""
        valid, missing = verify_d32_startup(self.models_dir, self.processed_dir)
        self.assertTrue(valid, f"Missing files in repo: {missing}")
        self.assertEqual(len(missing), 0)

    def test_d32_startup_check_missing_files(self):
        """Verify D32 catches missing files and reports remediation."""
        fake_models = REPO_ROOT / "models_non_existent"
        valid, missing = verify_d32_startup(fake_models, self.processed_dir)
        self.assertFalse(valid)
        self.assertGreater(len(missing), 0)

    def test_d33_prewarm_reproduces_exact_alarms(self):
        """
        Verify D33 silent buffer pre-warming:
        Iterates through all 6 test injections, pre-warms IF (10) and LSTM (30),
        and asserts bit-for-bit replication of all 18 test-side alarm timestamps
        matching twin_crosscheck_report.csv.
        """
        merged = self.inj_log.merge(
            self.status_df[["injection_id", "train_test_status", "start_ts", "end_ts"]],
            on="injection_id",
        )
        test_injections = merged[merged["train_test_status"] == "test"].copy()
        self.assertEqual(len(test_injections), 6, "Expected exactly 6 test-side injections")

        matches = 0
        total_evals = 0

        # Cache datasets to speed up test execution
        dfs = {}
        for s in ["out", "in"]:
            raw = pd.read_csv(self.processed_dir / f"{s}_labeled.csv", parse_dates=["ts"])
            dfs[s] = (
                raw.dropna(subset=["gap_seconds"])
                .sort_values(["ts", "gap_seconds"], ascending=[True, False], kind="stable")
                .reset_index(drop=True)
            )

        for _, row in test_injections.iterrows():
            inj_id = row["injection_id"]
            series = row["series"]
            onset_ts = pd.Timestamp(row["start_ts"])
            end_ts = pd.Timestamp(row["end_ts"])
            horizon_end = end_ts + pd.Timedelta(minutes=SEARCH_HORIZON_MINUTES)

            # Jump-to-injection window with 2 hours padding
            win_start_ts = onset_ts - pd.Timedelta(hours=2)
            win_end_ts = horizon_end + pd.Timedelta(hours=2)

            df_clean = dfs[series.lower()]
            win_indices = df_clean[(df_clean["ts"] >= win_start_ts) & (df_clean["ts"] <= win_end_ts)].index
            win_start_idx = win_indices[0]
            win_end_idx = win_indices[-1]

            # Instantiate monitors
            base_mon = BaselineMonitor(series, self.processed_dir / f"{series.lower()}_features.csv")
            if_mon = IFMonitor(series, self.models_dir / f"isolation_forest_{series.lower()}.joblib")
            lstm_thresh = 1.010091 if series == "Out" else 1.512753
            lstm_mon = LSTMMonitor(
                series,
                self.models_dir / f"lstm_{series.lower()}.h5",
                self.processed_dir / f"lstm_norm_stats_{series.lower()}.json",
                lstm_thresh,
            )

            # Pre-warm IF (10 rows immediately prior to visible window)
            prewarm_if_rows = df_clean.iloc[max(0, win_start_idx - 10) : win_start_idx]
            for _, r in prewarm_if_rows.iterrows():
                if_mon.process_event({
                    "ts": r["ts"],
                    "temp_injected": float(r["temp_injected"]),
                    "gap_seconds": float(r["gap_seconds"]),
                })
            if_mon.alarm_records.clear()

            # Pre-warm LSTM (30 rows immediately prior to visible window)
            prewarm_lstm_rows = df_clean.iloc[max(0, win_start_idx - 30) : win_start_idx]
            for _, r in prewarm_lstm_rows.iterrows():
                lstm_mon.process_event({
                    "ts": r["ts"],
                    "temp_injected": float(r["temp_injected"]),
                    "gap_seconds": float(r["gap_seconds"]),
                })
            lstm_mon.alarm_records.clear()

            # Evaluate visible window
            vis_rows = df_clean.iloc[win_start_idx : win_end_idx + 1]
            for _, r in vis_rows.iterrows():
                ev = {
                    "ts": r["ts"],
                    "temp_injected": float(r["temp_injected"]),
                    "gap_seconds": float(r["gap_seconds"]),
                }
                base_mon.process_event(ev)
                if_mon.process_event(ev)
                lstm_mon.process_event(ev)

            # Evaluate each monitor's first alarm in [onset_ts, horizon_end]
            for det_name, mon in [("baseline", base_mon), ("if", if_mon), ("lstm", lstm_mon)]:
                total_evals += 1
                df_a = pd.DataFrame(mon.alarm_records)
                in_win = df_a[(df_a["ts"] >= onset_ts) & (df_a["ts"] <= horizon_end) & (df_a["alarm"] == True)]
                live_ts = in_win.iloc[0]["ts"] if not in_win.empty else None

                expected_row = self.cross_df[
                    (self.cross_df["injection_id"] == inj_id) & (self.cross_df["detector"] == det_name)
                ].iloc[0]
                expected_ts = (
                    pd.Timestamp(expected_row["live_alarm_timestamp"])
                    if pd.notna(expected_row["live_alarm_timestamp"])
                    else None
                )

                self.assertEqual(
                    live_ts,
                    expected_ts,
                    f"Mismatch on {inj_id} ({det_name}): got {live_ts}, expected {expected_ts}",
                )
                matches += 1

        self.assertEqual(matches, 18)
        self.assertEqual(total_evals, 18)


if __name__ == "__main__":
    unittest.main()
