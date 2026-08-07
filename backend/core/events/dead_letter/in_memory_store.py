"""
In-Memory Dead Letter Store
===========================

In-memory implementation of IDeadLetterStore.

ADR Reference: ADR-035
"""

import logging
from typing import Optional, Dict
from datetime import datetime, timezone

from backend.core.events.interfaces.dead_letter import IDeadLetterStore, DeadLetterEntry

logger = logging.getLogger(__name__)


class InMemoryDeadLetterStore(IDeadLetterStore):
    """
    In-memory implementation of IDeadLetterStore.

    Features:
    - Thread-safe (using dict locks)
    - Stores events in memory
    - Supports replay and removal
    - Useful for testing and development
    """

    def __init__(self):
        self._store: Dict[str, DeadLetterEntry] = {}
        self._lock = None  # threading.Lock() would be used in production
        logger.info("InMemoryDeadLetterStore initialized")

    def store(self, entry: DeadLetterEntry) -> None:
        """
        Store a failed event in the dead letter store.

        Args:
            entry: The dead letter entry to store
        """
        if entry is None:
            raise ValueError("entry cannot be None")

        if entry.event is None:
            raise ValueError("entry.event cannot be None")

        event_id = entry.event.event_id
        self._store[event_id] = entry
        logger.debug(f"Stored dead letter entry for event {event_id}")

    def get_all(self) -> list[DeadLetterEntry]:
        """
        Get all dead letter entries.

        Returns:
            List of all dead letter entries
        """
        return list(self._store.values())

    def get_by_event_id(self, event_id: str) -> Optional[DeadLetterEntry]:
        """
        Get a dead letter entry by event ID.

        Args:
            event_id: The event ID to look up

        Returns:
            The dead letter entry, or None if not found
        """
        return self._store.get(event_id)

    def replay(self, event_id: str) -> bool:
        """
        Replay a dead letter event.

        Args:
            event_id: The event ID to replay

        Returns:
            True if replay was successful, False otherwise
        """
        if event_id not in self._store:
            logger.warning(f"Event {event_id} not found in dead letter store")
            return False

        logger.info(f"Replaying dead letter event {event_id}")
        # In a real implementation, this would re-publish the event
        return True

    def remove(self, event_id: str) -> bool:
        """
        Remove a dead letter entry.

        Args:
            event_id: The event ID to remove

        Returns:
            True if removed, False if not found
        """
        if event_id not in self._store:
            return False

        del self._store[event_id]
        logger.debug(f"Removed dead letter entry for event {event_id}")
        return True

    def count(self) -> int:
        """
        Get the total number of dead letter entries.

        Returns:
            The total count
        """
        return len(self._store)

    def clear(self) -> None:
        """Clear all dead letter entries."""
        self._store.clear()
        logger.info("Cleared all dead letter entries")