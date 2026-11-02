"""
src/fusion/__init__.py
======================
Dempster-Shafer Evidential Deep Learning (EDL) multi-detector fusion layer.
Proposal P5 from docs/RESEARCH_HANDOFF.md.
"""

from src.fusion.evidential_fusion import (
    EvidentialFusionMLP,
    evidential_loss,
    kl_divergence_dirichlet,
    dempster_shafer_combine,
)

__all__ = [
    "EvidentialFusionMLP",
    "evidential_loss",
    "kl_divergence_dirichlet",
    "dempster_shafer_combine",
]

