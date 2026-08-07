"""
Dead Letter Store Interface
===========================

Defines the IDeadLetterStore interface for storing failed events.

ADR Reference: ADR-035
Requirements: REQ-DL-001
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Any

from backend.core.events.interfaces.event import IEvent


@dataclass(frozen=True)
class DeadLetterEntry:
    """
    An entry in the dead letter store.

    Contains the failed event and the reason for failure.
    Immutable by design.
    """
    event: IEvent
    failure_reason: str
    failure_type: str
    attempts: int
    stored_at: datetime = None

    def __post_init__(self):
        if self.stored_at is None:
            object.__setattr__(self, "stored_at", datetime.now(timezone.utc))
        if self.stored_at.tzinfo is None:
            object.__setattr__(self, "stored_at", self.stored_at.replace(tzinfo=timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "event": self.event.to_dict(),
            "failure_reason": self.failure_reason,
            "failure_type": self.failure_type,
            "attempts": self.attempts,
            "stored_at": self.stored_at.isoformat(),
        }


class IDeadLetterStore(ABC):
    """
    Dead Letter Store Contract.

    Stores events that have failed permanently.

    Semantics (ADR-035):
    - Dead Letter: Storage for failed events after max retries
    - Supports inspection and replay
    """

    @abstractmethod
    def store(self, entry: DeadLetterEntry) -> None:
        """
        Store a failed event in the dead letter store.

        Precondition: event is not None
        Precondition: failure_reason is not None
        Postcondition: event is stored with failure reason

        Args:
            entry: The dead letter entry to store
        """
        pass

    @abstractmethod
    def get_all(self) -> list[DeadLetterEntry]:
        """
        Get all dead letter entries.

        Returns:
            List of all dead letter entries
        """
        pass

    @abstractmethod
    def get_by_event_id(self, event_id: str) -> Optional[DeadLetterEntry]:
        """
        Get a dead letter entry by event ID.

        Args:
            event_id: The event ID to look up

        Returns:
            The dead letter entry, or None if not found
        """
        pass

    @abstractmethod
    def replay(self, event_id: str) -> bool:
        """
        Replay a dead letter event.

        Args:
            event_id: The event ID to replay

        Returns:
            True if replay was successful, False otherwise
        """
        pass

    @abstractmethod
    def remove(self, event_id: str) -> bool:
        """
        Remove a dead letter entry.

        Args:
            event_id: The event ID to remove

        Returns:
            True if removed, False if not found
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        Get the total number of dead letter entries.

        Returns:
            The total count
        """
        pass