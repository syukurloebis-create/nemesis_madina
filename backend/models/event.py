# backend/models/event.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    BigInteger,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class Event(Base):
    __tablename__ = "events"

    # Database canonical: UUID PK
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    aggregate_id = Column(UUID, nullable=False)
    aggregate_type = Column(String(63), nullable=False)
    event_type = Column(String(63), nullable=False)
    event_version = Column(Integer, default=1)
    version = synonym("event_version")

    event_hash = Column(String(64), nullable=False)
    aggregate_hash = Column(String(64))
    previous_hash = Column(String(64))

    event_signature = Column(String(512))
    signing_key_id = Column(UUID)

    payload = Column(JSONB)
    event_metadata = Column("metadata", JSONB)  # Avoid Python metadata conflict

    commit_position = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(UUID)

    tenant_id = Column(UUID, nullable=False)

    # ✅ PATCH: ADDED canonical indexes and UniqueConstraint
    __table_args__ = (
        UniqueConstraint("commit_position", name="events_commit_position_key"),
        Index("idx_events_aggregate", "aggregate_id", "created_at"),
        Index("idx_events_commit", "commit_position"),
        Index("idx_events_tenant", "tenant_id"),
        Index("idx_events_type", "event_type"),
    )

    @hybrid_property
    def case_id(self):
        return self.aggregate_id

    @case_id.expression
    def case_id(cls):
        return cls.aggregate_id


class Snapshot(Base):
    __tablename__ = "snapshots"

    # 🟡 UNVERIFIED - PRESERVED AS-IS
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    aggregate_id = Column(UUID, nullable=False)
    aggregate_type = Column(String(63), nullable=False)
    snapshot_version = Column(Integer, nullable=False)
    snapshot_data = Column(JSON, nullable=False)

    created_at = Column(DateTime, default=func.now())
    created_by = Column(UUID)
    tenant_id = Column(UUID, nullable=False)

    __table_args__ = (
        Index("idx_snapshots_aggregate", "aggregate_id", "snapshot_version"),
        Index("idx_snapshots_tenant", "tenant_id"),
    )


class EventEnvelope:
    """Compatibility wrapper for legacy event structure"""
    def __init__(self, event):
        self.event = event
        self._id = event.id
        self._event_type = event.event_type
        self._payload = event.payload
        self._metadata = getattr(event, 'event_metadata', {})
        self._timestamp = event.created_at
        self._aggregate_id = event.aggregate_id
        self._aggregate_type = event.aggregate_type

    @property
    def id(self):
        return self._id

    @property
    def event_type(self):
        return self._event_type

    @property
    def payload(self):
        return self._payload

    @property
    def metadata(self):
        return self._metadata

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def aggregate_id(self):
        return self._aggregate_id

    @property
    def aggregate_type(self):
        return self._aggregate_type

    @property
    def case_id(self):
        """Compatibility alias for aggregate_id (when aggregate_type='CASE')"""
        return self._aggregate_id if self._aggregate_type == "CASE" else None