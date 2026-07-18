"""Dashboard Legacy Adapter — ONLY aggregation."""

from backend.domain.summary_objects import DashboardSummary
from backend.calculators.dashboard_status_calculator import DashboardStatusCalculator
from backend.adapters.legacy.fraud_adapter import FraudLegacyAdapter
from backend.adapters.legacy.risk_adapter import RiskLegacyAdapter
from backend.adapters.legacy.graph_adapter import GraphLegacyAdapter
from backend.adapters.legacy.evidence_adapter import EvidenceLegacyAdapter
from backend.adapters.legacy.procurement_adapter import ProcurementLegacyAdapter


class DashboardLegacyAdapter:
    """
    Dashboard Legacy Adapter — ONLY aggregation.
    
    Menggabungkan semua engine adapters dengan cara yang KONSISTEN.
    TIDAK ada pengecualian untuk Fraud.
    """
    
    @staticmethod
    def to_legacy(summary: DashboardSummary) -> dict:
        return {
            "case_id": summary.case_id,
            "fraud": FraudLegacyAdapter.to_legacy(summary.fraud),      # ← KONSISTEN
            "risk": RiskLegacyAdapter.to_legacy(summary.risk),
            "graph": GraphLegacyAdapter.to_legacy(summary.graph),
            "evidence": EvidenceLegacyAdapter.to_legacy(summary.evidence),
            "procurement": ProcurementLegacyAdapter.to_legacy(summary.procurement),
            "recovery": {
                "status": summary.recovery.business_state.value,      # ← Enum → string
                "actions": summary.recovery.actions,
                "engine_status": summary.recovery.engine_status.value,
            },
            "confidence": summary.confidence,
            "status": DashboardStatusCalculator.calculate(summary).value,  # ← Enum → string
            "generated_at": summary.generated_at.isoformat(),
        }