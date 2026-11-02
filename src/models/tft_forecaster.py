"""
src/models/tft_forecaster.py
============================
Multi-Horizon Quantile Temporal Forecaster (Proposal P3).
Predicts future temperature trajectories N-steps-ahead under irregular IoT sampling.

Key Architecture:
- Input: 30 past readings x 4 normalized features:
  [temp_norm, log_gap_norm, rolling_std_norm, rolling_delta_norm]
- Encoder: Bidirectional/temporal GRU/LSTM with multi-head self-attention
- Decoder: Multi-horizon projection producing quantiles (q=0.1, 0.5, 0.9)
  across a 10-step lookahead horizon (H=10, Q=3).
- Loss: Pinball (Quantile) loss across all horizons and quantiles.

Alarm Condition:
If forecasted upper quantile (q=0.9) or median breaches threshold within the
next 10 future steps, a pre-emptive alarm fires BEFORE the physical excursion occurs.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class TemporalQuantileForecaster(nn.Module):
    """
    Multi-horizon temporal forecaster predicting future quantile trajectories.
    """

    def __init__(
        self,
        input_dim: int = 4,
        hidden_dim: int = 64,
        horizon: int = 10,
        quantiles: list[float] | None = None,
        num_layers: int = 2,
    ):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.horizon = horizon
        self.quantiles = quantiles or [0.1, 0.5, 0.9]
        self.num_quantiles = len(self.quantiles)

        # Sequence encoder with temporal GRU
        self.encoder = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=0.1 if num_layers > 1 else 0.0,
        )

        # Multi-head attention across sequence timesteps
        self.attention = nn.MultiheadAttention(
            embed_dim=hidden_dim,
            num_heads=4,
            batch_first=True,
        )

        # Temporal horizon expansion and quantile projection
        self.fc_context = nn.Linear(hidden_dim, hidden_dim)
        self.fc_horizon = nn.Linear(hidden_dim, horizon * hidden_dim // 2)
        self.fc_head = nn.Sequential(
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, self.num_quantiles),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Input tensor of shape (B, L, input_dim) where L=30.
        Returns:
            quantiles: (B, horizon, num_quantiles) representing
                       predictions for each lookahead step at [q_0.1, q_0.5, q_0.9].
        """
        B, L, _ = x.shape
        gru_out, _ = self.encoder(x)  # (B, L, hidden_dim)

        # Temporal self-attention
        attn_out, _ = self.attention(gru_out, gru_out, gru_out)  # (B, L, hidden_dim)
        context = F.relu(self.fc_context(attn_out[:, -1, :]))    # (B, hidden_dim)

        # Expand to future horizon
        h_expanded = self.fc_horizon(context).view(B, self.horizon, self.hidden_dim // 2)  # (B, H, hidden//2)
        preds = self.fc_head(h_expanded)  # (B, H, num_quantiles)

        return preds


def pinball_loss(
    y_true: torch.Tensor,
    y_pred: torch.Tensor,
    quantiles: list[float] | None = None,
) -> torch.Tensor:
    """
    Multi-quantile Pinball Loss across all future forecast horizons.
    Args:
        y_true: Ground-truth target trajectory (B, horizon).
        y_pred: Predicted quantiles (B, horizon, num_quantiles).
        quantiles: List of quantile levels (e.g. [0.1, 0.5, 0.9]).
    Returns:
        Scalar loss.
    """
    if quantiles is None:
        quantiles = [0.1, 0.5, 0.9]

    total_loss = 0.0
    for i, q in enumerate(quantiles):
        err = y_true - y_pred[:, :, i]
        loss_q = torch.max((q - 1.0) * err, q * err)
        total_loss += loss_q.mean()

    return total_loss / len(quantiles)

