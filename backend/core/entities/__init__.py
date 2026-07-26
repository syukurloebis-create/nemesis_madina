# backend/core/entities/__init__.py

"""
Legacy compatibility shim - redirects to new location.
This file will be removed after all imports are migrated.

Target Removal: Phase 1
Owner: Domain Layer

VERIFIED: backend.domain.entities.finding exists
VERIFIED: Finding replaces BaseEntity
"""

import warnings
from typing import Any

warnings.warn(
    "backend.core.entities is deprecated. Use backend.domain.entities instead.",
    DeprecationWarning,
    stacklevel=2,
)

# ============================================================
# VERIFIED MAPPINGS (from audit)
# ============================================================

_LAZY_IMPORTS = {
    # Verified: backend.domain.entities.finding exists
    "BaseEntity": ("backend.domain.entities.finding", "Finding"),
    # EntityStatus, AnalysisResult, AnomalyReport need further audit
    "EntityStatus": None,  # Not verified yet
    "AnalysisResult": None,  # Not verified yet
    "AnomalyReport": None,  # Not verified yet
}


def __getattr__(name: str) -> Any:
    """Lazy import for compatibility shim."""
    if name not in _LAZY_IMPORTS:
        raise AttributeError(f"module {__name__} has no attribute {name}")
    
    import_info = _LAZY_IMPORTS[name]
    if import_info is None:
        raise RuntimeError(
            f"Compatibility shim incomplete: '{name}' has no verified mapping yet. "
            f"Please audit and migrate this import."
        )
    
    module_path, attr_name = import_info
    try:
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, attr_name)
    except (ImportError, AttributeError) as e:
        raise RuntimeError(
            f"Failed to resolve '{name}' from '{module_path}'. "
            f"Please migrate to new location."
        ) from e


__all__ = [
    "BaseEntity",
    "EntityStatus",
    "AnalysisResult",
    "AnomalyReport",
]