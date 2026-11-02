"""
tests/test_evidential_fusion.py
===============================
Unit tests for Proposal P5 (Evidential Deep Learning & Dempster-Shafer Fusion):
- Verifies EvidentialFusionMLP architecture, Dirichlet parameters, and vacuity mass.
- Verifies evidential loss (ACE + Dirichlet KL) backward gradient flow.
- Verifies Dempster-Shafer combination and conflict mass K calculation.
"""

import pathlib
import sys
import unittest
import torch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.fusion.evidential_fusion import (
    EvidentialFusionMLP,
    evidential_loss,
    kl_divergence_dirichlet,
    dempster_shafer_combine,
)
from src.twin_monitors import EvidentialFusionMonitor


class TestEvidentialFusion(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.mlp = EvidentialFusionMLP(input_dim=7, hidden_dim=32, latent_dim=16).to(self.device)

    def test_mlp_forward_and_shapes(self):
        """Verify MLP output shapes: prob (B, 1), uncertainty (B, 1), evidence (B, 2)."""
        x = torch.randn(16, 7, device=self.device)
        prob, u, evidence = self.mlp(x)

        self.assertEqual(prob.shape, (16, 1))
        self.assertEqual(u.shape, (16, 1))
        self.assertEqual(evidence.shape, (16, 2))

        # Evidence must be strictly non-negative
        self.assertTrue((evidence >= 0.0).all())
        # Prob and uncertainty in [0, 1]
        self.assertTrue((prob >= 0.0).all() and (prob <= 1.0).all())
        self.assertTrue((u > 0.0).all() and (u <= 1.0).all())

    def test_evidential_loss_gradient_flow(self):
        """Verify evidential loss computes valid scalar and propagates gradients back to weights."""
        x = torch.randn(8, 7, device=self.device)
        # Binary one-hot targets [normal, alarm]
        y_targets = torch.tensor([[1.0, 0.0], [0.0, 1.0]] * 4, device=self.device)

        _, _, evidence = self.mlp(x)
        alpha = evidence + 1.0
        loss, ace, kl = evidential_loss(alpha, y_targets, lambda_kl=0.01)

        self.assertFalse(torch.isnan(loss))
        self.assertGreater(loss.item(), 0.0)

        loss.backward()
        for name, p in self.mlp.named_parameters():
            self.assertIsNotNone(p.grad, f"Gradient missing for {name}")
            self.assertFalse(torch.isnan(p.grad).any(), f"NaN gradient in {name}")

    def test_dempster_shafer_agreement_and_conflict(self):
        """Verify Dempster-Shafer combination yields low conflict when models agree, high when they disagree."""
        # Agreement: both high alarm
        prob_agree, u_agree, k_agree = dempster_shafer_combine(0.9, 0.9, 0.9)
        self.assertGreater(prob_agree, 0.9)
        self.assertLess(k_agree, 0.2)

        # Conflict: one says 0.99 alarm, other says 0.01 alarm
        prob_conf, u_conf, k_conf = dempster_shafer_combine(0.99, 0.01, 0.5)
        self.assertGreater(k_conf, 0.9)  # High conflict

    def test_evidential_fusion_monitor_streaming(self):
        """Verify EvidentialFusionMonitor handles streaming inputs, detector records, and edge cases."""
        model_path = REPO_ROOT / "models" / "evidential_fusion_out.pt"
        stats_path = REPO_ROOT / "data" / "processed" / "fusion_eval_stats.json"

        monitor = EvidentialFusionMonitor(
            series_name="Out",
            model_path=model_path,
            stats_path=stats_path,
            prob_threshold=0.5,
            device="cpu",
        )

        event = {"ts": "2018-10-29 12:00:00", "temp_injected": 36.5, "gap_seconds": 120.0}

        # Case 1: Un-warmed / missing detector inputs
        rec1 = monitor.process_event(event)
        self.assertFalse(rec1["alarm"])
        self.assertEqual(rec1["vacuity"], 1.0)
        self.assertEqual(rec1["alarm_category"], "NORMAL")

        # Case 2: Normal detector inputs
        norm_records = {
            "baseline": {"score": 0.1},
            "if": {"score": 0.08},
            "lstm": {"score": 0.12},
            "vlstm": {"score_aleatoric": 0.15, "score_epistemic": 0.01},
            "pilstm": {"physics_residual": 0.0001},
        }
        rec2 = monitor.process_event(event, detector_records=norm_records)
        self.assertIn("prob_alarm", rec2)
        self.assertIn("vacuity", rec2)
        self.assertIn("conflict_mass_K", rec2)
        self.assertFalse(rec2["alarm"])

        # Case 3: High anomaly detector inputs (matching positive anomaly excursion)
        event_anom = {"ts": "2018-10-29 12:00:00", "temp_injected": 48.0, "gap_seconds": 0.0}
        anom_records = {
            "baseline": {"score": 1.14},
            "if": {"score": -0.174},
            "lstm": {"score": 2.23},
            "vlstm": {"score_aleatoric": 2.31, "score_epistemic": 0.135},
            "pilstm": {"physics_residual": 3.6e-8},
        }
        rec3 = monitor.process_event(event_anom, detector_records=anom_records)
        self.assertTrue(rec3["prob_alarm"] > 0.5)
        self.assertTrue(rec3["alarm"])
        self.assertIn("EVIDENTIAL", rec3["alarm_category"])


if __name__ == "__main__":
    unittest.main()
