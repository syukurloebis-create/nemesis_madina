from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, Text
from sqlalchemy.sql import func
from backend.database import Base
import uuid

class GraphEntity(Base):
    __tablename__ = "graph_entities"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=True)
    institution_id = Column(String, nullable=True)
    entity_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    external_id = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    address = Column(Text, nullable=True)
    attributes = Column(JSON, default=dict)
    extra_data = Column(JSON, default=dict)
    risk_score = Column(Float, default=0.0)
    confidence = Column(Float, default=1.0)
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_seen = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)


class GraphRelationship(Base):
    __tablename__ = "graph_relationships"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    case_id = Column(String, nullable=True)
    institution_id = Column(String, nullable=True)
    source_id = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    amount = Column(Float, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    description = Column(Text, nullable=True)
    extra_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String, nullable=True)


class CollusionDetection(Base):
    __tablename__ = "collusion_detections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String, nullable=False)
    pattern_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    entity_ids = Column(JSON, default=list)
    entity_names = Column(JSON, default=list)
    pattern_key = Column(String(64), nullable=True)
    confidence = Column(Float, default=0.0)
    severity = Column(Float, default=0.0)
    evidence = Column(JSON, default=dict)
    is_reviewed = Column(Integer, default=0)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())

# ============================================================
# ENUMS FOR GRAPH
# ============================================================

from enum import Enum


class NodeType(Enum):
    """Types of nodes in the graph"""
    ENTITY = "entity"
    VENDOR = "vendor"
    OFFICIAL = "official"
    COMPANY = "company"
    PERSON = "person"
    ADDRESS = "address"
    BANK_ACCOUNT = "bank_account"
    PROCUREMENT = "procurement"


class EdgeType(Enum):
    """Types of edges in the graph"""
    INTERACTS = "interacts"
    OWNER = "owner"
    DIRECTOR = "director"
    SHAREHOLDER = "shareholder"
    FAMILY = "family"
    SAME_ADDRESS = "same_address"
    SAME_PHONE = "same_phone"
    SAME_BANK_ACCOUNT = "same_bank_account"
    PROCUREMENT_PARTICIPANT = "procurement_participant"
    CONTRACT_SIGNATORY = "contract_signatory"
    COLLUSION = "collusion"
    FINANCIAL = "financial"
    SHARED_OWNERSHIP = "shared_ownership"
