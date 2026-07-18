# backend/domain/events/risk_events.py
"""
NEMESIS Madina - Risk Domain Events
"""

from dataclasses import dataclass
from typing import Dict, Any
from uuid import UUID

from backend.domain.events.base import DomainEvent
from backend.domain.value_objects.risk_assessment import RiskAssessment
from backend.domain.value_objects.risk_level import RiskLevel
from backend.domain.value_objects.case_id import CaseId


@dataclass(frozen=True)
class RiskPayload:
    """New-style payload for risk events."""
    
    case_id: CaseId
    score: float
    level: str
    anomaly_score: float
    collusion_score: float
    financial_score: float
    status: str = "SUCCESS"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": str(self.case_id),
            "score": self.score,
            "level": self.level,
            "anomaly_score": self.anomaly_score,
            "collusion_score": self.collusion_score,
            "financial_score": self.financial_score,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RiskPayload":
        return cls(
            case_id=CaseId(data["case_id"]),
            score=data["score"],
            level=data["level"],
            anomaly_score=data["anomaly_score"],
            collusion_score=data["collusion_score"],
            financial_score=data["financial_score"],
            status=data.get("status", "SUCCESS"),
        )


# ============================================================================
# NEW-STYLE EVENT (Target Architecture)
# ============================================================================

@dataclass(frozen=True)
class RiskAssessmentCompleted(DomainEvent[RiskPayload]):
    """Event emitted when risk assessment completes."""
    EVENT_NAME = "RiskAssessmentCompleted"
    EVENT_VERSION = "1"


# ============================================================================
# COMPATIBILITY ADAPTER (Plain Class - NOT dataclass)
# ============================================================================

class RiskAssessmentRecorded(RiskAssessmentCompleted):
    """
    Compatibility adapter for old aggregate calls.
    
    Old style: RiskAssessmentRecorded(case_id=..., assessment=...)
    New style: RiskAssessmentCompleted(payload=RiskPayload(...))
    
    ✅ Plain class (not dataclass) - no field ordering issues
    ✅ Inherits from new event
    ✅ Constructor matches old contract
    ✅ Produces valid DomainEvent
    ✅ Temporary - will be removed after migration
    """
    
    def __init__(self, case_id: CaseId, assessment: RiskAssessment):
        # Build payload
        payload = RiskPayload(
            case_id=case_id,
            score=assessment.score,
            level=assessment.level.value if hasattr(assessment.level, 'value') else str(assessment.level),
            anomaly_score=getattr(assessment, 'anomaly_score', 0.0),
            collusion_score=getattr(assessment, 'collusion_score', 0.0),
            financial_score=getattr(assessment, 'financial_score', 0.0),
        )
        # Call parent constructor with payload
        super().__init__(payload=payload)