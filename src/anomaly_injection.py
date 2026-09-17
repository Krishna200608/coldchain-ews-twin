"""
src/anomaly_injection.py
========================
Injects synthetic anomalies (step, drift, flatline) onto COPIES of the clean
feature DataFrames. The clean reference files are never overwritten.

STRUCTURAL PROXY NOTICE
-----------------------
All injected anomalies are SYNTHETIC PROXY constructs. They are not derived
from real cold-chain spoilage events and make no claims about food safety.
See docs/data_profile.md and D3 in docs/AD_LOG.md.

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D3: Anomalies are additive perturbations on a COPY, with a separate audit log.
    Three types only: step, drift, flatline. Raw/M1/clean feature files are
    never overwritten.

PARAMETERS — ALL ARE NAMED CONSTANTS
-------------------------------------
Every numeric parameter below is explicitly labelled as either:
  (a) an arbitrary documented default (not derived from data or spoilage kinetics), or
  (b) computed from data (none in this file — all are arbitrary defaults).

USAGE
-----
    python src/anomaly_injection.py

Inputs  (must exist):  data/processed/out_features.csv, in_features.csv
Outputs:
    data/processed/out_labeled.csv     — Out series with injected values + labels
    data/processed/in_labeled.csv      — In  series with injected values + labels
    data/processed/injection_log.csv   — one row per injection (audit trail)
"""

from __future__ import annotations

import logging
import pathlib

import numpy as np
import pandas as pd

from config import RANDOM_SEED

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ══ Named constants — all non-RANDOM_SEED values remain local ════════════════════

# Injection counts per series.
# 5 × 3 types × 2 series = 30 total injections.
# Arbitrary documented defaults.
N_STEP_PER_SERIES: int = 5
N_DRIFT_PER_SERIES: int = 5
N_FLATLINE_PER_SERIES: int = 5

# Duration range for all injection types (in readings, not time — D1).
# Arbitrary proxy defaults: not derived from real cold-chain spoilage kinetics.
DUR_MIN: int = 5
DUR_MAX: int = 30

# Step magnitude range (additive, same units as temp — °C proxy).
# Arbitrary proxy default: represents a sensor spike of 5–15 °C above real value.
STEP_MAG_MIN: float = 5.0
STEP_MAG_MAX: float = 15.0

# Drift final magnitude range (additive, same units as temp — °C proxy).
# Arbitrary proxy default: linear runaway drift ending 5–20 °C above real value.
DRIFT_FINAL_MAG_MIN: float = 5.0
DRIFT_FINAL_MAG_MAX: float = 20.0

# MIN_START_IDX: minimum positional index for injection start.
# Ensures rolling features (window=ROLLING_WINDOW from preprocessing) are stable
# and flatline always has a valid preceding reading (start-1 ≥ 0).
# Arbitrary safety margin; not a tuned parameter.
MIN_START_IDX: int = 15

# MIN_GAP_BETWEEN_INJECTIONS: buffer (readings) required between injection windows.
# Prevents flatline from inadvertently freezing a value that is itself injected.
# Arbitrary documented default.
MIN_GAP_BETWEEN_INJECTIONS: int = 5

# MAX_RESAMPLE_ATTEMPTS: max tries to find a non-overlapping start index.
MAX_RESAMPLE_ATTEMPTS: int = 500

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
OUT_FEATURES_CSV  = PROCESSED_DIR / "out_features.csv"
IN_FEATURES_CSV   = PROCESSED_DIR / "in_features.csv"
OUT_LABELED_CSV   = PROCESSED_DIR / "out_labeled.csv"
IN_LABELED_CSV    = PROCESSED_DIR / "in_labeled.csv"
INJECTION_LOG_CSV = PROCESSED_DIR / "injection_log.csv"


# ══ Injection functions ════════════════════════════════════════════════════════
# Each function:
#   - takes a COPY of temp values and a timestamps Series
#   - returns a modified copy of temp values + a record dict
#   - NEVER modifies the input array in-place

def inject_step(
    temp_arr: np.ndarray,
    timestamps: pd.Series,
    start_idx: int,
    duration: int,
    magnitude: float,
) -> tuple[np.ndarray, dict]:
    """
    Step (spike) injection: add 'magnitude' to 'duration' consecutive readings
    starting at start_idx. Values revert to original after the window ends.

    This represents a sudden, sustained sensor offset (e.g., brief heat exposure).
    The spike magnitude is an ARBITRARY PROXY DEFAULT (STEP_MAG_MIN to STEP_MAG_MAX).

    Parameters
    ----------
    temp_arr  : 1-D numpy array of temperature values (will not be mutated)
    timestamps: aligned pd.Series of timestamps (for record metadata)
    start_idx : positional start of the injection window
    duration  : number of readings to perturb
    magnitude : degrees to add (positive → temperature spike)

    Returns
    -------
    arr    : modified copy of temp_arr
    record : dict with injection metadata
    """
    arr = temp_arr.copy()
    end_idx = min(start_idx + duration, len(arr))
    actual_duration = end_idx - start_idx
    arr[start_idx:end_idx] = arr[start_idx:end_idx] + magnitude

    return arr, {
        "type": "step",
        "start_idx": start_idx,
        "end_idx": end_idx - 1,
        "start_timestamp": timestamps.iloc[start_idx],
        "duration": actual_duration,
        "magnitude": magnitude,
        "final_magnitude": magnitude,  # constant throughout window
    }


