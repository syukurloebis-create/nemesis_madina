from typing import List
from backend.domain.summary_objects import (
    FraudSummary,
    RiskSummary,
    GraphSummary,
    EvidenceSummary,
    DashboardSummary,
)
from backend.finding.models import Finding
from backend.domain.enums import Severity


class FindingFactory:
    """
    Finding Factory — Converts Summary Objects to Findings.
    
    SINGLE RESPONSIBILITY: Only creates Finding entities from summaries.
    """

    @staticmethod
    def create_all(summaries: DashboardSummary) -> List[Finding]:
        """Create all findings from dashboard summaries."""
        findings = []

        # Fraud patterns → Findings
        if summaries.fraud.patterns:
            findings.extend(
                FindingFactory._from_fraud(summaries.fraud)
            )

        # Risk → Findings
        if summaries.risk.score > 0:
            findings.extend(
                FindingFactory._from_risk(summaries.risk)
            )

        # Graph → Findings
        if summaries.graph.entities > 0:
            findings.extend(
                FindingFactory._from_graph(summaries.graph)
            )

        # Evidence → Findings (if any verification issues)
        if summaries.evidence.rejected > 0 or summaries.evidence.pending > 0:
            findings.extend(
                FindingFactory._from_evidence(summaries.evidence)
            )

        return findings

    @staticmethod
    def _from_fraud(fraud: FraudSummary) -> List[Finding]:
        """Convert fraud patterns to findings."""
        findings = []
        for pattern in fraud.patterns:
            findings.append(
                Finding(
                    title=f"Fraud Pattern Detected: {pattern.type}",
                    description=pattern.description or f"Pattern type: {pattern.type}",
                    severity=pattern.severity,
                    confidence=pattern.confidence,
                    source="fraud_engine",
                    metadata={
                        "pattern_type": pattern.type,
                        "detected_at": pattern.detected_at.isoformat(),
                        "validated": pattern.validated,
                    },
                )
            )
        return findings

    @staticmethod
    def _from_risk(risk: RiskSummary) -> List[Finding]:
        """Convert risk summary to findings."""
        findings = []

        if risk.score >= 80:
            findings.append(
                Finding(
                    title="Critical Risk Level Detected",
                    description=f"Risk score: {risk.score:.1f} (CRITICAL)",
                    severity=Severity.CRITICAL,
                    confidence=risk.score,
                    source="risk_engine",
                    metadata={
                        "anomaly_score": risk.anomaly_score,
                        "collusion_score": risk.collusion_score,
                        "financial_score": risk.financial_score,
                    },
                )
            )
        elif risk.score >= 60:
            findings.append(
                Finding(
                    title="High Risk Level Detected",
                    description=f"Risk score: {risk.score:.1f} (HIGH)",
                    severity=Severity.HIGH,
                    confidence=risk.score,
                    source="risk_engine",
                )
            )

        return findings

    @staticmethod
    def _from_graph(graph: GraphSummary) -> List[Finding]:
        """Convert graph summary to findings."""
        findings = []
        if graph.relationships > graph.entities * 2:
            findings.append(
                Finding(
                    title="Dense Network Detected",
                    description=f"Entities: {graph.entities}, Relationships: {graph.relationships}",
                    severity=Severity.MEDIUM,
                    confidence=70.0,
                    source="graph_engine",
                )
            )
        return findings

    @staticmethod
    def _from_evidence(evidence: EvidenceSummary) -> List[Finding]:
        """Convert evidence summary to findings."""
        findings = []
        if evidence.rejected > 0:
            findings.append(
                Finding(
                    title="Rejected Evidence",
                    description=f"{evidence.rejected} evidence items rejected",
                    severity=Severity.HIGH,
                    confidence=evidence.score,
                    source="evidence_engine",
                )
            )
        if evidence.pending > 0:
            findings.append(
                Finding(
                    title="Pending Evidence",
                    description=f"{evidence.pending} evidence items pending verification",
                    severity=Severity.MEDIUM,
                    confidence=evidence.score,
                    source="evidence_engine",
                )
            )
        return findings