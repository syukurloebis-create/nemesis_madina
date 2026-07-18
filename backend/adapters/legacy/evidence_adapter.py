"""Evidence Legacy Adapter — ONLY compatibility."""

from backend.domain.summary_objects import EvidenceSummary
from backend.adapters.legacy.base_adapter import BaseLegacyAdapter


class EvidenceLegacyAdapter(BaseLegacyAdapter):
    """Convert EvidenceSummary to legacy API format."""
    
    @staticmethod
    def to_legacy(summary: EvidenceSummary) -> dict:
        return {
            "score": summary.score,
            "level": summary.level.value,
            "total": summary.total,
            "verified": summary.verified,
            "rejected": summary.rejected,
            "pending": summary.pending,
            "avg_trust": summary.avg_trust,
            "avg_confidence": summary.avg_confidence,
            "status": EvidenceLegacyAdapter.to_legacy_status(summary.engine_status),
            "engine": summary.engine,
            "engine_status": summary.engine_status.value,
        }