def inject_drift(
    temp_arr: np.ndarray,
    timestamps: pd.Series,
    start_idx: int,
    duration: int,
    final_magnitude: float,
) -> tuple[np.ndarray, dict]:
    """
    Drift injection: linear ramp from +0 at start_idx to +final_magnitude at
    start_idx + duration - 1. Models a gradual sensor runaway or cold-chain breach.

    The ramp magnitude is an ARBITRARY PROXY DEFAULT
    (DRIFT_FINAL_MAG_MIN to DRIFT_FINAL_MAG_MAX).

    Parameters
    ----------
    final_magnitude : total additive offset at the end of the ramp
    """
    arr = temp_arr.copy()
    end_idx = min(start_idx + duration, len(arr))
    actual_duration = end_idx - start_idx
    ramp = np.linspace(0.0, final_magnitude, actual_duration)
    arr[start_idx:end_idx] = arr[start_idx:end_idx] + ramp

    return arr, {
        "type": "drift",
        "start_idx": start_idx,
        "end_idx": end_idx - 1,
        "start_timestamp": timestamps.iloc[start_idx],
        "duration": actual_duration,
        "magnitude": 0.0,            # starting additive offset
        "final_magnitude": final_magnitude,
    }


def inject_flatline(
    temp_arr: np.ndarray,
    timestamps: pd.Series,
    start_idx: int,
    duration: int,
) -> tuple[np.ndarray, dict]:
    """
    Flatline injection: freeze the temperature at the real value immediately
    preceding start_idx (i.e., the last un-injected value before onset).
    Models a stuck/failed sensor that stops reporting new readings.

    No magnitude parameter — the frozen value is whatever the sensor last reported.
    This anomaly type will NOT trigger a threshold-based alarm if the frozen value
    is below the alarm threshold (an expected, informative edge case; see
    baseline_and_labels.py and notebook §5).

    Requires start_idx >= 1 (guaranteed by MIN_START_IDX constant).
    """
    if start_idx < 1:
        raise ValueError(f"inject_flatline requires start_idx >= 1, got {start_idx}")
    arr = temp_arr.copy()
    frozen_value = float(arr[start_idx - 1])  # "last real value" before onset
    end_idx = min(start_idx + duration, len(arr))
    actual_duration = end_idx - start_idx
    arr[start_idx:end_idx] = frozen_value

    return arr, {
        "type": "flatline",
        "start_idx": start_idx,
        "end_idx": end_idx - 1,
        "start_timestamp": timestamps.iloc[start_idx],
        "duration": actual_duration,
        "magnitude": float("nan"),        # not applicable
        "final_magnitude": float("nan"),  # not applicable
        "frozen_at": frozen_value,        # informational
    }


# ══ Overlap guard ══════════════════════════════════════════════════════════════

def _sample_non_overlapping_start(
    rng: np.random.Generator,
    series_len: int,
    duration: int,
    occupied: set[int],
    is_flatline: bool = False,
) -> int:
    """
    Sample a start_idx such that the injection window [start, start+duration)
    plus a MIN_GAP_BETWEEN_INJECTIONS buffer on each side does not intersect
    any index in 'occupied'.

    For flatline injections, also checks that start-1 is not occupied
    (to protect the "frozen at" value from being itself injected).

    Raises RuntimeError if MAX_RESAMPLE_ATTEMPTS is exceeded.
    """
    # Valid start range: MIN_START_IDX to (series_len - duration - MIN_GAP - 1)
    lo = MIN_START_IDX
    hi = series_len - duration - MIN_GAP_BETWEEN_INJECTIONS - 1

    if hi <= lo:
        raise ValueError(
            f"Series too short (len={series_len}) for injection of duration={duration}."
        )

    for attempt in range(MAX_RESAMPLE_ATTEMPTS):
        start = int(rng.integers(lo, hi))
        end = start + duration

        # Buffered window to check for conflicts
        check_lo = max(0, start - MIN_GAP_BETWEEN_INJECTIONS)
        check_hi = min(series_len, end + MIN_GAP_BETWEEN_INJECTIONS)
        check_set = set(range(check_lo, check_hi))

        # For flatline: also check start-1 (the frozen-at source value)
        if is_flatline:
            check_set.add(max(0, start - 1))

        if not check_set.intersection(occupied):
            # Mark this window (with buffer) as occupied
            occupied.update(range(check_lo, check_hi))
            return start

    raise RuntimeError(
        f"Could not find non-overlapping injection start after "
        f"{MAX_RESAMPLE_ATTEMPTS} attempts (series_len={series_len}, "
        f"duration={duration})."
    )


