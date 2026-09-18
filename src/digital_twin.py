"""
src/digital_twin.py
===================
SimPy-based digital twin replay engine for the Cold Chain EWS project
(Milestone 5a — skeleton, NO anomaly detection logic wired in yet).

STRUCTURAL PROXY NOTICE
-----------------------
All data derives from IOT-temp.csv — a generic IoT temperature sensor log,
NOT operational refrigerated-transport telemetry.  All injected anomalies are
synthetic proxy constructs.  Nothing here makes a food-safety claim.
See docs/AD_LOG.md (D1–D19).

PIPELINE TOPOLOGY NOTICE  (D17)
--------------------------------
The "3-stage Source → Transit → Destination" structure models a DATA PIPELINE:

    Source      = sensor reading generation / emission event
    Transit     = transmission / processing latency (currently 0.0 s, D19)
    Destination = monitoring / logging layer (anomaly detection in M5b)

This is NOT a physical multi-location cold-chain path (e.g., warehouse →
truck → store).  The underlying dataset has a single, constant room_id
("Room Admin") identified during M1 EDA — there is no real spatial topology
to exploit.  Any description of "stages" refers strictly to this data-pipeline
abstraction.

DESIGN DECISIONS IMPLEMENTED
-----------------------------
D17: 3-stage pipeline is a data-pipeline model, not physical staging.
     No spatial topology exists in this dataset (room_id is a constant).

D18: SimPy virtual clock advances using REAL inter-arrival gaps
     (gap_seconds, computed causally in M2).  NOT wall-clock pacing, NOT
     fixed ticks.  Out and In run as independent SimPy processes (D2).
     Replay uses temp_injected — the "as-observed" stream (per D5 precedent)
     — never the clean temp column.

D19: TRANSIT_LATENCY_SECONDS = 0.0 (disabled by default).  Transit stage is
     a pass-through no-op in this milestone, preserving exact batch
     cross-check capability for M5b.

NO DETECTION LOGIC: No baseline, IF, or LSTM anomaly-detection logic is
wired in here.  The Destination process only logs received readings.
Detection is M5b.

USAGE
-----
    python src/digital_twin.py

Inputs (read-only — M2 outputs):
    data/processed/out_labeled.csv
    data/processed/in_labeled.csv

Outputs:
    data/processed/twin_replay_log_out.csv
    data/processed/twin_replay_log_in.csv
"""

from __future__ import annotations

import logging
import pathlib
import sys
import time
from typing import Generator

import numpy as np
import pandas as pd
import simpy

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from config import TRANSIT_LATENCY_SECONDS

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT     = pathlib.Path(__file__).resolve().parents[1]
PROCESSED_DIR = REPO_ROOT / "data" / "processed"

OUT_LABELED_CSV = PROCESSED_DIR / "out_labeled.csv"
IN_LABELED_CSV  = PROCESSED_DIR / "in_labeled.csv"

REPLAY_LOG_OUT_CSV = PROCESSED_DIR / "twin_replay_log_out.csv"
REPLAY_LOG_IN_CSV  = PROCESSED_DIR / "twin_replay_log_in.csv"


# ══ SimPy process definitions ══════════════════════════════════════════════════


