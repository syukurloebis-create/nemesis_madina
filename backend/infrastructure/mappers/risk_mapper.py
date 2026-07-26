# backend/infrastructure/mappers/risk_mapper.py
"""
NEMESIS Madina - Risk Assessment Mapper
✅ Maps RiskAssessment Value Object ↔ JSONB
✅ Stateless, pure functions
"""

from typing import Optional, Dict, Any
from backend.domain.value_objects.risk_assessment import RiskAssessment
from backend.domain.enums.risk_level import RiskLevel


class RiskAssessmentMapper:
    """Risk Assessment mapper for DDD infrastructure."""

    @staticmethod
    def to_dict(assessment: Optional[RiskAssessment]) -> Optional[Dict[str, Any]]:
        """Convert domain object to JSONB data."""
        if assessment is None:
            return None

        return {
            "case_id": assessment.case_id,
            "score": assessment.score,
            "level": assessment.level.value,  # ← Convert to string for JSON
            "confidence": assessment.confidence,
            "anomaly_score": assessment.anomaly_score,
            "collusion_score": assessment.collusion_score,
            "financial_score": assessment.financial_score,
            "status": assessment.status,
            "factors": assessment.factors,
        }
        

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> Optional[RiskAssessment]:
        """Convert JSONB data to domain object."""
        if data is None:
            return None
        
        return RiskAssessment(
            case_id=data.get("case_id", ""),
            score=float(data.get("score", 0.0)),
            level=RiskLevel(data.get("level", RiskLevel.UNKNOWN.value)),
            confidence=float(data.get("confidence", 0.0)),
            anomaly_score=float(data.get("anomaly_score", 0.0)),
            collusion_score=float(data.get("collusion_score", 0.0)),
            financial_score=float(data.get("financial_score", 0.0)),
            status=data.get("status", "SUCCESS"),
            factors=data.get("factors", []),
        )