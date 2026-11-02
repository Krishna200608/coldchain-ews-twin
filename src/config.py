"""
src/config.py
=============
Single source of truth for all named constants shared across the Cold Chain
EWS Digital Twin project.

STRUCTURAL PROXY NOTICE
-----------------------
All constants here are ARBITRARY DOCUMENTED DEFAULTS unless explicitly noted
as "computed from data." None are derived from real cold-chain data or
food-safety regulatory standards. See docs/AD_LOG.md for rationale.

Imports
-------
Every other src/ module should import from here instead of defining locally:

    from config import ROLLING_WINDOW, RANDOM_SEED   # etc.

Constants are grouped by the milestone that introduced them.
"""

from __future__ import annotations

# ══ Milestone 2 constants ══════════════════════════════════════════════════════

# ROLLING_WINDOW: count of consecutive real readings for rolling mean/std.
# Arbitrary documented default (D1). Count-based, NOT a time span — see D1.
ROLLING_WINDOW: int = 10

# MAX_MATCH_MINUTES: maximum time gap (minutes) for in_out_diff cross-series matching.
# Readings whose nearest cross-series match exceeds this cap receive NaN.
# Arbitrary documented default; not derived from data.
MAX_MATCH_MINUTES: int = 15

# RANDOM_SEED: shared seed for all reproducible random operations (injection, IF).
# Arbitrary documented default — changing this produces a different but equally
# valid result set.
RANDOM_SEED: int = 42

# K_SIGMA: standard deviations above the mean for the naive baseline alarm threshold.
# Conventional heuristic (Chebyshev / 2-sigma). Not a regulatory cold-chain limit.
K_SIGMA: float = 2.0

# D_IRREV_MINUTES: sustained threshold-exceedance duration for "irreversibility".
# Arbitrary documented default. NOT derived from real spoilage-kinetics data.
# No such source exists for this proxy dataset. See D4 in docs/AD_LOG.md.
D_IRREV_MINUTES: float = 10.0

# SEARCH_HORIZON_MINUTES: time past injection_end_ts to search for alarm/irrev.
# Search window = [onset_ts, injection_end_ts + SEARCH_HORIZON_MINUTES].
# Arbitrary documented default — sized to let D_IRREV_MINUTES criterion resolve
# shortly after a short-lived injection ends, without reaching unrelated future
# real data. Not derived from cold-chain data. See D4 fix note in docs/AD_LOG.md.
SEARCH_HORIZON_MINUTES: float = 60.0

# ══ Milestone 3 constants ══════════════════════════════════════════════════════

# TRAIN_FRACTION: proportion of the full time range used for training.
# Chronological split: cutoff_ts = date_min + TRAIN_FRACTION * (date_max - date_min).
# Arbitrary documented default (D6). Not tuned.
TRAIN_FRACTION: float = 0.7

# IF_RANDOM_STATE: random_state for sklearn IsolationForest.
# Set to RANDOM_SEED value for consistency; documented separately so the
# model's own seed is distinct from the injection seed conceptually.
# Arbitrary documented default (D7).
IF_RANDOM_STATE: int = 42

# ══ Milestone 4 constants ══════════════════════════════════════════════════════

# LSTM_WINDOW_LENGTH: count of consecutive real readings per input window for LSTM.
# Count-based windowing (D9 per D1). Arbitrary documented default.
LSTM_WINDOW_LENGTH: int = 30

# LSTM_WINDOW_STRIDE: step size (count of readings) between consecutive window starts.
# Subsampling/stride heuristic (D9). Arbitrary documented default.
LSTM_WINDOW_STRIDE: int = 5

# LSTM_VAL_FRACTION: proportion of the train period carved from its tail for validation.
# Chronological train/val split (D11). Arbitrary documented default.
LSTM_VAL_FRACTION: float = 0.1

# ══ Milestone 5 constants ══════════════════════════════════════════════════════

# TRANSIT_LATENCY_SECONDS: simulated end-to-end transmission/processing delay
# between the Source (sensor reading generation) and Destination (monitoring)
# stages of the SimPy digital twin replay pipeline.
#
# Set to 0.0 (DISABLED) by default so that sim_time_received exactly mirrors
# the cumulative real inter-arrival gaps, enabling exact row-by-row cross-check
# against batch M3/M4b results in Milestone 5b. Any nonzero value shifts all
# alarm timestamps and must be documented as a new AD_LOG decision before use.
# (D19 — see docs/AD_LOG.md).
TRANSIT_LATENCY_SECONDS: float = 0.0

# ══ Research Milestone Constants (P1–P5) ════════════════════════════════════════

# P4: Online Kalman + CUSUM Adaptive Threshold
KALMAN_R: float = 0.01
CUSUM_SLACK_FACTOR: float = 0.5
CUSUM_DECISION_FACTOR: float = 4.0

# Verified LSTM fixed threshold references (D13)
LSTM_THRESH_OUT: float = 1.010091
LSTM_THRESH_IN: float = 1.512753

# Initial score distribution stats for P4 Kalman adapters (train split causal)
IF_TRAIN_MU_OUT: float = -0.059340
IF_TRAIN_STD_OUT: float = 0.064521
IF_TRAIN_MU_IN: float = -0.081425
IF_TRAIN_STD_IN: float = 0.060547

LSTM_TRAIN_MU_OUT: float = 0.139011
LSTM_TRAIN_STD_OUT: float = 0.436083
LSTM_TRAIN_MU_IN: float = 0.270077
LSTM_TRAIN_STD_IN: float = 0.627397

# P2: Physics-Informed LSTM-AE
PHYSICS_LAMBDA: float = 0.1

# P1: Variational LSTM-AE
VLSTM_LATENT_DIM: int = 16
VLSTM_HIDDEN_SIZE: int = 32
MC_SAMPLES: int = 20
