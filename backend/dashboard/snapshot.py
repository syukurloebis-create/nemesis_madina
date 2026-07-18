# backend/dashboard/snapshot.py

from dataclasses import dataclass
from backend.domain.summary_objects import (
    RiskSummary,
    FraudSummary,
    GraphSummary,
    EvidenceSummary,
    ProcurementSummary
)
from backend.dashboard.status import DashboardStatus


@dataclass(frozen=True, slots=True)
class DashboardSnapshot:
    """
    Application Read Model - NOT a Domain Entity.

    This is a projection for dashboard presentation.
    Domain entities are RiskSummary, FraudSummary, etc.

    Immutable, thread-safe, cacheable.
    """

    risk_summary: RiskSummary
    fraud_summary: FraudSummary
    graph_summary: GraphSummary
    evidence_summary: EvidenceSummary
    procurement_summary: ProcurementSummary

    # Derived from ScoringPolicy
    total_risk_score: float = 0.0
    overall_status: DashboardStatus = DashboardStatus.UNKNOWN
    has_data: bool = False

    @classmethod
    def empty(cls) -> "DashboardSnapshot":
        """Return empty snapshot when no data available."""
        return cls(
            risk_summary=RiskSummary.empty(),
            fraud_summary=FraudSummary.empty(),
            graph_summary=GraphSummary.empty(),
            evidence_summary=EvidenceSummary.empty(),
            procurement_summary=ProcurementSummary.empty(),
            total_risk_score=0.0,
            overall_status=DashboardStatus.EMPTY,
            has_data=False
        )

    def is_available(self) -> bool:
        """Check if snapshot has usable data."""
        return self.overall_status in (DashboardStatus.OK, DashboardStatus.PARTIAL)