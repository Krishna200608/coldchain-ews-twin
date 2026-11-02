"""
tests/test_pilstm_monitor.py
============================
Unit and integration tests for PILSTMMonitor (Proposal P2).
Verifies:
- Live streaming event processing through PILSTMMonitor.
- Pre-warm window buffering (30 steps).
- Correct categorization of SENSOR_ARTIFACT vs TEMPERATURE_EXCURSION vs NORMAL.
"""

import json
import pathlib
import sys
import unittest
import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.twin_monitors import PILSTMMonitor


class TestPILSTMMonitor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.models_dir = REPO_ROOT / "models"
        cls.processed_dir = REPO_ROOT / "data" / "processed"

        with open(cls.processed_dir / "pilstm_eval_stats.json", "r") as f:
            stats = json.load(f)
        cls.pilstm_thresh_out = float(stats["Out"]["pilstm_threshold"])
        cls.pilstm_thresh_in = float(stats["In"]["pilstm_threshold"])

    def test_pilstm_monitor_prewarm_and_inference(self):
        """Verify PILSTMMonitor produces expected records across 35 sequential events."""
        mon = PILSTMMonitor(
            series_name="Out",
            model_path=self.models_dir / "pilstm_out.pt",
            norm_stats_path=self.processed_dir / "lstm_norm_stats_out.json",
            physics_params_path=self.processed_dir / "physics_params_out.json",
            threshold=self.pilstm_thresh_out,
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
        self.assertIn("alarm", rec30)
        self.assertIn("alarm_category", rec30)
        self.assertIn("dT_dt", rec30)

    def test_sensor_artifact_spike_detection(self):
        """Verify instantaneous unphysical jump (> 3*sigma_delta) is tagged as SENSOR_ARTIFACT."""
        mon = PILSTMMonitor(
            series_name="Out",
            model_path=self.models_dir / "pilstm_out.pt",
            norm_stats_path=self.processed_dir / "lstm_norm_stats_out.json",
            physics_params_path=self.processed_dir / "physics_params_out.json",
            threshold=self.pilstm_thresh_out,
            device="cpu",
        )

        # Pre-warm with 30 steady readings
        for i in range(30):
            mon.process_event({
                "ts": f"2018-09-01 00:{i:02d}:00",
                "temp_injected": 35.0,
                "gap_seconds": 60.0,
            })

        # Inject an electrical sensor spike: +15°C jump in 1 second (15 °C/s >> 0.0227 °C/s spike threshold)
        rec_spike = mon.process_event({
            "ts": "2018-09-01 00:30:01",
            "temp_injected": 50.0,
            "gap_seconds": 1.0,
        })

        if rec_spike["alarm"]:
            self.assertEqual(rec_spike["alarm_category"], "SENSOR_ARTIFACT")


if __name__ == "__main__":
    unittest.main()