# ══ Per-series injection driver ════════════════════════════════════════════════

def inject_series(
    df_clean: pd.DataFrame,
    series_name: str,
    rng: np.random.Generator,
    injection_id_offset: int = 0,
) -> tuple[pd.DataFrame, list[dict]]:
    """
    Apply N_STEP + N_DRIFT + N_FLATLINE injections to a copy of df_clean.

    The original df_clean is NOT modified.

    Parameters
    ----------
    df_clean          : clean feature DataFrame for one series (Out or In)
    series_name       : 'Out' or 'In' (for logging and record)
    rng               : seeded numpy Generator
    injection_id_offset: integer offset for injection IDs

    Returns
    -------
    df_labeled : copy of df_clean with added columns:
                   temp_injected, is_injected_anomaly, injection_type
    records    : list of record dicts (one per injection)
    """
    df = df_clean.copy()
    df["temp_injected"]      = df["temp"].astype(float)
    df["is_injected_anomaly"] = False
    df["injection_type"]     = None

    temp_arr   = df["temp_injected"].values
    timestamps = df["ts"].reset_index(drop=True)
    series_len = len(df)

    occupied: set[int] = set()
    records: list[dict] = []
    injection_id = injection_id_offset

    def _apply(arr: np.ndarray, record: dict, inj_type: str) -> np.ndarray:
        """Write results back into df columns and records list."""
        nonlocal injection_id
        s  = record["start_idx"]
        e  = record["end_idx"] + 1   # slice end (exclusive)
        df.iloc[s:e, df.columns.get_loc("temp_injected")]       = arr[s:e]
        df.iloc[s:e, df.columns.get_loc("is_injected_anomaly")] = True
        df.iloc[s:e, df.columns.get_loc("injection_type")]      = inj_type
        records.append({
            "injection_id":    f"{series_name.lower()}_{inj_type}_{injection_id:03d}",
            "series":          series_name,
            **record,
            "seed":            RANDOM_SEED,
        })
        injection_id += 1
        return arr

    # ── Step injections ───────────────────────────────────────────────────────
    for _ in range(N_STEP_PER_SERIES):
        dur = int(rng.integers(DUR_MIN, DUR_MAX + 1))
        mag = float(rng.uniform(STEP_MAG_MIN, STEP_MAG_MAX))
        start = _sample_non_overlapping_start(rng, series_len, dur, occupied)
        arr, record = inject_step(temp_arr, timestamps, start, dur, mag)
        temp_arr = _apply(arr, record, "step")
        logger.info(
            "  [%s] step   start=%d  dur=%d  mag=%.2f",
            series_name, start, dur, mag,
        )

    # ── Drift injections ──────────────────────────────────────────────────────
    for _ in range(N_DRIFT_PER_SERIES):
        dur = int(rng.integers(DUR_MIN, DUR_MAX + 1))
        final_mag = float(rng.uniform(DRIFT_FINAL_MAG_MIN, DRIFT_FINAL_MAG_MAX))
        start = _sample_non_overlapping_start(rng, series_len, dur, occupied)
        arr, record = inject_drift(temp_arr, timestamps, start, dur, final_mag)
        temp_arr = _apply(arr, record, "drift")
        logger.info(
            "  [%s] drift  start=%d  dur=%d  final_mag=%.2f",
            series_name, start, dur, final_mag,
        )

    # ── Flatline injections ───────────────────────────────────────────────────
    for _ in range(N_FLATLINE_PER_SERIES):
        dur = int(rng.integers(DUR_MIN, DUR_MAX + 1))
        start = _sample_non_overlapping_start(
            rng, series_len, dur, occupied, is_flatline=True
        )
        arr, record = inject_flatline(temp_arr, timestamps, start, dur)
        temp_arr = _apply(arr, record, "flatline")
        logger.info(
            "  [%s] flatline start=%d  dur=%d  frozen_at=%.1f",
            series_name, start, dur, record["frozen_at"],
        )

    total = N_STEP_PER_SERIES + N_DRIFT_PER_SERIES + N_FLATLINE_PER_SERIES
    n_injected_rows = int(df["is_injected_anomaly"].sum())
    logger.info(
        "Series '%s': %d injections applied | %d rows labeled is_injected_anomaly=True",
        series_name, total, n_injected_rows,
    )

    return df, records


