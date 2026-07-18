"""Procurement Legacy Adapter — ONLY compatibility."""

from backend.domain.summary_objects import ProcurementSummary
from backend.adapters.legacy.base_adapter import BaseLegacyAdapter


class ProcurementLegacyAdapter(BaseLegacyAdapter):
    """Convert ProcurementSummary to legacy API format."""
    
    @staticmethod
    def to_legacy(summary: ProcurementSummary) -> dict:
        return {
            "packages": summary.packages,
            "vendors": summary.vendors,
            "instansi_count": summary.instansi_count,
            "total_value": summary.total_value,
            "avg_value": summary.avg_value,
            "completed": summary.completed,
            "status": ProcurementLegacyAdapter.to_legacy_status(summary.engine_status),
            "engine": summary.engine,
            "engine_status": summary.engine_status.value,
        }