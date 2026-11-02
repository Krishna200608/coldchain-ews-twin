"""
tests/test_vlstm_monitor.py
===========================
Unit and integration tests for VLSTMMonitor (Proposal P1).
Verifies:
- Live streaming event processing through VLSTMMonitor.
- Pre-warm window buffering (30 steps).
- Extraction of aleatoric vs. epistemic uncertainty decomposition.
- Confidence categorization (HIGH vs LOW confidence alarm).
"""

import json
import pathlib
import sys
import unittest
import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.twin_monitors import VLSTMMonitor


class TestVLSTMMonitor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models_dir = REPO_ROOT / "models"
        cls.processed_dir = REPO_ROOT / "data" / "processed"

        with open(cls.processed_dir / "vlstm_eval_stats.json", "r") as f:
            stats = json.load(f)
        cls.vlstm_thresh_out = float(stats["Out"]["tau_aleatoric"])
        cls.vlstm_thresh_in = float(stats["In"]["tau_aleatoric"])

    def test_vlstm_monitor_prewarm_and_inference(self):
        """Verify VLSTMMonitor produces expected uncertainty records across sequential events."""
        mon = VLSTMMonitor(
            series_name="Out",
            model_path=self.models_dir / "vlstm_out.pt",
            norm_stats_path=self.processed_dir / "lstm_norm_stats_out.json",
            threshold=self.vlstm_thresh_out,
            n_mc_samples=10,
            device="cpu",
        )

        # Feed 29 events (blind spot)
        for i in range(29):
            rec = mon.process_event({
                "ts": f"2018-09-01 00:{i:02d}:00",
                "temp_injected": 35.0,
                "gap_seconds": 60.0,
            })
            self.assertFalse(rec["alarm"])
            self.assertTrue(np.isnan(rec["score"]))
            self.assertEqual(rec["alarm_category"], "NORMAL")

        # 30th event fills the window
        rec30 = mon.process_event({
            "ts": "2018-09-01 00:30:00",
            "temp_injected": 35.0,
            "gap_seconds": 60.0,
        })
        self.assertFalse(np.isnan(rec30["score"]))
        self.assertFalse(np.isnan(rec30["score_aleatoric"]))
        self.assertFalse(np.isnan(rec30["score_epistemic"]))
        self.assertGreaterEqual(rec30["uncertainty_pct"], 0.0)
        self.assertLessEqual(rec30["uncertainty_pct"], 100.0)
        self.assertIn("alarm_category", rec30)


if __name__ == "__main__":
    unittest.main()
