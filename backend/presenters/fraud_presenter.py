"""
Fraud Presenter — Pure Serializer.

Architecture Decision (ADR-020):
- Presenter is PURE SERIALIZER only
- NO business logic
- NO calculations
- NO knowledge of DTO, Calculator, Repository
- ONLY converts FraudSummary → API response

Engine Pipeline Standard:
- All engines (Fraud, Risk, Evidence, Graph, Procurement) follow same pattern
"""

from typing import Dict, Any, List
from backend.domain.summary_objects import FraudSummary, FraudPatternSummary


class FraudPresenter:
    """
    Fraud Presenter — Pure Serializer.
    
    ONLY serializes FraudSummary to API format.
    NO business logic.
    NO calculations.
    """
    
    @staticmethod
    def to_api_response(summary: FraudSummary) -> Dict[str, Any]:
        """
        Serialize FraudSummary to API response format.
        
        Args:
            summary: FraudSummary read model
            
        Returns:
            Dict: API response ready for JSON serialization
        """
        return {
            "overall_risk": summary.overall_risk.value,
            "score": round(summary.score, 2),
            "total_patterns": summary.total_patterns,
            "validated_patterns": summary.validated_patterns,
            "highest_confidence": round(summary.highest_confidence, 2),
            "average_confidence": round(summary.average_confidence, 2),
            "active_alerts": summary.active_alerts,
            "high_confidence": summary.high_confidence,
            "patterns": FraudPresenter._serialize_patterns(summary.patterns),
            "engine": summary.engine,
            "engine_status": summary.engine_status.value,
        }
    
    @staticmethod
    def _serialize_patterns(patterns: List[FraudPatternSummary]) -> List[Dict[str, Any]]:
        """Serialize pattern list."""
        return [
            {
                "type": p.type,
                "severity": p.severity.value,
                "confidence": round(p.confidence, 2),
                "detected_at": p.detected_at.isoformat(),
                "validated": p.validated,
                "description": p.description,
            }
            for p in patterns
        ]