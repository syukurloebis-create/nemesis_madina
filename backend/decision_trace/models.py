"""Decision Trace Models - Sesuai dengan schema PostgreSQL"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field


class DecisionType(str, Enum):
    RISK_SCORE = "risk_score"
    TRUST_SCORE = "trust_score"
    ANOMALY_DETECTION = "anomaly_detection"
    COLLUSION_DETECTION = "collusion_detection"
    RECOMMENDATION = "recommendation"


class DecisionTrace(BaseModel):
    """Decision trace - sesuai schema PostgreSQL"""
    trace_id: UUID = Field(default_factory=uuid4)
    entity_id: str
    entity_type: Optional[str] = None
    decision_type: DecisionType
    score: Optional[float] = None
    reasons: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_ids: List[UUID] = Field(default_factory=list)
    lineage_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionTraceCreate(BaseModel):
    """Request untuk membuat decision trace"""
    entity_id: str
    entity_type: Optional[str] = None
    decision_type: DecisionType
    score: Optional[float] = None
    reasons: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_ids: List[UUID] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ExplainabilityResult(BaseModel):
    """Hasil explainability untuk audit"""
    trace_id: UUID
    entity_id: str
    decision_type: DecisionType
    score: float
    explanations: List[Dict[str, Any]]
    evidence_count: int
    created_at: datetime