# ══ Main ═══════════════════════════════════════════════════════════════════════

def main() -> None:
    logger.info("=== Cold Chain EWS — Anomaly Injection (Milestone 2) ===")
    logger.info(
        "PROXY NOTICE: All injected anomalies are SYNTHETIC constructs on a "
        "proxy dataset. Not real cold-chain disruptions. See D3 in AD_LOG.md."
    )

    # ── Load CLEAN feature files (must not contain is_injected_anomaly column) ─
    logger.info("Loading clean feature files …")
    df_out_clean = pd.read_csv(OUT_FEATURES_CSV, parse_dates=["ts"])
    df_in_clean  = pd.read_csv(IN_FEATURES_CSV,  parse_dates=["ts"])

    # Safety assertion: these files must be untouched by injection
    assert "is_injected_anomaly" not in df_out_clean.columns, \
        "out_features.csv already has is_injected_anomaly — injection contamination!"
    assert "is_injected_anomaly" not in df_in_clean.columns, \
        "in_features.csv already has is_injected_anomaly — injection contamination!"
    logger.info("Assertion passed: clean feature files contain no injected labels.")

    # ── Seeded RNG (D3: reproducibility) ──────────────────────────────────────
    rng = np.random.default_rng(RANDOM_SEED)
    logger.info("RNG seeded with RANDOM_SEED=%d (arbitrary reproducibility choice)", RANDOM_SEED)

    total_injections = (N_STEP_PER_SERIES + N_DRIFT_PER_SERIES + N_FLATLINE_PER_SERIES) * 2
    logger.info(
        "Injection config: %d step + %d drift + %d flatline per series × 2 series = %d total",
        N_STEP_PER_SERIES, N_DRIFT_PER_SERIES, N_FLATLINE_PER_SERIES, total_injections,
    )
    logger.info(
        "Ranges — duration: %d–%d readings | step mag: %.1f–%.1f | drift final_mag: %.1f–%.1f",
        DUR_MIN, DUR_MAX, STEP_MAG_MIN, STEP_MAG_MAX, DRIFT_FINAL_MAG_MIN, DRIFT_FINAL_MAG_MAX,
    )
    logger.info("(All ranges are ARBITRARY PROXY DEFAULTS — not derived from cold-chain data)")

    # ── Inject per series ──────────────────────────────────────────────────────
    logger.info("Injecting into Out series …")
    df_out_labeled, records_out = inject_series(df_out_clean, "Out", rng, injection_id_offset=0)

    logger.info("Injecting into In series …")
    df_in_labeled,  records_in  = inject_series(df_in_clean,  "In",  rng, injection_id_offset=15)

    all_records = records_out + records_in
    logger.info("Total injections: %d (expected 30)", len(all_records))

    # ── Build injection log ────────────────────────────────────────────────────
    log_rows = []
    for r in all_records:
        log_rows.append({
            "injection_id":      r["injection_id"],
            "series":            r["series"],
            "type":              r["type"],
            "start_idx":         r["start_idx"],
            "end_idx":           r["end_idx"],
            "start_timestamp":   r["start_timestamp"],
            "duration":          r["duration"],
            "magnitude":         r.get("magnitude", float("nan")),
            "final_magnitude":   r.get("final_magnitude", float("nan")),
            "frozen_at":         r.get("frozen_at", float("nan")),
            "seed":              r["seed"],
        })
    injection_log = pd.DataFrame(log_rows)

    # ── Save outputs ───────────────────────────────────────────────────────────
    df_out_labeled.to_csv(OUT_LABELED_CSV,   index=False)
    df_in_labeled.to_csv(IN_LABELED_CSV,     index=False)
    injection_log.to_csv(INJECTION_LOG_CSV,  index=False)

    logger.info("Saved: %s (%d rows)", OUT_LABELED_CSV.name,   len(df_out_labeled))
    logger.info("Saved: %s (%d rows)", IN_LABELED_CSV.name,    len(df_in_labeled))
    logger.info("Saved: %s (%d rows)", INJECTION_LOG_CSV.name, len(injection_log))

    # ── Confirm no overlap ────────────────────────────────────────────────────
    for series_name, df_lbl in [("Out", df_out_labeled), ("In", df_in_labeled)]:
        labeled_rows = df_lbl[df_lbl["is_injected_anomaly"]].index.tolist()
        assert len(labeled_rows) == len(set(labeled_rows)), \
            f"Overlap detected in {series_name} series — duplicate row indices labeled!"
    logger.info("Overlap check passed: no row is labeled by two injections.")

    logger.info("=== Anomaly injection complete ===")
    print("\nInjection log:")
    print(injection_log[["injection_id","series","type","start_idx","duration","magnitude","final_magnitude","frozen_at"]].to_string(index=False))


if __name__ == "__main__":
    main()
