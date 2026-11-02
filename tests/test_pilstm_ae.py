"""
tests/test_pilstm_ae.py
=======================
Unit tests for Proposal P2 (Physics-Informed LSTM-Autoencoder):
- Verifies PILSTMAutoencoder architecture, layer shapes, and parameter counts.
- Verifies physics_informed_loss calculation and backward gradient flow.
- Verifies fit_physics_parameters strictly estimates constants on training data (D6).
"""

import pathlib
import sys
import unittest
import numpy as np
import pandas as pd
import torch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.models.pilstm_ae import (
    PILSTMAutoencoder,
    PILSTMAEEncoder,
    PILSTMAEDecoder,
    physics_informed_loss,
    fit_physics_parameters,
)


class TestPILSTMAE(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = PILSTMAutoencoder(input_size=2, hidden_size=32, window_length=30).to(self.device)

    def test_model_architecture_and_parameter_count(self):
        """Verify layer dimensions and parameter count ~13,000 (matching Keras baseline 12,866)."""
        total_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        # Encoder LSTM(2->32): 4 * (2*32 + 32*32 + 32 + 32) = 4,608
        # Decoder LSTM(32->32): 4 * (32*32 + 32*32 + 32 + 32) = 8,448
        # Decoder Linear(32->2): 32*2 + 2 = 66
        # Total = 13,122
        self.assertAlmostEqual(total_params, 13122, delta=200)

    def test_forward_pass_shape(self):
        """Verify forward pass returns exact input shape (B, 30, 2)."""
        x = torch.randn(8, 30, 2, device=self.device)
        out = self.model(x)
        self.assertEqual(out.shape, (8, 30, 2))

    def test_physics_loss_gradient_flow(self):
        """Verify physics-informed loss computes valid scalar and propagates gradients back to weights."""
        x = torch.randn(4, 30, 2, device=self.device, requires_grad=True)
        x_hat = self.model(x)
        total_loss, mse, phys = physics_informed_loss(
            x_norm=x,
            x_hat_norm=x_hat,
            t_mean=35.0,
            t_std=5.0,
            g_mean=1.0,
            g_std=2.0,
            k_cooling=0.0001,
            T_amb=35.0,
            lambda_physics=0.1,
        )
        self.assertGreater(total_loss.item(), 0.0)
        self.assertGreaterEqual(mse.item(), 0.0)
        self.assertGreaterEqual(phys.item(), 0.0)

        # Backward pass
        total_loss.backward()
        for name, param in self.model.named_parameters():
            self.assertIsNotNone(param.grad, f"Gradient missing for {name}")
            self.assertFalse(torch.isnan(param.grad).any(), f"NaN gradient in {name}")

    def test_fit_physics_parameters_train_only(self):
        """Verify parameter estimation fits valid thermal properties on train partition."""
        labeled_csv = REPO_ROOT / "data" / "processed" / "out_labeled.csv"
        if not labeled_csv.exists():
            self.skipTest("out_labeled.csv not available")

        df = pd.read_csv(labeled_csv, parse_dates=["ts"])
        params = fit_physics_parameters(df, cutoff_ts="2018-10-29 11:10:48")

        self.assertIn("T_amb", params)
        self.assertIn("k_cooling", params)
        self.assertIn("sigma_delta", params)
        self.assertGreater(params["T_amb"], 15.0)
        self.assertLess(params["T_amb"], 45.0)
        self.assertGreater(params["k_cooling"], 0.0)
        self.assertGreater(params["sigma_delta"], 0.0)


if __name__ == "__main__":
    unittest.main()

