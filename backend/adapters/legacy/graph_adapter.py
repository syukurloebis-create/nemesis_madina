"""Graph Legacy Adapter — ONLY compatibility."""

from backend.domain.summary_objects import GraphSummary
from backend.adapters.legacy.base_adapter import BaseLegacyAdapter


class GraphLegacyAdapter(BaseLegacyAdapter):
    """Convert GraphSummary to legacy API format."""
    
    @staticmethod
    def to_legacy(summary: GraphSummary) -> dict:
        return {
            "entities": summary.entities,
            "relationships": summary.relationships,
            "status": GraphLegacyAdapter.to_legacy_status(summary.engine_status),
            "engine": summary.engine,
            "engine_status": summary.engine_status.value,
        }