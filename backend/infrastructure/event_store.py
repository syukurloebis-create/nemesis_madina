# backend/infrastructure/event_store.py

"""
Legacy compatibility shim - redirects to new location.
Target Removal: Phase 1
"""

import warnings
from backend.cases.event_store import EventStore  # ← Import actual implementation
from backend.cases.event_store import EventStore as EventStoreRepository  # ← Alias for legacy

warnings.warn(
    "backend.infrastructure.event_store is deprecated. Use backend.cases.event_store instead.",
    DeprecationWarning,
    stacklevel=2,
)

# ✅ Ekspor kedua nama untuk kompatibilitas
__all__ = [
    "EventStore",
    "EventStoreRepository",  # ← Legacy name
]