# backend/infrastructure/models/read_models.py
"""
NEMESIS Madina - Read Models for CQRS
✅ Materialized views for read side
✅ Separate from write models
"""

from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class DashboardView(Base):
    """Dashboard materialized view for read side."""
    
    __tablename__ = "dashboard_view"
    
    # Primary key
    case_id = Column(String, primary_key=True)
    
    # Status
    status = Column(String, nullable=False, default="active")
    
    # Scores
    fraud_score = Column(Float, default=0.0)
    risk_score = Column(Float, default=0.0)
    risk_level = Column(String, default="unknown")
    confidence = Column(Float, default=0.0)
    
    # Counts
    analysis_count = Column(Integer, default=0)
    evidence_count = Column(Integer, default=0)
    total_events = Column(Integer, default=0)
    avg_confidence = Column(Float, default=0.0)
    
    # Latest analysis data (JSON)
    latest_fraud = Column(JSON, nullable=True)
    latest_risk = Column(JSON, nullable=True)
    latest_graph = Column(JSON, nullable=True)
    latest_evidence = Column(JSON, nullable=True)
    latest_procurement = Column(JSON, nullable=True)
    
    # Metadata
    last_updated = Column(DateTime, nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)