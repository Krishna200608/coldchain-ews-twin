"""
dashboard/constants.py
======================
UI-specific constants, icon mapping, and navigation definitions for the
Streamlit Digital Twin dashboard.

CRITICAL RULE:
Core scientific parameters (SEARCH_HORIZON_MINUTES, ROLLING_WINDOW,
LSTM_WINDOW_LENGTH, K_SIGMA, etc.) MUST be imported directly from
src/config.py. Never duplicate or redefine their values here.
"""

from __future__ import annotations

import pathlib
import sys

# Ensure repository root and src directory are on sys.path
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_DIR = REPO_ROOT / "src"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

# Import core scientific and pipeline constants directly from src.config
from src.config import (
    K_SIGMA,
    LSTM_WINDOW_LENGTH,
    ROLLING_WINDOW,
    SEARCH_HORIZON_MINUTES,
)

# Core filesystem paths
MODELS_DIR = REPO_ROOT / "models"
DATA_DIR = REPO_ROOT / "data" / "processed"

# Detector-specific threshold constants from Milestone 4b
LSTM_THRESH_OUT: float = 1.010091
LSTM_THRESH_IN: float = 1.512753

# Pre-warm buffer lengths (D33)
IF_PREWARM_STEPS: int = ROLLING_WINDOW
LSTM_PREWARM_STEPS: int = LSTM_WINDOW_LENGTH

# UI Material Symbol shortcodes (M6.1 icon design standard)
ICON_APP = ":material/ac_unit:"
ICON_NAV = ":material/navigation:"
ICON_TOUR = ":material/tour:"
ICON_EXPLORE = ":material/explore:"
ICON_SPEED = ":material/speed:"
ICON_FIRST_PAGE = ":material/first_page:"
ICON_LAST_PAGE = ":material/last_page:"
ICON_BASELINE = ":material/rule:"
ICON_IF = ":material/forest:"
ICON_LSTM = ":material/memory:"
ICON_CHART = ":material/timeline:"
ICON_EXPANDER = ":material/monitoring:"
ICON_ALERT_LOG = ":material/list_alt:"
ICON_AUDIT = ":material/fact_check:"
ICON_VERIFIED = ":material/verified:"
ICON_WARNING = ":material/warning:"
ICON_INFO = ":material/info:"
ICON_ERROR = ":material/error:"

# Replay speed factor options (D28)
REPLAY_SPEED_OPTIONS: list[str] = ["1x", "5x", "10x", "25x", "Instant"]

# Guided Tour showcase definitions (D29, D34)
GUIDED_TOUR_STEPS: list[dict[str, str]] = [
    {
        "id": "out_step_001",
        "label": "1. out_step_001 — Step",
        "summary": "Step Anomaly: Catastrophic jump triggers all 3 models synchronously at onset.",
    },
    {
        "id": "out_drift_009",
        "label": "2. out_drift_009 — Drift",
        "summary": "Thermal Drift: Multivariate early warning lead vs sequence memory inertia lag.",
    },
    {
        "id": "out_flatline_013",
        "label": "3. out_flatline_013 — Flatline",
        "summary": "In-Range Flatline: Zero variance failure for Baseline, subtle detection by IF.",
    },
    {
        "id": "in_drift_023",
        "label": "4. in_drift_023 — Drift",
        "summary": "Inbound Drift: IF achieves +11.0 min early warning prior to baseline crossing.",
    },
]
