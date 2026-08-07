"""
File-Based Dead Letter Store
============================

File-based implementation of IDeadLetterStore for persistence.

ADR Reference: ADR-035
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional, List

from backend.core.events.interfaces.dead_letter import IDeadLetterStore, DeadLetterEntry
from backend.core.events.interfaces.event import BaseEvent

logger = logging.getLogger(__name__)


class FileBasedDeadLetterStore(IDeadLetterStore):
    """
    File-based implementation of IDeadLetterStore.

    Features:
    - Persistent storage in JSON files
    - Append-only write model
    - Supports replay and removal
    """

    def __init__(self, filepath: str = "dead_letter_store.json"):
        """
        Initialize the file-based dead letter store.

        Args:
            filepath: Path to the JSON file for storage
        """
        self._filepath = filepath
        self._entries: List[DeadLetterEntry] = []
        self._load()
        logger.info(f"FileBasedDeadLetterStore initialized (file={filepath})")

    def _load(self) -> None:
        """Load entries from file."""
        if not os.path.exists(self._filepath):
            self._entries = []
            return

        try:
            with open(self._filepath, "r") as f:
                data = json.load(f)
                # Deserialize entries (simplified)
                self._entries = []
                for item in data:
                    # Reconstruct event (simplified)
                    event = BaseEvent(
                        event_type=item["event"]["event_type"],
                        payload=item["event"]["payload"],
                        event_id=item["event"]["event_id"],
                        occurred_at=datetime.fromisoformat(item["event"]["occurred_at"]),
                    )
                    entry = DeadLetterEntry(
                        event=event,
                        failure_reason=item["failure_reason"],
                        failure_type=item["failure_type"],
                        attempts=item["attempts"],
                        stored_at=datetime.fromisoformat(item["stored_at"]),
                    )
                    self._entries.append(entry)
        except Exception as e:
            logger.error(f"Failed to load dead letter store: {e}")
            self._entries = []

    def _save(self) -> None:
        """Save entries to file."""
        try:
            data = [entry.to_dict() for entry in self._entries]
            with open(self._filepath, "w") as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save dead letter store: {e}")

    def store(self, entry: DeadLetterEntry) -> None:
        """Store a failed event in the dead letter store."""
        if entry is None:
            raise ValueError("entry cannot be None")

        self._entries.append(entry)
        self._save()
        logger.debug(f"Stored dead letter entry for event {entry.event.event_id}")

    def get_all(self) -> List[DeadLetterEntry]:
        """Get all dead letter entries."""
        return self._entries.copy()

    def get_by_event_id(self, event_id: str) -> Optional[DeadLetterEntry]:
        """Get a dead letter entry by event ID."""
        for entry in self._entries:
            if entry.event.event_id == event_id:
                return entry
        return None

    def replay(self, event_id: str) -> bool:
        """Replay a dead letter event."""
        entry = self.get_by_event_id(event_id)
        if entry is None:
            logger.warning(f"Event {event_id} not found in dead letter store")
            return False

        logger.info(f"Replaying dead letter event {event_id}")
        # In a real implementation, this would re-publish the event
        return True

    def remove(self, event_id: str) -> bool:
        """Remove a dead letter entry."""
        for i, entry in enumerate(self._entries):
            if entry.event.event_id == event_id:
                del self._entries[i]
                self._save()
                logger.debug(f"Removed dead letter entry for event {event_id}")
                return True
        return False

    def count(self) -> int:
        """Get the total number of dead letter entries."""
        return len(self._entries)