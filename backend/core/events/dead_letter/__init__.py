"""
Dead Letter Package
===================

Dead letter store implementations for the canonical event architecture.

ADR Reference: ADR-035
"""

from backend.core.events.dead_letter.in_memory_store import InMemoryDeadLetterStore
from backend.core.events.dead_letter.file_store import FileBasedDeadLetterStore

__all__ = [
    "InMemoryDeadLetterStore",
    "FileBasedDeadLetterStore",
]