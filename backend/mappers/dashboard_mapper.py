"""
Dashboard Mapper — Agregasi semua summary.
"""

from typing import Dict, Any
from uuid import UUID

from backend.domain.summary_objects import (  # ← PERBAIKAN
    DashboardSummary,
    FraudSummary,
    GraphSummary,
    RiskSummary,
    EvidenceSummary,
    ProcurementSummary,
    RecoverySummary
)
from backend.domain.enums import EngineType, EngineStatus


class DashboardMapper:
    """
    Dashboard Mapper — Agregasi semua summary.
    """

    @staticmethod
    def to_dashboard_summary(
        case_id: str,
        fraud: FraudSummary,
        graph: GraphSummary,
        risk: RiskSummary,
        evidence: EvidenceSummary,
        procurement: ProcurementSummary,
        recovery: RecoverySummary,
        confidence: float = 0.0,
        status: str = "minimal"
    ) -> DashboardSummary:
        """Agregasi semua summary menjadi DashboardSummary."""
        return DashboardSummary(
            case_id=case_id,
            fraud=fraud,
            graph=graph,
            risk=risk,
            evidence=evidence,
            procurement=procurement,
            recovery=recovery,
            confidence=confidence,
            status=status
        )