"""
src/models/pilstm_ae.py
=======================
Physics-Informed LSTM-Autoencoder (PILSTM-AE) for cold-chain early warning anomaly detection.
Proposal P2 from docs/RESEARCH_HANDOFF.md.

Architecture:
    Encoder:   LSTM(2 -> 32, batch_first=True)
    Bottleneck: RepeatVector(hidden_dim, window_length=30)
    Decoder:   LSTM(32 -> 32, batch_first=True)
    Output:    Linear(32 -> 2) applied at each timestep
    Total:     ~13,000 parameters (matching Keras baseline capacity)

Thermodynamic Regularization:
    Loss = MSE_recon + lambda_physics * || dT_pred/dt - (-k * (T - T_amb)) ||^2
    Where Newton's Law of Cooling governs heat transfer across thermal boundaries.
    Enforces physically plausible cooling trajectories and discriminates electrical
    sensor spikes from genuine excursions.

Constraints Obeyed:
    D1: Count-based windowing (30 readings, 2 features: [temp_norm, log_gap_norm]).
    D6: Ambient temperature and cooling constants fitted strictly on train split.
    D16: Final-timestep scoring for causal real-time monitoring.
"""

from __future__ import annotations

import pathlib
from typing import Any
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F


class PILSTMAEEncoder(nn.Module):
    """
    Sequence encoder mapping (batch, seq_len=30, input_dim=2) to latent bottleneck (batch, hidden_dim=32).
    """

    def __init__(self, input_size: int = 2, hidden_size: int = 32):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (B, L, 2)
        _, (h_n, _) = self.lstm(x)
        return h_n[-1]  # (B, hidden_size)


class PILSTMAEDecoder(nn.Module):
    """
    Sequence decoder mapping latent bottleneck vector (batch, hidden_dim=32)
    back to reconstructed trajectory (batch, seq_len=30, output_dim=2).
    """

    def __init__(self, hidden_size: int = 32, output_size: int = 2, window_length: int = 30):
        super().__init__()
        self.window_length = window_length
        self.lstm = nn.LSTM(hidden_size, hidden_size, batch_first=True)
        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        # z: (B, hidden_size)
        # RepeatVector equivalent: (B, 1, hidden_size) -> (B, window_length, hidden_size)
        z_rep = z.unsqueeze(1).repeat(1, self.window_length, 1)
        out, _ = self.lstm(z_rep)
        return self.linear(out)  # (B, window_length, output_size)


class PILSTMAutoencoder(nn.Module):
    """
    Complete Physics-Informed LSTM-Autoencoder.
    """

    def __init__(self, input_size: int = 2, hidden_size: int = 32, window_length: int = 30):
        super().__init__()
        self.encoder = PILSTMAEEncoder(input_size, hidden_size)
        self.decoder = PILSTMAEDecoder(hidden_size, input_size, window_length)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.encoder(x)
        return self.decoder(z)


