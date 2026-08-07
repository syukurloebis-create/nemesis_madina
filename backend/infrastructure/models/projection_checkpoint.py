"""
NEMESIS Madina - Projection Checkpoint
✅ Persistent processed events table
✅ Idempotent across restarts
"""

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Integer,
    UniqueConstraint,
    select,
)
from sqlalchemy.dialects.postgresql import UUID
from backend.database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import uuid


class ProcessedEvent(Base):
    """Track processed events for idempotency."""
    __tablename__ = "processed_events"
    __table_args__ = (
        UniqueConstraint("event_id", "projection_name", name="uq_processed_event"),
    )
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(String(255), nullable=False)
    projection_name = Column(String(100), nullable=False)
    aggregate_id = Column(String(255), nullable=True)
    event_sequence = Column(Integer, nullable=True)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class ProjectionCheckpointModel(Base):
    """
    Persistent projection checkpoint ORM model.

    Stores last processed event sequence for projection rebuild resume.
    Used by ProjectionRebuilder for atomic checkpoint updates.
    """
    __tablename__ = "projection_checkpoints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    projection_name = Column(String(100), nullable=False, unique=True, index=True)
    last_sequence = Column(Integer, nullable=False, default=0)
    total_processed = Column(Integer, nullable=False, default=0)
    total_failed = Column(Integer, nullable=False, default=0)
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    ) 
   
    def __init__(self, session: AsyncSession, projection_name: str):
        self._session = session
        self._projection_name = projection_name
        self._processed_events = set()
    
    async def load_checkpoint(self) -> None:
        """Load processed events from database."""
        result = await self._session.execute(
            select(ProcessedEvent.event_id)
            .where(ProcessedEvent.projection_name == self._projection_name)
        )
        self._processed_events = {row[0] for row in result}
    
    async def is_processed(self, event_id: str) -> bool:
        """Check if event already processed."""
        if event_id in self._processed_events:
            return True
        
        # Double-check database
        result = await self._session.execute(
            select(ProcessedEvent)
            .where(ProcessedEvent.event_id == event_id)
            .where(ProcessedEvent.projection_name == self._projection_name)
        )
        if result.scalar_one_or_none():
            self._processed_events.add(event_id)
            return True
        return False
    
    async def mark_processed(self, event_id: str, aggregate_id: str = None, sequence: int = None) -> None:
        """Mark event as processed."""
        model = ProcessedEvent(
            event_id=event_id,
            projection_name=self._projection_name,
            aggregate_id=aggregate_id,
            event_sequence=sequence,
        )
        self._session.add(model)
        self._processed_events.add(event_id)