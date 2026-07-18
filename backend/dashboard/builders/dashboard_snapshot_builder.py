# backend/dashboard/builders/dashboard_snapshot_builder.py

from backend.dashboard.snapshot import DashboardSnapshot
from backend.dashboard.policies.scoring_policy import DashboardScoringPolicy
from backend.domain.summary_objects import (
    RiskSummary,
    FraudSummary,
    GraphSummary,
    EvidenceSummary,
    ProcurementSummary
)


class DashboardSnapshotBuilder:
    """
    Immutable Builder for DashboardSnapshot.

    Each with_xxx() returns a new builder instance.
    Thread-safe and easy to test.
    """

    def __init__(
        self,
        scoring_policy: DashboardScoringPolicy,
        risk: RiskSummary | None = None,
        fraud: FraudSummary | None = None,
        graph: GraphSummary | None = None,
        evidence: EvidenceSummary | None = None,
        procurement: ProcurementSummary | None = None
    ):
        self._scoring_policy = scoring_policy
        self._risk = risk
        self._fraud = fraud
        self._graph = graph
        self._evidence = evidence
        self._procurement = procurement

    def with_risk(self, risk: RiskSummary) -> "DashboardSnapshotBuilder":
        """Add risk summary."""
        return DashboardSnapshotBuilder(
            scoring_policy=self._scoring_policy,
            risk=risk,
            fraud=self._fraud,
            graph=self._graph,
            evidence=self._evidence,
            procurement=self._procurement
        )

    def with_fraud(self, fraud: FraudSummary) -> "DashboardSnapshotBuilder":
        """Add fraud summary."""
        return DashboardSnapshotBuilder(
            scoring_policy=self._scoring_policy,
            risk=self._risk,
            fraud=fraud,
            graph=self._graph,
            evidence=self._evidence,
            procurement=self._procurement
        )

    def with_graph(self, graph: GraphSummary) -> "DashboardSnapshotBuilder":
        """Add graph summary."""
        return DashboardSnapshotBuilder(
            scoring_policy=self._scoring_policy,
            risk=self._risk,
            fraud=self._fraud,
            graph=graph,
            evidence=self._evidence,
            procurement=self._procurement
        )

    def with_evidence(self, evidence: EvidenceSummary) -> "DashboardSnapshotBuilder":
        """Add evidence summary."""
        return DashboardSnapshotBuilder(
            scoring_policy=self._scoring_policy,
            risk=self._risk,
            fraud=self._fraud,
            graph=self._graph,
            evidence=evidence,
            procurement=self._procurement
        )

    def with_procurement(self, procurement: ProcurementSummary) -> "DashboardSnapshotBuilder":
        """Add procurement summary."""
        return DashboardSnapshotBuilder(
            scoring_policy=self._scoring_policy,
            risk=self._risk,
            fraud=self._fraud,
            graph=self._graph,
            evidence=self._evidence,
            procurement=procurement
        )

    def build(self) -> DashboardSnapshot:
        """Build the final DashboardSnapshot."""
        # Use empty summaries for missing data
        risk = self._risk or RiskSummary.empty()
        fraud = self._fraud or FraudSummary.empty()
        graph = self._graph or GraphSummary.empty()
        evidence = self._evidence or EvidenceSummary.empty()
        procurement = self._procurement or ProcurementSummary.empty()

        # Calculate using policy
        total_risk_score = self._scoring_policy.calculate_total_risk(
            risk, fraud, evidence, graph
        )

        overall_status = self._scoring_policy.determine_overall_status([
            risk, fraud, graph, evidence, procurement
        ])

        has_data = self._scoring_policy.has_any_data([
            risk, fraud, graph, evidence, procurement
        ])

        return DashboardSnapshot(
            risk_summary=risk,
            fraud_summary=fraud,
            graph_summary=graph,
            evidence_summary=evidence,
            procurement_summary=procurement,
            total_risk_score=total_risk_score,
            overall_status=overall_status,
            has_data=has_data
        )