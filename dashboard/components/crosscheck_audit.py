"""
dashboard/components/crosscheck_audit.py
========================================
Milestone 5b Cross-Check Verification Audit component with bit-exact match
validation banner, responsive audit table, and protocol detail expander.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.constants import (
    ICON_AUDIT,
    ICON_VERIFIED,
    ICON_WARNING,
)


def _summarize_audit_notes(note_str: str) -> str:
    """Map verbose verification strings to concise in-table summaries to prevent canvas truncation."""
    s = str(note_str)
    if "whole-series" in s:
        return "Exact match (M2 whole-series threshold, D24)"
    if "M3 batch test" in s:
        return "Exact match (M3 batch test evaluation)"
    if "M4b batch test" in s:
        return "Exact match (M4b batch test, unaffected by D23)"
    if "never flagged" in s:
        return "Exact match (never flagged in window)"
    return s


def render_crosscheck_audit(
    status: str,
    selected_inj_id: str,
    crosscheck_df: pd.DataFrame,
) -> None:
    """Render the Milestone 5b Cross-Check Verification Audit footer."""
    st.markdown("---")
    st.subheader("Milestone 5b Cross-Check Verification Audit", icon=ICON_AUDIT)

    if status == "test":
        # Filter cross-check report for this injection
        m5b_report = crosscheck_df[crosscheck_df["injection_id"] == selected_inj_id].copy()
        all_matched = bool((m5b_report["match"] == True).all() or (m5b_report["match"] == "True").all())

        c_audit1, c_audit2 = st.columns([3, 1])
        with c_audit1:
            st.markdown(
                "This injection is part of the **6 out-of-sample test injections** representing the primary scientific benchmark. "
                "All streaming alarms produced by the Digital Twin are verified against the frozen batch evaluations from Milestones 2, 3, and 4b."
            )
        with c_audit2:
            if all_matched:
                st.success(
                    "100% BIT-EXACT MATCH\n\nAll 3 live detectors match frozen Milestone 2/3/4b evaluations exactly.",
                    icon=ICON_VERIFIED,
                )
            else:
                st.warning("Cross-check review required.", icon=ICON_WARNING)

        m5b_display = m5b_report.copy()
        m5b_display["notes_summary"] = m5b_display["notes"].apply(_summarize_audit_notes)

        # Full container width table with concise notes and unconstrained column to fill width
        st.dataframe(
            m5b_display[["detector", "live_alarm_timestamp", "batch_alarm_timestamp", "match", "notes_summary"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "detector": st.column_config.TextColumn("Detector", width="small"),
                "live_alarm_timestamp": st.column_config.TextColumn("Live Alarm", width="medium"),
                "batch_alarm_timestamp": st.column_config.TextColumn("Batch Alarm", width="medium"),
                "match": st.column_config.CheckboxColumn("Exact Match", width="small"),
                "notes_summary": st.column_config.TextColumn(
                    "Verification Notes",
                    help="Concise verification summary against frozen batch baseline (see expander below for full scientific protocol detail)",
                ),
            },
        )

        with st.expander("Detailed Verification Notes & Scientific Protocol Context (D23, D24, D26)", expanded=False):
            for _, r in m5b_report.iterrows():
                st.markdown(f"- **{r['detector'].upper()}**: {r['notes']}")
    else:
        st.markdown(
            f"**Injection `{selected_inj_id}` is a training-region deployment demonstration (D26/D31).**<br>"
            "Because models had prior training exposure to this period, batch cross-check values are not computed or claimed as an out-of-sample benchmark.",
            unsafe_allow_html=True,
        )
