"""
src/data_acquisition.py
=======================
Downloads the Kaggle dataset `atulanandjha/temperature-readings-iot-devices`
to data/raw/.

IMPORTANT — STRUCTURAL PROXY NOTICE
-------------------------------------
This dataset is a generic IoT temperature sensor log, NOT real
refrigerated-transport telemetry. It is used exclusively as a structural
proxy for the cold-chain digital twin pipeline. See README.md and
docs/data_profile.md for full context.

AUTHENTICATION
--------------
This script does NOT hardcode any Kaggle credentials. It relies on the
Kaggle API credentials file already present on your system at:
  - Linux/macOS : ~/.kaggle/kaggle.json
  - Windows     : C:\\Users\\<you>\\.kaggle\\kaggle.json

One-time setup:
  1. Go to https://www.kaggle.com/settings → API → "Create New Token"
  2. Save the downloaded kaggle.json to the path above
  3. chmod 600 ~/.kaggle/kaggle.json  (Linux/macOS only)

Never commit kaggle.json — it is listed in .gitignore.

USAGE
-----
  python src/data_acquisition.py

The raw CSV is written to data/raw/ without any modification.
"""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── Paths ──────────────────────────────────────────────────────────────────────
# Resolve relative to this file so the script works regardless of cwd.
REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
DATASET_SLUG = "atulanandjha/temperature-readings-iot-devices"


def _ensure_raw_dir() -> None:
    """Create data/raw/ if it doesn't already exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Raw data directory: %s", RAW_DIR)


def _download_via_kagglehub() -> Path:
    """
    Download the dataset using kagglehub (preferred method).

    kagglehub caches downloads in its own cache dir and returns the local path.
    We then copy the CSV(s) into data/raw/.

    Returns
    -------
    Path
        Path to the data/raw/ directory after copying.

    Raises
    ------
    ImportError
        If kagglehub is not installed.
    """
    import kagglehub  # type: ignore[import]

    logger.info("Attempting download via kagglehub …")
    cache_path = Path(kagglehub.dataset_download(DATASET_SLUG))
    logger.info("kagglehub cache path: %s", cache_path)

    # Copy every CSV found in the cache to data/raw/
    csv_files = list(cache_path.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV files found in kagglehub cache at {cache_path}"
        )
    for src in csv_files:
        dst = RAW_DIR / src.name
        if dst.exists():
            logger.info("Already present, skipping copy: %s", dst.name)
        else:
            shutil.copy2(src, dst)
            logger.info("Copied → %s", dst)
    return RAW_DIR


def _download_via_kaggle_api() -> Path:
    """
    Fallback: download the dataset using the official kaggle CLI API client.

    Requires the `kaggle` package and ~/.kaggle/kaggle.json.

    Returns
    -------
    Path
        Path to the data/raw/ directory after extraction.

    Raises
    ------
    ImportError
        If the kaggle package is not installed.
    """
    import kaggle  # type: ignore[import]  # noqa: F401 — triggers auth check

    logger.info("Attempting download via kaggle API (fallback) …")
    from kaggle.api.kaggle_api_extended import KaggleApiExtended  # type: ignore[import]

    api = KaggleApiExtended()
    api.authenticate()
    api.dataset_download_files(
        DATASET_SLUG,
        path=str(RAW_DIR),
        unzip=True,
        quiet=False,
    )
    logger.info("Download complete via kaggle API → %s", RAW_DIR)
    return RAW_DIR


def acquire() -> Path:
    """
    Main entry point: try kagglehub first, fall back to kaggle API.

    Returns
    -------
    Path
        The data/raw/ directory containing the downloaded CSV(s).
    """
    _ensure_raw_dir()

    # ── Try kagglehub ──────────────────────────────────────────────────────────
    try:
        return _download_via_kagglehub()
    except ImportError:
        logger.warning("kagglehub not installed — falling back to kaggle API.")
    except Exception as exc:
        logger.warning("kagglehub download failed (%s) — falling back.", exc)

    # ── Try kaggle API ─────────────────────────────────────────────────────────
    try:
        return _download_via_kaggle_api()
    except ImportError:
        logger.error(
            "Neither kagglehub nor the kaggle package is installed.\n"
            "Install one of them:\n"
            "  pip install kagglehub\n"
            "  pip install kaggle"
        )
        sys.exit(1)
    except Exception as exc:
        logger.error("kaggle API download failed: %s", exc)
        sys.exit(1)


def _verify_download(raw_dir: Path) -> None:
    """
    Log the CSV files present in data/raw/ after download so the user
    can confirm which file(s) arrived.
    """
    csv_files = sorted(raw_dir.glob("*.csv"))
    if not csv_files:
        logger.warning("No CSV files found in %s — check the download step.", raw_dir)
        return
    logger.info("Files in data/raw/:")
    for f in csv_files:
        size_mb = f.stat().st_size / 1_048_576
        logger.info("  %-40s  %.2f MB", f.name, size_mb)


if __name__ == "__main__":
    logger.info("=== Cold Chain EWS — Data Acquisition ===")
    logger.info("Dataset slug : %s", DATASET_SLUG)
    logger.info(
        "NOTE: This dataset is a STRUCTURAL PROXY for cold-chain telemetry, "
        "not real refrigerated-transport data. See README.md for details."
    )

    raw_dir = acquire()
    _verify_download(raw_dir)

    logger.info("Done. Raw data is in: %s", raw_dir)
    logger.info(
        "Next step: open notebooks/01_eda.ipynb to explore the data."
    )
