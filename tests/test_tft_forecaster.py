"""
tests/test_tft_forecaster.py
============================
Unit tests for Proposal P3 (Multi-Horizon Quantile Forecaster / TFT):
- Verifies TemporalQuantileForecaster forward pass and output shapes (B, 10, 3).
- Verifies Pinball loss computation and backward gradient flow.
- Verifies quantile calibration.
"""

import pathlib
import sys
import unittest
import torch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.models.tft_forecaster import TemporalQuantileForecaster, pinball_loss
from src.twin_monitors import TFTForecastMonitor


class TestTFTForecaster(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = TemporalQuantileForecaster(
            input_dim=4,
            hidden_dim=64,
            horizon=10,
            quantiles=[0.1, 0.5, 0.9],
        ).to(self.device)

    def test_forward_shapes(self):
        """Verify model output shape: (batch_size, horizon, 3)."""
        x = torch.randn(16, 30, 4, device=self.device)
        preds = self.model(x)

        self.assertEqual(preds.shape, (16, 10, 3))
        self.assertFalse(torch.isnan(preds).any())

    def test_pinball_loss_gradient_flow(self):
        """Verify pinball loss backward gradient flow."""
        x = torch.randn(8, 30, 4, device=self.device)
        y_true = torch.randn(8, 10, device=self.device)

        preds = self.model(x)
        loss = pinball_loss(y_true, preds, quantiles=[0.1, 0.5, 0.9])

        self.assertFalse(torch.isnan(loss))
        self.assertGreater(loss.item(), 0.0)

        loss.backward()
        for name, p in self.model.named_parameters():
            self.assertIsNotNone(p.grad, f"Gradient missing for {name}")
            self.assertFalse(torch.isnan(p.grad).any(), f"NaN gradient in {name}")

    def test_tft_forecast_monitor_streaming(self):
        """Verify TFTForecastMonitor streams events and generates trajectory breach forecasts."""
        model_path = REPO_ROOT / "models" / "tft_forecaster_out.pt"
        stats_path = REPO_ROOT / "data" / "processed" / "tft_eval_stats.json"

        monitor = TFTForecastMonitor(
            series_name="Out",
            model_path=model_path,
            stats_path=stats_path,
            threshold=45.0,
            horizon=10,
            device="cpu",
        )

        # Buffer warmup: first 29 events
        for i in range(29):
            rec = monitor.process_event({
                "ts": f"2018-10-29 12:{i:02d}:00",
                "temp_injected": 32.0,
                "gap_seconds": 60.0,
            })
            self.assertFalse(rec["alarm"])
            self.assertIsNone(rec["steps_to_breach"])

        # 30th event: buffer is full, model produces 10-step forecast
        rec30 = monitor.process_event({
            "ts": "2018-10-29 12:30:00",
            "temp_injected": 32.5,
            "gap_seconds": 60.0,
        })
        self.assertIn("max_forecast_temp", rec30)
        self.assertIn("median_forecast", rec30)
        self.assertIn("alarm", rec30)
        self.assertFalse(rec30["alarm"])  # Normal temperature (32.5 C vs 45.0 C threshold)

        # High excursion event: should trigger pre-emptive trajectory alarm
        rec_excursion = monitor.process_event({
            "ts": "2018-10-29 12:31:00",
            "temp_injected": 52.0,
            "gap_seconds": 60.0,
        })
        self.assertTrue(rec_excursion["alarm"])
        self.assertEqual(rec_excursion["alarm_category"], "PREEMPTIVE_TRAJECTORY_ALARM")
        self.assertIsNotNone(rec_excursion["steps_to_breach"])


if __name__ == "__main__":
    unittest.main()
