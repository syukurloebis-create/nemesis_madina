# backend/infrastructure/events/stored_event.py

"""
NEMESIS Madina - Stored Event Envelope
Infrastructure contract for event storage with metadata.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from backend.domain.events.base import DomainEvent

T = TypeVar("T", bound=DomainEvent)


@dataclass(frozen=True)
class StoredEvent(Generic[T]):
    """
    Infrastructure event envelope.

    Contains persistence metadata.
    Never leaks into domain.
    """

    commit_position: int
    aggregate_id: str
    event_version: int
    event: T
    created_at: datetime