def physics_informed_loss(
    x_norm: torch.Tensor,
    x_hat_norm: torch.Tensor,
    t_mean: float,
    t_std: float,
    g_mean: float,
    g_std: float,
    k_cooling: float,
    T_amb: float,
    lambda_physics: float = 0.1,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """
    Combined MSE reconstruction loss and Newton's Law of Cooling thermodynamic residual.

    Args:
        x_norm: Ground-truth normalized input tensor of shape (B, L, 2).
        x_hat_norm: Reconstructed normalized tensor of shape (B, L, 2).
        t_mean, t_std: Normalization stats for temp_injected.
        g_mean, g_std: Normalization stats for log_gap_seconds.
        k_cooling: Train-calibrated cooling rate constant (s^-1).
        T_amb: Train-calibrated baseline ambient temperature (°C).
        lambda_physics: Weight hyperparameter for thermodynamic loss penalty.

    Returns:
        total_loss, mse_loss, physics_residual
    """
    mse_loss = F.mse_loss(x_hat_norm, x_norm)

    # Denormalize temperature and gap_seconds for physical rate computation
    # Temperature: T = z * std + mean
    T_act = x_norm[:, :, 0] * t_std + t_mean
    T_hat = x_hat_norm[:, :, 0] * t_std + t_mean

    # Gap seconds: log_gap = z * std + mean => gap = exp(log_gap) - 1
    log_gap = x_norm[:, :, 1] * g_std + g_mean
    gap = torch.exp(log_gap) - 1.0

    # Numerical stabilization: clamp minimum gap to 1.0s to avoid singularity on same-second timestamps
    gap_clamped = torch.clamp(gap[:, 1:], min=1.0)

    # Predicted rate of change from decoder reconstruction: dT_pred / dt (°C/s)
    dT_pred = (T_hat[:, 1:] - T_hat[:, :-1]) / gap_clamped

    # Physically expected rate from Newton's Law of Cooling: dT_physics / dt = -k * (T - T_amb)
    dT_physics = -k_cooling * (T_act[:, :-1] - T_amb)

    # Clamp extreme derivatives to prevent outlier gradient explosions
    dT_pred_clamped = torch.clamp(dT_pred, min=-5.0, max=5.0)
    dT_physics_clamped = torch.clamp(dT_physics, min=-5.0, max=5.0)

    physics_residual = F.mse_loss(dT_pred_clamped, dT_physics_clamped)
    total_loss = mse_loss + lambda_physics * physics_residual

    return total_loss, mse_loss, physics_residual


def fit_physics_parameters(
    df: pd.DataFrame,
    cutoff_ts: str = "2018-10-29 11:10:48",
) -> dict[str, float]:
    """
    Fit Newton's Law of Cooling parameters (k_cooling, T_amb, sigma_delta)
    strictly from uncorrupted training partition data (D6 compliant).

    Args:
        df: Labeled DataFrame containing ['ts', 'temp_injected', 'gap_seconds', 'is_injected_anomaly'].
        cutoff_ts: Chronological train/test split cutoff timestamp.

    Returns:
        Dict with keys: {'T_amb', 'k_cooling', 'sigma_delta', 'dt_min', 'dt_max'}.
    """
    cutoff = pd.Timestamp(cutoff_ts)
    train_mask = (df["ts"] < cutoff) & (df["is_injected_anomaly"] == False)
    train_df = (
        df[train_mask]
        .dropna(subset=["gap_seconds", "temp_injected"])
        .sort_values(["ts", "gap_seconds"])
        .reset_index(drop=True)
    )

    T = train_df["temp_injected"].values.astype(np.float64)
    gaps = train_df["gap_seconds"].values.astype(np.float64)

    dT = np.diff(T)
    dt = gaps[1:]

    # Filter positive gaps to estimate dT/dt
    valid = dt > 0.0
    dT_valid = dT[valid]
    dt_valid = dt[valid]
    T_valid = T[:-1][valid]

    rates = dT_valid / dt_valid

    # Robust percentile filtering (1% to 99%) to exclude sensor recording anomalies
    p1, p99 = np.percentile(rates, [1.0, 99.0])
    robust_mask = (rates >= p1) & (rates <= p99)

    rates_rob = rates[robust_mask]
    T_rob = T_valid[robust_mask]

    T_amb = float(np.median(T))

    # Newton cooling: rate = -k * (T - T_amb) => k = - sum(rate * (T - T_amb)) / sum((T - T_amb)^2)
    diff_T = T_rob - T_amb
    denom = float(np.sum(diff_T ** 2))
    if denom > 1e-6:
        k_est = float(-np.sum(rates_rob * diff_T) / denom)
    else:
        k_est = 0.0001

    k_cooling = float(max(1e-6, k_est))
    sigma_delta = float(np.std(rates_rob))

    return {
        "T_amb": T_amb,
        "k_cooling": k_cooling,
        "sigma_delta": sigma_delta,
        "spike_rate_threshold": 3.0 * sigma_delta,
    }

