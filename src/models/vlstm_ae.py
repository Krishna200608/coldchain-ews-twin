"""
src/models/vlstm_ae.py
======================
Variational LSTM-Autoencoder (VLSTM-AE) with Uncertainty Quantification.
Proposal P1 from docs/RESEARCH_HANDOFF.md.

Architecture:
    Encoder:   LSTM(2 -> 64, batch_first=True)
               fc_mu: Linear(64 -> 16)
               fc_logvar: Linear(64 -> 16)
    Bottleneck: Reparameterization z = mu + eps * exp(0.5 * logvar)
               RepeatVector(16, window_length=30)
    Decoder:   LSTM(16 -> 64, batch_first=True)
               Linear(64 -> 2) applied at each timestep
    Total:     ~45,000 parameters

Loss (ELBO):
    Loss = MSE_recon + beta * KL_divergence
    KL = -0.5 * mean(1 + logvar - mu^2 - exp(logvar))
    KL Annealing: beta = min(1.0, epoch / annealing_epochs)

Uncertainty Quantification (MC Sampling, N=30 passes):
    - Aleatoric Uncertainty: Expected reconstruction MSE (data / measurement noise).
    - Epistemic Uncertainty: Variance of stochastic reconstructions (model ignorance).
    - Confidence Metric: uncertainty_pct = epistemic / (aleatoric + epistemic + eps) * 100.
      < 30%: HIGH CONFIDENCE ALARM
      > 70%: UNCERTAIN — LOW CONFIDENCE / VERIFY MANUALLY

Constraints Obeyed:
    D1: Count-based windowing (30 readings, 2 features: [temp_norm, log_gap_norm]).
    D6: Chronological train/test split.
    D16: Final-timestep causal scoring.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class VLSTMEncoder(nn.Module):
    """
    Variational LSTM Encoder mapping (B, L=30, 2) to latent distribution parameters (mu, logvar).
    """

    def __init__(self, input_size: int = 2, hidden_size: int = 64, latent_dim: int = 16):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc_mu = nn.Linear(hidden_size, latent_dim)
        self.fc_logvar = nn.Linear(hidden_size, latent_dim)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # x: (B, L, input_size)
        _, (h_n, _) = self.lstm(x)
        h = h_n[-1]  # (B, hidden_size)
        mu = self.fc_mu(h)  # (B, latent_dim)
        logvar = self.fc_logvar(h)  # (B, latent_dim)
        return mu, logvar

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        if self.training:
            std = torch.exp(0.5 * logvar)
            eps = torch.randn_like(std)
            return mu + eps * std
        return mu


class VLSTMDecoder(nn.Module):
    """
    LSTM Decoder reconstructing (B, L=30, 2) sequence from sampled latent vector z.
    """

    def __init__(
        self,
        latent_dim: int = 16,
        hidden_size: int = 64,
        output_size: int = 2,
        window_length: int = 30,
    ):
        super().__init__()
        self.window_length = window_length
        self.lstm = nn.LSTM(latent_dim, hidden_size, batch_first=True)
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        # z: (B, latent_dim) -> (B, window_length, latent_dim)
        z_rep = z.unsqueeze(1).repeat(1, self.window_length, 1)
        out, _ = self.lstm(z_rep)
        return self.linear(out)  # (B, window_length, output_size)


class VLSTMAutoencoder(nn.Module):
    """
    Complete Variational LSTM-Autoencoder with Monte Carlo uncertainty estimation.
    """

    def __init__(
        self,
        input_size: int = 2,
        hidden_size: int = 64,
        latent_dim: int = 16,
        window_length: int = 30,
    ):
        super().__init__()
        self.latent_dim = latent_dim
        self.window_length = window_length
        self.encoder = VLSTMEncoder(input_size, hidden_size, latent_dim)
        self.decoder = VLSTMDecoder(latent_dim, hidden_size, input_size, window_length)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, logvar = self.encoder(x)
        z = self.encoder.reparameterize(mu, logvar)
        recon = self.decoder(z)
        return recon, mu, logvar

    def compute_uncertainty(
        self,
        x: torch.Tensor,
        n_samples: int = 30,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Monte Carlo stochastic sampling for epistemic and aleatoric uncertainty decomposition.

        Args:
            x: Input tensor of shape (B, L, 2).
            n_samples: Number of stochastic forward passes (default 30).

        Returns:
            aleatoric: Expected reconstruction MSE at final timestep (B,).
            epistemic: Variance of reconstruction predictions across passes (B,).
            mean_recon: Average reconstructed sequence tensor (B, L, 2).
        """
        was_training = self.training
        self.eval()

        reconstructions = []
        with torch.no_grad():
            mu, logvar = self.encoder(x)
            std = torch.exp(0.5 * logvar)

            for _ in range(n_samples):
                eps = torch.randn_like(std)
                z = mu + eps * std
                recon = self.decoder(z)
                reconstructions.append(recon)

        if was_training:
            self.train()

        stack = torch.stack(reconstructions, dim=0)  # (N, B, L, 2)
        mean_recon = stack.mean(dim=0)  # (B, L, 2)

        # Final timestep evaluation (D16 compliant)
        diff_last = stack[:, :, -1, :] - x.unsqueeze(0)[:, :, -1, :]  # (N, B, 2)
        per_sample_mse = torch.mean(diff_last ** 2, dim=-1)  # (N, B)

        # Aleatoric: expected reconstruction MSE (data / noise floor)
        aleatoric = per_sample_mse.mean(dim=0)  # (B,)

        # Epistemic: variance of predictions (model epistemic uncertainty)
        epistemic = per_sample_mse.var(dim=0) if n_samples > 1 else torch.zeros_like(aleatoric)

        return aleatoric, epistemic, mean_recon


def vlstm_loss(
    recon: torch.Tensor,
    x: torch.Tensor,
    mu: torch.Tensor,
    logvar: torch.Tensor,
    beta: float = 1.0,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Evidence Lower Bound (ELBO) Loss for VLSTM-AE.

    Args:
        recon: Reconstructed sequence (B, L, 2).
        x: Target ground-truth sequence (B, L, 2).
        mu: Latent Gaussian mean (B, latent_dim).
        logvar: Latent Gaussian log-variance (B, latent_dim).
        beta: KL weight hyperparameter (annealed from 0 to 1).

    Returns:
        total_loss, mse_loss, kl_loss
    """
    mse_loss = F.mse_loss(recon, x)
    # Analytical KL divergence: -0.5 * sum(1 + log(sigma^2) - mu^2 - sigma^2)
    kl_loss = -0.5 * torch.mean(1.0 + logvar - mu.pow(2) - logvar.exp())
    total_loss = mse_loss + beta * kl_loss
    return total_loss, mse_loss, kl_loss
