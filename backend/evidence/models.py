# backend/evidence/models.py

from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Float, JSON 
from sqlalchemy.sql import func
from backend.database import Base
import enum
import uuid

class EvidenceStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    VERIFIED = "verified"
    ANALYZED = "analyzed"
    SUBMITTED = "submitted"
    REJECTED = "rejected"


class Evidence(Base):
    __tablename__ = "evidence"
    
    # ============================================
    # EXISTING COLUMNS (UNCHANGED)
    # ============================================
    id = Column(String, primary_key=True)
    case_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=True)
    status = Column(String, nullable=True)
    confidence_score = Column(Float, nullable=False)
    verified_at = Column(DateTime, nullable=True)
    uploaded_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    # ORM Extensions (Documented)
    file_path = Column(String, nullable=False)  # ⚠️ ORM Extension - Verify DB presence
    mime_type = Column(String, nullable=True)  # ⚠️ ORM Extension - Verify DB presence
    description = Column(Text, nullable=True)  # ⚠️ ORM Extension - Verify DB presence
    verified_by = Column(String, nullable=True)  # ⚠️ ORM Extension - Verify DB presence
    user_id = Column(String, nullable=False)  # ⚠️ ORM Extension - Verify DB presence
    institution_id = Column(String, nullable=False)  # ⚠️ ORM Extension - Verify DB presence
    created_by = Column(String, nullable=False)  # ⚠️ ORM Extension - Verify DB presence
    created_at = Column(DateTime, nullable=True)  # ⚠️ ORM Extension - Verify DB presence
    
    # ============================================
    # NEW PRODUCTION CONTRACT COLUMNS (Pending Provenance)
    # ============================================
    # These columns exist in Production DB and are actively used.
    # They have NO migration provenance (created outside Alembic).
    # Status: Production Contract (Pending)
    trust_score = Column(Float, nullable=True)  # ← ADD (Production: 50+ occurrences)
    file_type = Column(String, nullable=True)  # ← ADD (Production: 10+ occurrences)
    file_size = Column(Integer, nullable=True)  # ← ADD (Production: verification, export)


class ChainOfCustody(Base):
    __tablename__ = "chain_of_custody"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, nullable=False)  # Tanpa foreign key
    action = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    institution_id = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class Finding(Base):
    __tablename__ = "findings"
    
    # ============================================
    # EXISTING COLUMNS (UNCHANGED)
    # ============================================
    id = Column(String, primary_key=True)
    case_id = Column(String, nullable=True)
    finding_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    severity = Column(String, nullable=False)
    confidence = Column(Float, nullable=True)
    anomaly_score = Column(Float, nullable=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    created_by = Column(String, nullable=True)
    evidence_ids = Column(JSON, nullable=True)
    
    # ============================================
    # CANONICAL COLUMNS (Migration Provenance)
    # ============================================
    fingerprint = Column(String(64), nullable=True)  # Migration: 4cc8a0a5030b
    detection_method = Column(String, nullable=True)  # Migration: 4cc8a0a5030b
    
    # ============================================
    # NEW CANONICAL COLUMN (Migration Provenance) ← ADD
    # ============================================
    # Migration: 7e9dcf0e5a5d_add_intelligence_graph_schema.py
    # Runtime: Multiple services, routers, audit, investigation
    # Status: Canonical Contract
    title = Column(String, nullable=False)  # ← ADD
    
    # ============================================
    # PRODUCTION CONTRACT COLUMNS (Pending Provenance)
    # ============================================
    status = Column(String, nullable=True)  # ENUM in DB - normalization deferred to E2.2
    anomaly_details = Column(JSON, nullable=True)
    financial_loss = Column(Float, nullable=True)
    risk_score = Column(Float, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    escalated_to = Column(String, nullable=True)
    escalated_at = Column(DateTime, nullable=True)
    institution_id = Column(String, nullable=True)
