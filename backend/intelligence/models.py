"""
SQLAlchemy Models for Intelligence Layer
"""

from sqlalchemy import (
    Column, String, Integer, Float, DateTime, JSON, Text,
    Enum, ForeignKey, Index, Boolean
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
import enum
import uuid

from backend.database import Base


class RiskLevel(str, enum.Enum):
    """Risk level classification"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class DetectionType(str, enum.Enum):
    """Type of anomaly detection"""
    STATISTICAL = "statistical"
    GRAPH = "graph"
    ML = "ml"
    RULE = "rule"
    TEMPORAL = "temporal"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class AlertStatus(str, enum.Enum):
    """Alert lifecycle status"""
    PENDING = "pending"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class RiskScore(Base):
    """Risk score for a case or entity"""
    
    __tablename__ = "risk_scores"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_id = Column(String, nullable=True, index=True)  # Person, company, account
    entity_type = Column(String, nullable=True)  # person, company, account
    
    # Risk metrics
    overall_score = Column(Float, nullable=False)  # 0-100
    risk_level = Column(Enum(RiskLevel), nullable=False)
    
    # Component scores
    anomaly_score = Column(Float, default=0.0)
    collusion_score = Column(Float, default=0.0)
    financial_score = Column(Float, default=0.0)
    temporal_score = Column(Float, default=0.0)
    
    # Explanation
    factors = Column(JSON, default=list)  # List of contributing factors
    recommendations = Column(JSON, default=list)  # Actionable recommendations
    
    # Metadata
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)
    calculated_by = Column(String, nullable=True)  # system/user
    
    __table_args__ = (
        Index("idx_risk_case_score", "case_id", "overall_score"),
        Index("idx_risk_entity", "entity_id", "entity_type"),
    )


class AnomalyDetection(Base):
    """Record of detected anomalies"""
    
    __tablename__ = "anomaly_detections"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    event_id = Column(Integer, nullable=True)  # Related event if any
    
    detection_type = Column(Enum(DetectionType), nullable=False)
    anomaly_type = Column(String, nullable=False)  # e.g., "unusual_amount", "suspicious_pattern"
    
    # Detection details
    confidence = Column(Float, default=0.0)  # 0-1 confidence
    severity = Column(Float, default=0.0)  # 0-1 severity
    
    # Data
    observed_value = Column(JSON, nullable=True)
    expected_value = Column(JSON, nullable=True)
    deviation = Column(Float, nullable=True)
    
    # Explanation
    reason = Column(Text, nullable=True)
    evidence = Column(JSON, default=list)
    
    # Status
    is_reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        Index("idx_anomaly_case_type", "case_id", "detection_type"),
        Index("idx_anomaly_severity", "severity"),
    )


class Alert(Base):
    """Alerts generated from intelligence analysis"""
    
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    anomaly_id = Column(String, ForeignKey("anomaly_detections.id"), nullable=True)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(Enum(AlertSeverity), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING)
    
    # Alert details
    alert_type = Column(String, nullable=False)  # e.g., "fraud_alert", "risk_escalation"
    triggered_by = Column(String, nullable=True)  # Rule name or detector
    
    # Action tracking
    assigned_to = Column(String, nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_note = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_alert_case_status", "case_id", "status"),
        Index("idx_alert_severity_status", "severity", "status"),
    )


class IntelligenceReport(Base):
    """Intelligence reports and summaries"""
    
    __tablename__ = "intelligence_reports"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    report_type = Column(String, nullable=False)  # risk_summary, timeline, network
    title = Column(String, nullable=False)
    content = Column(JSON, nullable=False)  # Structured report data
    
    # Report metadata
    generated_by = Column(String, nullable=True)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    version = Column(Integer, default=1)
    
    # Sharing
    is_shared = Column(Boolean, default=False)
    shared_with = Column(JSON, default=list)  # List of institution IDs
    
    __table_args__ = (
        Index("idx_report_case_type", "case_id", "report_type"),
    )