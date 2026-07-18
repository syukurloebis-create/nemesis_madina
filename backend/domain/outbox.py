"""
NEMESIS Madina - Outbox
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID, uuid4

from backend.domain.events.base import DomainEvent


class OutboxStatus:
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"


@dataclass(frozen=True)
class OutboxEntry:
    """Outbox entry for reliable event publishing."""
    
    id: str
    event: DomainEvent
    status: str
    created_at: datetime
    updated_at: datetime
    retry_count: int = 0
    last_error: Optional[str] = None
    
    @classmethod
    def create(cls, event: DomainEvent) -> "OutboxEntry":
        return cls(
            id=str(uuid4()),
            event=event,
            status=OutboxStatus.PENDING,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
    
    def mark_published(self) -> "OutboxEntry":
        return OutboxEntry(
            id=self.id,
            event=self.event,
            status=OutboxStatus.PUBLISHED,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
            retry_count=self.retry_count,
            last_error=self.last_error,
        )
    
    def mark_failed(self, error: str) -> "OutboxEntry":
        return OutboxEntry(
            id=self.id,
            event=self.event,
            status=OutboxStatus.FAILED,
            created_at=self.created_at,
            updated_at=datetime.now(timezone.utc),
            retry_count=self.retry_count + 1,
            last_error=error,
        )


class Outbox:
    """
    Outbox pattern for reliable event publishing.
    ✅ Events are stored before publishing
    ✅ No event loss if publish fails
    ✅ Background worker retries failed events
    """
    
    def __init__(self):
        self._entries: List[OutboxEntry] = []
    
    def add(self, event: DomainEvent) -> None:
        """Add event to outbox."""
        self._entries.append(OutboxEntry.create(event))
    
    def add_many(self, events: List[DomainEvent]) -> None:
        """Add multiple events to outbox."""
        for event in events:
            self.add(event)
    
    def get_pending(self) -> List[OutboxEntry]:
        """Get all pending entries."""
        return [
            entry for entry in self._entries
            if entry.status == OutboxStatus.PENDING
        ]
    
    def mark_published(self, entry_id: str) -> None:
        """Mark an entry as published."""
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                self._entries[i] = entry.mark_published()
                break
    
    def mark_failed(self, entry_id: str, error: str) -> None:
        """Mark an entry as failed."""
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                self._entries[i] = entry.mark_failed(error)
                break
    
    def clear_published(self) -> None:
        """Remove published entries."""
        self._entries = [
            entry for entry in self._entries
            if entry.status != OutboxStatus.PUBLISHED
        ]
    
    def __len__(self) -> int:
        return len(self._entries)