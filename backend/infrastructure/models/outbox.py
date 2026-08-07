"""
Outbox Model — SQLAlchemy ORM
✅ Uses Base from backend.database (single source of truth)
✅ JSONB for PostgreSQL
✅ Index for polling
✅ Unique constraint on event_id
"""

from sqlalchemy import Column, String, DateTime, Integer, Enum as SQLAEnum, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
import enum

from backend.database import Base


class OutboxStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


class OutboxModel(Base):
    __tablename__ = "outbox_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    aggregate_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    event_type = Column(String(255), nullable=False, index=True)
    payload = Column(JSONB, nullable=False)
    status = Column(SQLAEnum(OutboxStatus), nullable=False, default=OutboxStatus.PENDING)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(String, nullable=True)

    __table_args__ = (
        Index("idx_outbox_pending", "status", "created_at"),
        Index("idx_outbox_aggregate", "aggregate_id", "event_type"),
        UniqueConstraint("event_id", name="uq_outbox_event_id"),  # ✅ Idempotency at DB level
    )