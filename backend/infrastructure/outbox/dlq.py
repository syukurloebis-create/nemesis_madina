"""
NEMESIS Madina - Dead Letter Queue
✅ DLQ for failed messages
✅ Poison message handling
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.infrastructure.models.outbox import DeadLetterModel


class DeadLetterQueue:
    """Dead Letter Queue for failed messages."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def add(self, entry_id: str, error: str, payload: dict) -> None:
        """Add entry to DLQ."""
        model = DeadLetterModel(
            entry_id=entry_id,
            error=error,
            payload=payload,
            failed_at=datetime.now(timezone.utc),
        )
        self._session.add(model)
    
    async def get_all(self) -> list:
        """Get all DLQ entries."""
        result = await self._session.execute(select(DeadLetterModel))
        return result.scalars().all()