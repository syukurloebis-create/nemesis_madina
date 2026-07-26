# backend/infrastructure/outbox/repository.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from backend.infrastructure.outbox.outbox import OutboxMessage


class IOutboxRepository(ABC):
    """Canonical Outbox Repository Contract."""

    @abstractmethod
    async def save(self, message: OutboxMessage) -> None:
        """Save a new outbox message."""
        pass

    @abstractmethod
    async def claim_pending(self, limit: int = 100) -> List[OutboxMessage]:
        """Claim pending messages for processing."""
        pass

    @abstractmethod
    async def mark_published(self, message_id: str) -> None:
        """Mark message as published."""
        pass

    @abstractmethod
    async def mark_failed(self, message_id: str, error: str) -> None:
        """Mark message as failed."""
        pass

    @abstractmethod
    async def mark_dead_letter(self, message_id: str, error: str) -> None:
        """Move message to dead letter queue."""
        pass

    @abstractmethod
    async def count_pending(self) -> int:
        """Get count of pending messages."""
        pass