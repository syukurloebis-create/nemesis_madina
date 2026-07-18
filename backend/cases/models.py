from sqlalchemy import (
    Column,
    String,
    DateTime,
    Text,
    Boolean,
    Integer,
    CheckConstraint,
    UUID,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
from enum import Enum
import uuid

from backend.database import Base


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

    # ============================================================
    # EXISTING COLUMNS
    # ============================================================

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    title = Column(
        String,
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    status = Column(
        String,
        default="OPEN"
    )

    priority = Column(
        String,
        default="MEDIUM"
    )

    assigned_to = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    institution_id = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    tenant_id = Column(
        UUID(as_uuid=True),
        nullable=False
    )

    created_by = Column(
        UUID(as_uuid=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now()
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False
    )

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # ============================================================
    # EXISTING RISK COLUMNS (if they exist in current schema)
    # ============================================================
    # Uncomment these if they are already in your database
    # If not, add them in a separate migration first
    #
    # risk_score = Column(Float, nullable=True, default=0.0)
    # risk_level = Column(String, nullable=True, default="LOW")
    # risk_factors = Column(JSONB, nullable=True)

    # ============================================================
    # NEW: DDD REPOSITORY COLUMNS
    # ============================================================

    # Version for optimistic locking
    version = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    # Latest analysis snapshots as JSONB
    latest_fraud = Column(JSONB, nullable=True)
    latest_risk = Column(JSONB, nullable=True)
    latest_evidence = Column(JSONB, nullable=True)
    latest_graph = Column(JSONB, nullable=True)
    latest_procurement = Column(JSONB, nullable=True)

    # ============================================================
    # TABLE CONSTRAINTS
    # ============================================================

    __table_args__ = (
        CheckConstraint(
            "version >= 0",
            name="ck_cases_version_non_negative"
        ),
        # Add other constraints as needed
    )