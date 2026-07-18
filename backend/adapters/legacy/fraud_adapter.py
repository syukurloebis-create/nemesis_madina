"""Fraud Legacy Adapter — ONLY compatibility."""

from backend.domain.summary_objects import FraudSummary
from backend.adapters.legacy.base_adapter import BaseLegacyAdapter
from backend.mappers.status_mapper import StatusMapper


class FraudLegacyAdapter(BaseLegacyAdapter):
    """Convert FraudSummary to legacy API format."""
    
    @staticmethod
    def to_legacy(summary: FraudSummary) -> dict:
        return {
            "overall_risk": summary.overall_risk.value,
            "score": summary.score,
            "total_patterns": summary.total_patterns,
            "validated_patterns": summary.validated_patterns,
            "highest_confidence": summary.highest_confidence,
            "average_confidence": summary.average_confidence,
            "active_alerts": summary.active_alerts,
            "high_confidence": summary.high_confidence,
            "patterns": [
                {
                    "type": p.type,
                    "severity": p.severity.value,
                    "confidence": p.confidence,
                    "detected_at": p.detected_at.isoformat(),
                    "validated": p.validated,
                    "description": p.description,
                }
                for p in summary.patterns
            ],
            "status": StatusMapper.to_legacy(summary.engine_status),
            "engine": summary.engine,
            "engine_status": summary.engine_status.value,
        }