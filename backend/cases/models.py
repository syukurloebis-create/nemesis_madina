# backend/cases/models.py

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from enum import Enum
import uuid

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
    Numeric  
)
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
    
    # ============================================
    # EXISTING COLUMNS (UNCHANGED)
    # ============================================
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    assigned_to = Column(UUID, nullable=True)  # UNCHANGED
    institution_id = Column(UUID, nullable=True)  # UNCHANGED
    tenant_id = Column(UUID, nullable=False)
    created_by = Column(UUID, nullable=True)  # UNCHANGED
    created_at = Column(DateTime, nullable=True)  # UNCHANGED
    updated_at = Column(DateTime, nullable=True)  # UNCHANGED
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)  # UNCHANGED
    version = Column(Integer, nullable=False, default=0)
    latest_fraud = Column(JSONB, nullable=True)
    latest_risk = Column(JSONB, nullable=True)
    latest_evidence = Column(JSONB, nullable=True)
    latest_graph = Column(JSONB, nullable=True)
    latest_procurement = Column(JSONB, nullable=True)
    
    # ============================================
    # NEW CANONICAL COLUMNS (Add - Verified by production usage)
    # ============================================
    workflow_stage = Column(String(50), nullable=True)  # ← ADD (Production: dashboard_service, executive, governance, provenance, copilot)
    risk_score = Column(Numeric(5, 2), nullable=True)  # ← ADD (Production: executive, provenance, copilot)
    risk_level = Column(String(20), nullable=True)  # ← ADD (Production: executive, provenance)
    review_notes = Column(Text, nullable=True)  # ← ADD (Production: services)
    review_by = Column(UUID, nullable=True)  # ← ADD (Production: services)
    review_at = Column(DateTime, nullable=True)  # ← ADD (Production: services)
    assigned_at = Column(DateTime, nullable=True)  # ← ADD (Production: services)
    investigation_started_at = Column(DateTime, nullable=True)  # ← ADD (Production: services)
    investigation_completed_at = Column(DateTime, nullable=True)  # ← ADD (Production: services)
    
    # PENDING VERIFICATION (Don't add yet)
    # risk_factors = Column(JSONB, nullable=True)  # ⚠️ Need migration verification

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