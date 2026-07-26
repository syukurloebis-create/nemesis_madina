"""
NEMESIS Madina - Aggregate Root Base
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import Tuple, Any, Optional
from dataclasses import dataclass, field

from backend.domain.events.base import DomainEvent
from backend.domain.value_objects.case_id import CaseId


@dataclass
class AggregateRoot(ABC):
    """
    Base class for all aggregate roots.

    ✅ Uses deque for efficient FIFO event storage
    ✅ id returns CaseId (type-safe)
    ✅ version for optimistic locking
    ✅ clear_events() for manual cleanup
    """

    # Internal state - NEVER passed to constructor
    _pending_events: deque[DomainEvent[Any]] = field(
        default_factory=deque,
        init=False,      # ✅ Remove from constructor
        repr=False,      # ✅ Cleaner repr
    )
    _version: int = field(
        default=0,
        init=False,      # ✅ Remove from constructor
    )

    def _record(self, event: DomainEvent[Any]) -> None:
        """
        Record a domain event (internal API only).
        ✅ Increments version on each event
        """
        self._pending_events.append(event)
        self._version += 1

    def pull_domain_events(self) -> Tuple[DomainEvent[Any], ...]:
        """
        Pull all pending events (consume semantics).
        ✅ Returns tuple, clears internal list
        """
        events = tuple(self._pending_events)
        self._pending_events.clear()
        return events

    def peek_domain_events(self) -> Tuple[DomainEvent[Any], ...]:
        """
        Peek at pending events without consuming them.
        ✅ Non-destructive event inspection
        ✅ Useful for testing and debugging
        """
        return tuple(self._pending_events)

    def has_pending_events(self) -> bool:
        """Check if there are pending events."""
        return len(self._pending_events) > 0

    def clear_events(self) -> None:
        """
        Clear all pending events without pulling.
        ✅ Useful for manual cleanup or peeking
        """
        self._pending_events.clear()
    

    @property
    def version(self) -> int:
        """Get current version (for optimistic locking)."""
        return self._version

    @property
    @abstractmethod
    def id(self) -> CaseId:
        """Get aggregate identifier as CaseId (type-safe)."""
        pass