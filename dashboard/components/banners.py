"""
dashboard/components/banners.py
===============================
Header titles, persistent structural proxy notice, and train-side demo banners (D31).
"""

from __future__ import annotations

import streamlit as st

from dashboard.constants import ICON_APP, ICON_INFO, ICON_WARNING


def render_header_and_disclaimers() -> None:
    """Render page title and persistent D31 Structural Proxy Notice banner."""
    st.title(f"{ICON_APP} Cold Chain EWS — Live Digital Twin Anomaly Monitor")
    st.markdown(
        "**A presentation-grade streaming early warning demonstration comparing Naive Baseline, "
        "Isolation Forest, and LSTM-Autoencoder anomaly detection.**"
    )

    # D31: Persistent Structural Proxy Disclaimer Banner
    st.warning(
        "**STRUCTURAL PROXY NOTICE**: All telemetry derives from `IOT-temp.csv` "
        "(generic IoT temperature sensor log), **NOT** refrigerated-transport operations. "
        "All injected anomalies are synthetic proxy constructs. Detectors carry no food-safety significance. "
        "See `docs/AD_LOG.md` (D1–D34).",
        icon=ICON_WARNING,
    )


def render_train_demo_banner(status: str) -> None:
    """Render D31 informational disclaimer if selected injection is from training set."""
    if status == "train":
        st.info(
            "**DEMO ONLY — Prior Training Exposure (D26/D31)**: "
            "This injection occurred during the training time range (`ts < cutoff_ts`). "
            "Its live detection is demonstrated strictly as an interactive deployment preview, "
            "**not** as an out-of-sample scientific performance claim.",
            icon=ICON_INFO,
        )
