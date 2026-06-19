from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    JSON,
    BigInteger,
    Index
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import synonym
from sqlalchemy.sql import func
from backend.database import Base
import uuid


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    aggregate_id = Column(UUID, nullable=False)
    aggregate_type = Column(String(63), nullable=False)

    event_type = Column(String(63), nullable=False)
    event_version = Column(Integer, default=1)
    version = synonym("event_version")

    # Compatibility synonym for legacy code

    event_hash = Column(String(64), nullable=False)
    aggregate_hash = Column(String(64))
    previous_hash = Column(String(64))

    event_signature = Column(String(512))
    signing_key_id = Column(UUID)

    payload = Column(JSONB)
    event_metadata = Column("metadata", JSONB)

    commit_position = Column(BigInteger, unique=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(UUID)

    tenant_id = Column(UUID, nullable=False)

    # ? FIX: Hanya hybrid_property dengan expression
    @hybrid_property
    def case_id(self):
        return self.aggregate_id

    @case_id.expression
    def case_id(cls):
        return cls.aggregate_id


class Snapshot(Base):
    __tablename__ = "snapshots"
    
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
        self.id = event.id
        self.event_type = event.event_type
        self.payload = event.payload
        self.metadata = getattr(event, 'event_metadata', {})
        self.timestamp = event.created_at
        self.case_id = getattr(event, 'case_id', event.aggregate_id)
        self.aggregate_id = event.aggregate_id
        self.aggregate_type = event.aggregate_type

    #
    @property
    def case_id(self):
        """Compatibility alias for aggregate_id (when aggregate_type='CASE')"""
        return self.aggregate_id if self.aggregate_type == "CASE" else None