def source_process(
    env: simpy.Environment,
    df: pd.DataFrame,
    series_name: str,
    to_transit: simpy.Store,
) -> Generator:
    """
    SOURCE PROCESS — one instance per series (Out and In, per D2/D18).

    Reads rows from df in timestamp order and, for each row, yields an
    env.timeout equal to that row's gap_seconds (the real inter-arrival
    time since the previous reading in the same series, computed causally
    in M2).  Then places a reading event on the to_transit Store.

    Replay uses temp_injected (the "as-observed" stream, per D5/D18).
    Never reads the clean 'temp' column.

    Parameters
    ----------
    env         : SimPy Environment (shared clock).
    df          : Labeled DataFrame for this series, sorted by ts.
    series_name : 'Out' or 'In' — carried into every emitted event.
    to_transit  : SimPy Store connecting Source → Transit.
    """
    # NOTE: We sort by (ts ASC, gap_seconds DESC) with kind='stable'.
    # In M2 preprocessing, when transitioning to a new timestamp, the inter-arrival
    # gap from the previous timestamp was assigned to the first reading of the new minute,
    # with subsequent readings at that same minute having gap_seconds=0.0.
    # Sorting by (ts ASC, gap_seconds DESC) stably preserves this chronological order,
    # ensuring SimPy's virtual clock advances at the start of each timestamp group.
    df = df.sort_values(["ts", "gap_seconds"], ascending=[True, False], kind="stable").reset_index(drop=True)

    for _, row in df.iterrows():
        gap = float(row["gap_seconds"]) if pd.notna(row["gap_seconds"]) else 0.0
        # Advance virtual clock by the real inter-arrival gap (D18)
        yield env.timeout(gap)

        # Emit reading event as a dict; no wiring to detection logic yet (M5a)
        event = {
            "series":              series_name,
            "ts":                  row["ts"],
            "temp_injected":       float(row["temp_injected"]),
            "is_injected_anomaly": bool(row["is_injected_anomaly"]),
            "injection_type":      str(row["injection_type"]),
        }
        yield to_transit.put(event)


def transit_process(
    env: simpy.Environment,
    to_transit: simpy.Store,
    to_destination: simpy.Store,
    transit_latency: float,
) -> Generator:
    """
    TRANSIT PROCESS — models transmission / processing latency (D17/D19).

    Receives each reading from to_transit, applies
    env.timeout(transit_latency) (currently 0.0 — a no-op pass-through),
    then forwards the event to to_destination.

    The Transit stage exists for pipeline realism and extensibility.
    With TRANSIT_LATENCY_SECONDS = 0.0 the stage adds zero delay, so
    sim_time_received at the Destination is exactly the sum of gap_seconds
    up to that row — enabling exact cross-check against batch results (D19).

    PIPELINE TOPOLOGY REMINDER (D17): "Transit" here means data
    transmission latency, NOT a physical journey between locations.
    """
    while True:
        event = yield to_transit.get()
        # Apply transmission latency (virtual time only, no real sleep) (D18/D19)
        yield env.timeout(transit_latency)
        yield to_destination.put(event)


def destination_process(
    env: simpy.Environment,
    to_destination: simpy.Store,
    log_list: list,
    expected_count: int,
) -> Generator:
    """
    DESTINATION PROCESS — monitoring / logging layer (M5a skeleton).

    Receives each reading from to_destination and appends a record to
    log_list, including sim_time_received (env.now at the moment of
    receipt).  No anomaly detection logic is present in this milestone —
    that is M5b.

    Parameters
    ----------
    env              : SimPy Environment.
    to_destination   : SimPy Store connecting Transit → Destination.
    log_list         : Shared list to accumulate received-reading records.
    expected_count   : Total rows expected; used only for progress logging.
    """
    received = 0
    while received < expected_count:
        event = yield to_destination.get()
        record = {
            "series":              event["series"],
            "ts":                  event["ts"],
            "temp_injected":       event["temp_injected"],
            "is_injected_anomaly": event["is_injected_anomaly"],
            "injection_type":      event["injection_type"],
            "sim_time_received":   env.now,
            # NOTE: No anomaly detection fields — M5a skeleton only (M5b adds these)
        }
        log_list.append(record)
        received += 1

    logger.info(
        "Destination [%s]: all %d readings received (sim_time=%.3f s)",
        event["series"], received, env.now,
    )


# ══ Per-series replay orchestration ══════════════════════════════════════════


