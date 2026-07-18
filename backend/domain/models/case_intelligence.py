"""
Case Intelligence — Aggregate Root untuk API Response.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any

# ✅ PERBAIKAN: Import dari summary_objects
from backend.domain.summary_objects import (
    FraudSummary,
    GraphSummary,
    RiskSummary,
    EvidenceSummary,
    ProcurementSummary,
    RecoverySummary
)


class CaseIntelligence(BaseModel):
    """
    Case Intelligence — Aggregate Root.

    Dibangun oleh CaseIntelligenceFactory.
    Digunakan sebagai response model FastAPI.
    """

    case_id: str
    total: int = Field(ge=0, default=0)
    critical: int = Field(ge=0, default=0)
    high: int = Field(ge=0, default=0)
    medium: int = Field(ge=0, default=0)
    findings: List[Dict[str, Any]] = Field(default_factory=list)
    fraud: FraudSummary
    graph: GraphSummary
    risk: RiskSummary
    evidence: EvidenceSummary
    procurement: ProcurementSummary
    recovery: RecoverySummary
    confidence: float = Field(ge=0, le=100, default=0)
    status: str = "minimal"
    generated_at: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None
    trace_id: Optional[str] = None
    version: Optional[Dict[str, Any]] = None