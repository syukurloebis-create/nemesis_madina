"""Risk Legacy Adapter — ONLY compatibility."""

from backend.domain.summary_objects import RiskSummary
from backend.adapters.legacy.base_adapter import BaseLegacyAdapter


class RiskLegacyAdapter(BaseLegacyAdapter):
    """Convert RiskSummary to legacy API format."""
    
    @staticmethod
    def to_legacy(summary: RiskSummary) -> dict:
        return {
            "score": summary.score,
            "level": summary.level.value,
            "status": RiskLegacyAdapter.to_legacy_status(summary.engine_status),
            "anomaly_score": summary.anomaly_score,
            "collusion_score": summary.collusion_score,
            "financial_score": summary.financial_score,
            "recommendations": summary.recommendations,
            "engine": summary.engine,
            "engine_status": summary.engine_status.value,
        }