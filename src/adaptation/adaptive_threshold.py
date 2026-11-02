"""
src/adaptation/adaptive_threshold.py
=====================================
Online adaptive anomaly threshold using Kalman Filter + CUSUM control chart.

Mathematical Formulation:
-------------------------
1. Kalman Filter state update:
   - Tracks the running latent mean (mu) of normal anomaly scores.
   - Contamination Guard: Only updates Kalman state when score < adaptive_threshold,
     preventing anomalous excursions from corrupting the baseline.
   - Innovation: y_t = s_t - mu_{t-1}
   - Kalman gain: K_t = P_{t-1} / (P_{t-1} + R)
   - State update: mu_t = mu_{t-1} + K_t * y_t
   - Covariance update: P_t = (1 - K_t) * P_{t-1}
   - Running standard deviation: sigma_t = max(1e-6, 0.99 * sigma_{t-1} + 0.01 * |y_t|)

2. Dynamic Threshold:
   - tau_t = mu_t + k_sigma * sigma_t (where k_sigma defaults to 2.0, matching K_SIGMA)

3. Page's Cumulative Sum (CUSUM) Control Chart:
   - Detects persistent distributional drift before individual point thresholds trip.
   - Slack parameter: k = cusum_slack_factor * init_std
   - Decision interval: h = cusum_decision_factor * init_std
   - Upper sum: C+_t = max(0, C+_{t-1} + s_t - mu_t - k)
   - Lower sum: C-_t = max(0, C-_{t-1} - s_t + mu_t - k)
   - CUSUM alarm: (C+_t > h) or (C-_t > h)

Architectural Constraints Obeyed:
---------------------------------
- D1: No time-grid assumption; operates strictly on sequential count-based events.
- D6: Initialized strictly from training split statistics (no test lookahead leakage).
- D13: Original fixed threshold remains preserved alongside adaptive threshold for benchmark parity.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class AdaptiveThresholdResult:
    """Encapsulates the output of a single online adaptation step."""
    adaptive_threshold: float
    kalman_mean: float
    kalman_std: float
    cusum_plus: float
    cusum_minus: float
    cusum_alarm: bool
    is_stable: bool  # True after at least 30 clean updates have been processed


class KalmanCUSUMAdapter:
    """
    Online adaptive threshold and drift detector for streaming anomaly scores.
    """

    def __init__(
        self,
        init_mean: float,
        init_std: float,
        k_sigma: float = 2.0,
        measurement_noise_R: float = 0.01,
        cusum_slack_factor: float = 0.5,
        cusum_decision_factor: float = 4.0,
    ) -> None:
        self.mu: float = float(init_mean)
        self.sigma: float = max(1e-6, float(init_std))
        self.k_sigma: float = float(k_sigma)
        self.P: float = 1.0  # Kalman error covariance initial estimate
        self.R: float = float(measurement_noise_R)
        self.k: float = float(cusum_slack_factor * self.sigma)
        self.h: float = float(cusum_decision_factor * self.sigma)
        self.C_plus: float = 0.0
        self.C_minus: float = 0.0
        self._n_stable_updates: int = 0

    def update(self, score: float) -> AdaptiveThresholdResult:
        """
        Process a single new anomaly score and update Kalman filter and CUSUM state.
        
        Args:
            score: Raw continuous anomaly score (positive orientation: higher = more anomalous).
            
        Returns:
            AdaptiveThresholdResult containing current dynamic threshold, Kalman stats, and CUSUM state.
        """
        if np.isnan(score) or np.isinf(score):
            return AdaptiveThresholdResult(
                adaptive_threshold=float(self.mu + self.k_sigma * self.sigma),
                kalman_mean=float(self.mu),
                kalman_std=float(self.sigma),
                cusum_plus=float(self.C_plus),
                cusum_minus=float(self.C_minus),
                cusum_alarm=False,
                is_stable=bool(self._n_stable_updates >= 30),
            )

        current_adaptive_thr = self.mu + self.k_sigma * self.sigma

        # Contamination guard: update Kalman filter only on healthy/in-control readings
        if score < current_adaptive_thr:
            K = self.P / (self.P + self.R)
            innovation = score - self.mu
            self.mu = self.mu + K * innovation
            self.sigma = max(1e-6, self.sigma * 0.99 + abs(innovation) * 0.01)
            self.P = (1.0 - K) * self.P
            self._n_stable_updates += 1

        # CUSUM drift detection
        self.C_plus = max(0.0, self.C_plus + score - self.mu - self.k)
        self.C_minus = max(0.0, self.C_minus - score + self.mu - self.k)

        cusum_alarm = bool((self.C_plus > self.h) or (self.C_minus > self.h))
        if cusum_alarm:
            # Reset CUSUM accumulation registers following an alarm
            self.C_plus = 0.0
            self.C_minus = 0.0

        return AdaptiveThresholdResult(
            adaptive_threshold=float(self.mu + self.k_sigma * self.sigma),
            kalman_mean=float(self.mu),
            kalman_std=float(self.sigma),
            cusum_plus=float(self.C_plus),
            cusum_minus=float(self.C_minus),
            cusum_alarm=cusum_alarm,
            is_stable=bool(self._n_stable_updates >= 30),
        )

    def reset(self) -> None:
        """Reset internal accumulator state (preserves initial hyperparameters)."""
        self.P = 1.0
        self.C_plus = 0.0
        self.C_minus = 0.0
        self._n_stable_updates = 0

