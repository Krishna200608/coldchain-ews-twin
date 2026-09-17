"""
src/split_utils.py
==================
Shared utilities for chronological train/test splitting across models (IF, LSTM, etc.).

STRUCTURAL PROXY NOTICE
-----------------------
Split logic applies to synthetic/proxy IoT telemetry. See docs/AD_LOG.md (D6).
"""

from __future__ import annotations

import logging
import pathlib
import sys
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from config import TRAIN_FRACTION

logger = logging.getLogger(__name__)


def compute_cutoff_ts(df_out: pd.DataFrame, df_in: pd.DataFrame) -> pd.Timestamp:
    """
    Compute cutoff_ts = date_min + TRAIN_FRACTION * (date_max - date_min)
    from the FULL dataset (both series combined), per D6.

    Using the actual loaded data — not hardcoded date strings from M1.
    """
    all_ts   = pd.concat([df_out["ts"], df_in["ts"]])
    date_min = all_ts.min()
    date_max = all_ts.max()
    cutoff   = date_min + TRAIN_FRACTION * (date_max - date_min)
    logger.info(
        "cutoff_ts: date_min=%s  date_max=%s  TRAIN_FRACTION=%.1f  cutoff=%s",
        date_min, date_max, TRAIN_FRACTION, cutoff,
    )
    return cutoff


def split_series(
    df: pd.DataFrame, cutoff_ts: pd.Timestamp, series_name: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (df_train, df_test) with the same cutoff_ts for both series."""
    train = df[df["ts"] < cutoff_ts].copy()
    test  = df[df["ts"] >= cutoff_ts].copy()
    logger.info(
        "Series '%s' split: train=%d rows (ts < %s)  test=%d rows (ts >= %s)",
        series_name, len(train), cutoff_ts, len(test), cutoff_ts,
    )
    return train, test
