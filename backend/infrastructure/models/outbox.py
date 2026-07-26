# backend/infrastructure/models/outbox.py

"""
Legacy compatibility shim - redirects to new location.
This file will be removed after all imports are migrated.

Target Removal: Phase 1
"""

import warnings
from backend.infrastructure.outbox.outbox import OutboxMessage, OutboxRepository

warnings.warn(
    "backend.infrastructure.models.outbox is deprecated. Use backend.infrastructure.outbox.outbox instead.",
    DeprecationWarning,
    stacklevel=2,
)

# ✅ Alias untuk kompatibilitas
OutboxModel = OutboxMessage

__all__ = [
    "OutboxMessage",
    "OutboxRepository",
    "OutboxModel",  # ← Tambahkan
]