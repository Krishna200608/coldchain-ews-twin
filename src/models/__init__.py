"""
src/models/__init__.py
======================
Deep learning research models for Cold Chain EWS Digital Twin:
- PILSTMAutoencoder: Physics-Informed LSTM-AE regularized with Newton's Law of Cooling (Proposal P2)
- VLSTMAutoencoder: Variational LSTM-AE with uncertainty quantification (Proposal P1)
"""

from src.models.pilstm_ae import (
    PILSTMAutoencoder,
    PILSTMAEEncoder,
    PILSTMAEDecoder,
    physics_informed_loss,
    fit_physics_parameters,
)
from src.models.vlstm_ae import (
    VLSTMAutoencoder,
    VLSTMEncoder,
    VLSTMDecoder,
    vlstm_loss,
)

__all__ = [
    "PILSTMAutoencoder",
    "PILSTMAEEncoder",
    "PILSTMAEDecoder",
    "physics_informed_loss",
    "fit_physics_parameters",
    "VLSTMAutoencoder",
    "VLSTMEncoder",
    "VLSTMDecoder",
    "vlstm_loss",
]
