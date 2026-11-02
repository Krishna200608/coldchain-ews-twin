"""
tests/test_adaptive_threshold.py
================================
Unit tests for online Kalman + CUSUM adaptive thresholding (Proposal P4).
"""

import unittest
import numpy as np
from src.adaptation.adaptive_threshold import KalmanCUSUMAdapter, AdaptiveThresholdResult


class TestKalmanCUSUMAdapter(unittest.TestCase):
    def setUp(self):
        self.init_mean = 0.5
        self.init_std = 0.1
        self.k_sigma = 2.0
        self.adapter = KalmanCUSUMAdapter(
            init_mean=self.init_mean,
            init_std=self.init_std,
            k_sigma=self.k_sigma,
            measurement_noise_R=0.01,
            cusum_slack_factor=0.5,
            cusum_decision_factor=4.0,
        )

    def test_initial_state(self):
        """Verify initial threshold equals init_mean + k_sigma * init_std."""
        expected_thr = self.init_mean + self.k_sigma * self.init_std
        self.assertAlmostEqual(self.adapter.mu, self.init_mean)
        self.assertAlmostEqual(self.adapter.sigma, self.init_std)
        self.assertAlmostEqual(self.adapter.k, 0.5 * self.init_std)
        self.assertAlmostEqual(self.adapter.h, 4.0 * self.init_std)

    def test_in_control_adaptation_and_stability(self):
        """Verify Kalman adapts to normal fluctuations and marks is_stable after 30 readings."""
        np.random.seed(42)
        normal_scores = np.random.normal(loc=0.5, scale=0.05, size=50)

        for i, score in enumerate(normal_scores):
            res = self.adapter.update(score)
            self.assertIsInstance(res, AdaptiveThresholdResult)
            self.assertFalse(res.cusum_alarm)
            if i + 1 < 30:
                self.assertFalse(res.is_stable)
            else:
                self.assertTrue(res.is_stable)

        # Kalman mean should stay close to empirical mean 0.5
        self.assertAlmostEqual(self.adapter.mu, 0.5, delta=0.05)
        # Covariance P should decrease with observations
        self.assertLess(self.adapter.P, 1.0)

    def test_contamination_guard(self):
        """Verify outlier scores (> threshold) do NOT corrupt the Kalman state."""
        # Warm up with some normal points
        for _ in range(10):
            self.adapter.update(0.5)

        mu_before = self.adapter.mu
        sigma_before = self.adapter.sigma
        stable_count_before = self.adapter._n_stable_updates

        # Inject extreme outlier
        outlier_score = 100.0
        res = self.adapter.update(outlier_score)

        # Contamination guard should have prevented mu and sigma update
        self.assertEqual(self.adapter.mu, mu_before)
        self.assertEqual(self.adapter.sigma, sigma_before)
        self.assertEqual(self.adapter._n_stable_updates, stable_count_before)

    def test_cusum_drift_detection(self):
        """Verify persistent drift triggers CUSUM alarm."""
        # Feed high scores repeatedly to drive CUSUM accumulation
        drift_score = 0.8  # Well above mean 0.5
        alarm_triggered = False

        for _ in range(30):
            res = self.adapter.update(drift_score)
            if res.cusum_alarm:
                alarm_triggered = True
                break

        self.assertTrue(alarm_triggered, "CUSUM should trigger alarm on sustained upward drift")

    def test_nan_and_inf_handling(self):
        """Verify NaN or inf scores do not crash and preserve state."""
        mu_before = self.adapter.mu
        res_nan = self.adapter.update(float("nan"))
        self.assertFalse(res_nan.cusum_alarm)
        self.assertEqual(self.adapter.mu, mu_before)

        res_inf = self.adapter.update(float("inf"))
        self.assertFalse(res_inf.cusum_alarm)
        self.assertEqual(self.adapter.mu, mu_before)


if __name__ == "__main__":
    unittest.main()

