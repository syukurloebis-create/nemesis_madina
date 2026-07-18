"""
NEMESIS Madina - Fraud Analysis Mapper
✅ Maps FraudAnalysis Value Object ↔ JSONB
✅ Stateless, pure functions
"""

from typing import Optional, Sequence, Dict, Any
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.enums.risk_level import RiskLevel


class FraudAnalysisMapper:
    """Fraud Analysis mapper for DDD infrastructure."""

    @staticmethod
    def to_dict(analysis: Optional[FraudAnalysis]) -> Optional[Dict[str, Any]]:
        """Convert domain object to JSONB data."""
        if analysis is None:
            return None
        
        return {
            "case_id": analysis.case_id,
            "patterns": analysis.patterns,
            "overall_risk": analysis.overall_risk.value if hasattr(analysis.overall_risk, 'value') else str(analysis.overall_risk),
            "score": analysis.score,
            "total_patterns": analysis.total_patterns,
            "active_alerts": analysis.active_alerts,
            "high_confidence": analysis.high_confidence,
            "validated_patterns": analysis.validated_patterns,
            "highest_confidence": analysis.highest_confidence,
            "average_confidence": analysis.average_confidence,
        }

    @staticmethod
    def from_dict(data: Optional[Dict[str, Any]]) -> Optional[FraudAnalysis]:
        """Convert JSONB data to domain object."""
        if data is None:
            return None
        
        return FraudAnalysis(
            case_id=data.get("case_id", ""),
            patterns=data.get("patterns", []),
            overall_risk=RiskLevel(data.get("overall_risk", "UNKNOWN")),
            score=float(data.get("score", 0.0)),
            total_patterns=int(data.get("total_patterns", 0)),
            active_alerts=int(data.get("active_alerts", 0)),
            high_confidence=int(data.get("high_confidence", 0)),
            validated_patterns=int(data.get("validated_patterns", 0)),
            highest_confidence=float(data.get("highest_confidence", 0.0)),
            average_confidence=float(data.get("average_confidence", 0.0)),
        )