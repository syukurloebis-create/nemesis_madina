# backend/dashboard/aggregators/intelligence_aggregator.py

from backend.dashboard.snapshot import DashboardSnapshot
from backend.dashboard.builders.dashboard_snapshot_builder import DashboardSnapshotBuilder
from backend.dashboard.policies.scoring_policy import DashboardScoringPolicy
from backend.domain.summary_objects import (
    RiskSummary,
    FraudSummary,
    GraphSummary,
    EvidenceSummary,
    ProcurementSummary
)


class IntelligenceAggregator:
    """
    Pure aggregation layer - NO business rules.

    Responsibilities:
    1. Merge pipeline results
    2. Use ScoringPolicy for business rules
    3. Return immutable DashboardSnapshot

    This is pure composition - no calculations.
    Builder is internal detail.
    """

    def __init__(self, scoring_policy: DashboardScoringPolicy):
        self._scoring_policy = scoring_policy

    def aggregate(
        self,
        risk: RiskSummary,
        fraud: FraudSummary,
        graph: GraphSummary,
        evidence: EvidenceSummary,
        procurement: ProcurementSummary
    ) -> DashboardSnapshot:
        """
        Aggregate all summaries into DashboardSnapshot.

        Uses ScoringPolicy for business rules.
        Builder is used internally.
        """
        builder = DashboardSnapshotBuilder(self._scoring_policy)

        return (
            builder
            .with_risk(risk)
            .with_fraud(fraud)
            .with_graph(graph)
            .with_evidence(evidence)
            .with_procurement(procurement)
            .build()
        )

    def aggregate_from_dict(self, summaries: dict) -> DashboardSnapshot:
        """Aggregate from dictionary of summaries."""
        return self.aggregate(
            risk=summaries.get("risk", RiskSummary.empty()),
            fraud=summaries.get("fraud", FraudSummary.empty()),
            graph=summaries.get("graph", GraphSummary.empty()),
            evidence=summaries.get("evidence", EvidenceSummary.empty()),
            procurement=summaries.get("procurement", ProcurementSummary.empty())
        )

    def empty_snapshot(self) -> DashboardSnapshot:
        """Return empty snapshot when no data available."""
        return DashboardSnapshot.empty()