def replay_series(
    df: pd.DataFrame,
    series_name: str,
    transit_latency: float,
) -> pd.DataFrame:
    """
    Run the full 3-stage SimPy replay for one series.

    Creates a fresh SimPy Environment, instantiates Source → Transit →
    Destination processes, runs until all rows have been processed, and
    returns the log as a DataFrame.

    Parameters
    ----------
    df              : Labeled DataFrame (out_labeled or in_labeled), M2 output.
    series_name     : 'Out' or 'In'.
    transit_latency : TRANSIT_LATENCY_SECONDS (0.0 by default, D19).

    Returns
    -------
    pd.DataFrame with columns:
        series, ts, temp_injected, is_injected_anomaly, injection_type,
        sim_time_received
    """
    # Drop the initial NaN gap_seconds row (same as M3/M4 — row 0 has no predecessor).
    # Sort by (ts ASC, gap_seconds DESC) with kind='stable' to place the inter-minute
    # time advancement at the boundary of each timestamp cluster.
    df_clean = (
        df.dropna(subset=["gap_seconds"])
        .copy()
        .sort_values(["ts", "gap_seconds"], ascending=[True, False], kind="stable")
        .reset_index(drop=True)
    )

    logger.info(
        "Replay [%s]: %d source rows (after dropping 1 NaN-gap row from %d total).",
        series_name, len(df_clean), len(df),
    )

    env            = simpy.Environment()
    to_transit     = simpy.Store(env)
    to_destination = simpy.Store(env)
    log_list: list = []

    # Instantiate the three pipeline processes
    env.process(source_process(env, df_clean, series_name, to_transit))
    env.process(transit_process(env, to_transit, to_destination, transit_latency))
    env.process(destination_process(env, to_destination, log_list, len(df_clean)))

    env.run()  # advance virtual clock until all events are processed

    replay_df = pd.DataFrame(log_list)
    logger.info(
        "Replay [%s]: complete. %d rows logged. Final sim_time=%.3f s (= %.6f days).",
        series_name, len(replay_df),
        replay_df["sim_time_received"].iloc[-1],
        replay_df["sim_time_received"].iloc[-1] / 86400,
    )
    return replay_df


# ══ Main ═══════════════════════════════════════════════════════════════════════


def main() -> None:
    logger.info("=== Cold Chain EWS — SimPy Digital Twin Replay (Milestone 5a) ===")
    logger.info(
        "PROXY NOTICE: All data is synthetic proxy telemetry. No food-safety claims."
    )
    logger.info(
        "D17: Pipeline stages model data flow, NOT physical cold-chain geography. "
        "dataset has a single constant room_id — no real spatial topology."
    )
    logger.info(
        "D18: Virtual clock advances via real gap_seconds. "
        "temp_injected used (not clean temp). Out/In are independent processes."
    )
    logger.info(
        "D19: TRANSIT_LATENCY_SECONDS=%.1f (disabled — pass-through for exact M5b cross-check).",
        TRANSIT_LATENCY_SECONDS,
    )
    logger.info("NO DETECTION LOGIC: Destination logs only. Detection is M5b.")

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Load labeled CSVs (M2 outputs — read-only)
    logger.info("Loading labeled CSVs …")
    df_out = pd.read_csv(OUT_LABELED_CSV, parse_dates=["ts"])
    df_in  = pd.read_csv(IN_LABELED_CSV,  parse_dates=["ts"])
    logger.info("  Out: %d rows | In: %d rows", len(df_out), len(df_in))

    # ── Full two-series replay — wall-clock timed ─────────────────────────────
    wall_start = time.perf_counter()

    logger.info("--- Starting Out replay ---")
    log_out = replay_series(df_out, "Out", TRANSIT_LATENCY_SECONDS)

    logger.info("--- Starting In replay ---")
    log_in  = replay_series(df_in,  "In",  TRANSIT_LATENCY_SECONDS)

    wall_elapsed = time.perf_counter() - wall_start
    logger.info(
        "Total wall-clock time for both series: %.3f seconds "
        "(NOT the simulated 133-day span — SimPy clock is virtual).",
        wall_elapsed,
    )

    # ── Save replay logs ──────────────────────────────────────────────────────
    log_out.to_csv(REPLAY_LOG_OUT_CSV, index=False)
    log_in.to_csv(REPLAY_LOG_IN_CSV,   index=False)
    logger.info("Saved: %s (%d rows)", REPLAY_LOG_OUT_CSV.name, len(log_out))
    logger.info("Saved: %s (%d rows)", REPLAY_LOG_IN_CSV.name,  len(log_in))

    logger.info("=== Milestone 5a replay complete ===")
    logger.info(
        "Confirm: no detection logic added | no time.sleep used | "
        "no M1-M4b files touched | TRANSIT_LATENCY_SECONDS=0.0"
    )


if __name__ == "__main__":
    main()
