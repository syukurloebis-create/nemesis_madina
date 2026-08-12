# backend/cases/models.py

from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Boolean,
    Integer,
    CheckConstraint,
    UUID,
    JSON,
    Numeric,
    Index,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from backend.database import Base
import uuid
from enum import Enum


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Case(Base):
    __tablename__ = "cases"

    # Database canonical: UUID PK
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    status = Column(String, nullable=True)
    priority = Column(String, nullable=True)

    assigned_to = Column(UUID(as_uuid=True), nullable=True)
    assigned_at = Column(DateTime, nullable=True)

    institution_id = Column(UUID(as_uuid=True), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), nullable=False)

    created_by = Column(UUID(as_uuid=True), nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)

    is_deleted = Column(Boolean, nullable=False, default=False, server_default="false")
    deleted_at = Column(DateTime, nullable=True)

    # Single version definition
    version = Column(Integer, nullable=False, default=0, server_default="0")

    # Latest analysis snapshots - GIN indexed for JSON queries
    latest_fraud = Column(JSONB, nullable=True)
    latest_risk = Column(JSONB, nullable=True)
    latest_evidence = Column(JSONB, nullable=True)
    latest_graph = Column(JSONB, nullable=True)
    latest_procurement = Column(JSONB, nullable=True)

    workflow_stage = Column(String(50), nullable=True)

    risk_score = Column(Numeric(5, 2), nullable=True)
    risk_level = Column(String(20), nullable=True)

    review_notes = Column(Text, nullable=True)
    review_by = Column(UUID(as_uuid=True), nullable=True)
    review_at = Column(DateTime, nullable=True)

    investigation_started_at = Column(DateTime, nullable=True)
    investigation_completed_at = Column(DateTime, nullable=True)

    # ✅ PATCH: ADDED 2 GIN indexes (preserved existing CheckConstraint)
    __table_args__ = (
        CheckConstraint("version >= 0", name="ck_cases_version_non_negative"),
        Index("idx_cases_latest_fraud", "latest_fraud", postgresql_using="gin"),
        Index("idx_cases_latest_risk", "latest_risk", postgresql_using="gin"),
    )