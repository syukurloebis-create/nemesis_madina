# backend/core/entities/models.py

"""
Legacy compatibility shim - redirects to new location.
This file will be removed after all imports are migrated.

Target Removal: Phase 1
Owner: Domain Layer
"""

import warnings
from backend.domain.entities.finding import Finding

warnings.warn(
    "backend.core.entities.models is deprecated. Use backend.domain.entities.finding instead.",
    DeprecationWarning,
    stacklevel=2,
)

# Only re-export if symbol actually exists
BaseEntity = Finding

# These symbols need further audit - raise error on access
__all__ = ["BaseEntity", "EntityStatus", "AnalysisResult", "AnomalyReport"]


def __getattr__(name: str):
    if name in ["EntityStatus", "AnalysisResult", "AnomalyReport"]:
        raise RuntimeError(
            f"Compatibility shim incomplete: '{name}' has no verified mapping yet. "
            f"Please audit and migrate this import."
        )
    raise AttributeError(f"module {__name__} has no attribute {name}")