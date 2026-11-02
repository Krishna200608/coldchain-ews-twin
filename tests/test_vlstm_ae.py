"""
tests/test_vlstm_ae.py
======================
Unit tests for Proposal P1 (Variational LSTM-Autoencoder):
- Verifies VLSTMAutoencoder architecture, latent projections, and parameter count.
- Verifies ELBO loss (MSE + beta * KL) calculation and backward gradient flow.
- Verifies Monte Carlo uncertainty sampling and uncertainty percentage decomposition.
"""

import pathlib
import sys
import unittest
import torch

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "src"))

from src.models.vlstm_ae import (
    VLSTMAutoencoder,
    VLSTMEncoder,
    VLSTMDecoder,
    vlstm_loss,
)


class TestVLSTMAE(unittest.TestCase):
    def setUp(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = VLSTMAutoencoder(
            input_size=2, hidden_size=64, latent_dim=16, window_length=30
        ).to(self.device)

    def test_model_architecture_and_parameter_count(self):
        """Verify layer dimensions and parameter count ~45,000."""
        total_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        # Encoder:
        #   LSTM(2->64): 4 * (2*64 + 64*64 + 64 + 64) = 17,408
        #   Linear(64->16) mu: 64*16 + 16 = 1,040
        #   Linear(64->16) logvar: 64*16 + 16 = 1,040
        # Decoder:
        #   LSTM(16->64): 4 * (16*64 + 64*64 + 64 + 64) = 20,992
        #   Linear(64->2): 64*2 + 2 = 130
        # Total = 40,610
        self.assertAlmostEqual(total_params, 40610, delta=1000)

    def test_forward_pass_shape(self):
        """Verify forward pass returns reconstruction (B, 30, 2) and latent stats (B, 16)."""
        x = torch.randn(8, 30, 2, device=self.device)
        self.model.train()
        recon, mu, logvar = self.model(x)
        self.assertEqual(recon.shape, (8, 30, 2))
        self.assertEqual(mu.shape, (8, 16))
        self.assertEqual(logvar.shape, (8, 16))

    def test_elbo_loss_gradient_flow(self):
        """Verify ELBO loss computes valid scalar and propagates gradients back to weights."""
        x = torch.randn(4, 30, 2, device=self.device, requires_grad=True)
        recon, mu, logvar = self.model(x)
        loss, mse, kl = vlstm_loss(recon, x, mu, logvar, beta=0.5)

        self.assertGreater(loss.item(), 0.0)
        self.assertGreaterEqual(mse.item(), 0.0)
        self.assertGreaterEqual(kl.item(), 0.0)

        loss.backward()
        for name, param in self.model.named_parameters():
            self.assertIsNotNone(param.grad, f"Gradient missing for {name}")
            self.assertFalse(torch.isnan(param.grad).any(), f"NaN gradient in {name}")

    def test_mc_uncertainty_decomposition(self):
        """Verify MC sampling yields positive aleatoric and epistemic uncertainty scores."""
        x = torch.randn(4, 30, 2, device=self.device)
        aleatoric, epistemic, mean_recon = self.model.compute_uncertainty(x, n_samples=15)

        self.assertEqual(aleatoric.shape, (4,))
        self.assertEqual(epistemic.shape, (4,))
        self.assertEqual(mean_recon.shape, (4, 30, 2))

        self.assertTrue((aleatoric >= 0.0).all())
        self.assertTrue((epistemic >= 0.0).all())


if __name__ == "__main__":
    unittest.main()
