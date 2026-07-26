"""
Case Intelligence Factory — ALL Business Logic.
"""

from typing import List, Sequence
from uuid import uuid4, UUID
from datetime import datetime, timezone
import logging

from backend.core.context import ExecutionContext
from backend.domain.models.case_intelligence import CaseIntelligence
from backend.domain.entities.finding import Finding
from backend.domain.summary_objects import (
    DashboardSummary,
    FraudSummary,
    FraudPatternSummary,
    GraphSummary,
    RiskSummary,
    EvidenceSummary,
    ProcurementSummary,
    RecoverySummary,
)
from backend.infrastructure.parallel_executor import CollectorResultRegistry
from backend.mappers.fraud_mapper import FraudMapper
from backend.mappers.graph_mapper import GraphMapper
from backend.mappers.risk_mapper import RiskMapper
from backend.mappers.evidence_mapper import EvidenceMapper
from backend.mappers.procurement_mapper import ProcurementMapper
from backend.calculators.fraud_score_calculator import FraudScoreCalculator
from backend.calculators.risk_score_calculator import RiskScoreCalculator
from backend.calculators.evidence_score_calculator import EvidenceScoreCalculator
from backend.calculators.config import CalculatorConfig
from backend.services.domain.confidence_calculator import ConfidenceCalculator
from backend.services.domain.status_calculator import StatusCalculator
from backend.dashboard.snapshot import DashboardSnapshot
from backend.presenters.finding_presenter import FindingPresenter

logger = logging.getLogger(__name__)


class CaseIntelligenceFactory:
    """Case Intelligence Factory — ALL Business Logic."""

    def __init__(
        self,
        fraud_mapper: FraudMapper,
        graph_mapper: GraphMapper,
        risk_mapper: RiskMapper,
        evidence_mapper: EvidenceMapper,
        procurement_mapper: ProcurementMapper,
        fraud_calculator: FraudScoreCalculator,
        risk_calculator: RiskScoreCalculator,
        evidence_calculator: EvidenceScoreCalculator,
        config: CalculatorConfig,
        confidence_calculator: ConfidenceCalculator,
        status_calculator: StatusCalculator,
    ):
        self._fraud_mapper = fraud_mapper
        self._graph_mapper = graph_mapper
        self._risk_mapper = risk_mapper
        self._evidence_mapper = evidence_mapper
        self._procurement_mapper = procurement_mapper
        self._fraud_calculator = fraud_calculator
        self._risk_calculator = risk_calculator
        self._evidence_calculator = evidence_calculator
        self._config = config
        self._confidence_calculator = confidence_calculator
        self._status_calculator = status_calculator

    def create_from_results(
        self,
        case_id: UUID,
        results: CollectorResultRegistry,
        context: ExecutionContext,
    ) -> CaseIntelligence:
        """
        Create CaseIntelligence from CollectorResultRegistry.
        """
        # ===== 1. Build summaries =====
        fraud_summary = self._build_fraud(results)
        graph_summary = self._build_graph(results)
        risk_summary = self._build_risk(results)
        evidence_summary = self._build_evidence(results)
        procurement_summary = self._build_procurement(results)

        # ===== 2. Build findings =====
        findings = self._build_findings(
            fraud_summary,
            graph_summary,
            risk_summary,
            evidence_summary,
            procurement_summary,
        )

        # ===== 3. Calculate confidence & status =====
        confidence_result = self._confidence_calculator.calculate(
            fraud_summary,
            graph_summary,
            risk_summary,
            evidence_summary,
            procurement_summary,
        )

        status_result = self._status_calculator.calculate(
            fraud_summary,
            graph_summary,
            risk_summary,
            evidence_summary,
            procurement_summary,
        )

        confidence_score = confidence_result.score
        status_str = status_result.status.value

        return DashboardIntelligenceDTO(
            case_id=case_id,
            fraud=fraud_summary,
            graph=graph_summary,
            risk=risk_summary,
            evidence=evidence_summary,
            procurement=procurement_summary,
            confidence=confidence_score,
            status=status_str,
            generated_at=datetime.now(timezone.utc),
            version=self._version,
        )

        # ===== 4. Serialize findings via Presenter =====
        serialized_findings = FindingPresenter.present_list(findings)

        # ===== 5. Aggregate stats =====
        total = len(findings)
        critical = sum(1 for f in findings if f.severity == "CRITICAL")
        high = sum(1 for f in findings if f.severity == "HIGH")
        medium = sum(1 for f in findings if f.severity == "MEDIUM")

        # ===== 6. Assemble CaseIntelligence =====
        return CaseIntelligence(
            case_id=str(case_id),
            total=total,
            critical=critical,
            high=high,
            medium=medium,
            findings=serialized_findings,  # ← Dict, bukan Finding
            fraud=fraud_summary,
            graph=graph_summary,
            risk=risk_summary,
            evidence=evidence_summary,
            procurement=procurement_summary,
            recovery=RecoverySummary(),
            confidence=confidence_result.score,
            status=status_result.status.value,
            generated_at=datetime.now(timezone.utc),
            request_id=context.request_id,
            trace_id=context.trace_id,
            version=context.version.to_dict() if context.version else None,
        )

    # ==========================================================================
    # BUILDERS — Summary dari Collector Results
    # ==========================================================================

    def _build_fraud(self, results: CollectorResultRegistry) -> FraudSummary:
        dto = results.fraud
        if dto is None:
            dto = self._empty_fraud_dto()
        calc = self._fraud_calculator.calculate(dto, self._config.get_fraud_weights())
        return self._fraud_mapper.to_summary(dto, calc)

    def _build_graph(self, results: CollectorResultRegistry) -> GraphSummary:
        dto = results.graph
        if dto is None:
            return GraphSummary()
        return self._graph_mapper.to_summary(dto)

    def _build_risk(self, results: CollectorResultRegistry) -> RiskSummary:
        dto = results.risk
        if dto is None:
            return RiskSummary()
        calc = self._risk_calculator.calculate(dto, self._config.get_risk_weights())
        return self._risk_mapper.to_summary(dto, calc)

    def _build_evidence(self, results: CollectorResultRegistry) -> EvidenceSummary:
        dto = results.evidence
        if dto is None:
            return EvidenceSummary()
        calc = self._evidence_calculator.calculate(dto, self._config.get_evidence_weights())
        return self._evidence_mapper.to_summary(dto, calc)

    def _build_procurement(self, results: CollectorResultRegistry) -> ProcurementSummary:
        dto = results.procurement
        if dto is None:
            return ProcurementSummary()
        return self._procurement_mapper.to_summary(dto)

    def _empty_fraud_dto(self):
        from backend.dtos.collector_dtos import FraudCollectorDTO
        return FraudCollectorDTO(
            total_patterns=0,
            critical=0,
            high=0,
            medium=0,
            low=0,
            avg_confidence=0,
            highest_confidence=0,
            validated_patterns=0,
            patterns=(),
        )

    # ==========================================================================
    # FINDINGS BUILDER — Dari Summary Objects
    # ==========================================================================

    def _build_findings(
        self,
        fraud: FraudSummary,
        graph: GraphSummary,
        risk: RiskSummary,
        evidence: EvidenceSummary,
        procurement: ProcurementSummary,
    ) -> List[Finding]:
        """Build findings from all summaries."""
        findings: List[Finding] = []

        # Fraud patterns → Findings
        if fraud.patterns:
            findings.extend(self._fraud_to_findings(fraud.patterns))

        # Risk → Findings
        if risk.score > 0:
            findings.extend(self._risk_to_findings(risk))

        # Graph → Findings
        if graph.entities > 0:
            findings.extend(self._graph_to_findings(graph))

        # Evidence → Findings
        if evidence.total > 0:
            findings.extend(self._evidence_to_findings(evidence))

        # Procurement → Findings
        if procurement.packages > 0:
            findings.extend(self._procurement_to_findings(procurement))

        return findings

    # ==========================================================================
    # ENGINE-SPECIFIC FINDINGS CONVERTERS
    # ==========================================================================

    def _fraud_to_findings(
        self,
        patterns: Sequence[FraudPatternSummary],
    ) -> List[Finding]:
        """Convert fraud patterns to findings."""
        findings = []
        for pattern in patterns:
            findings.append(
                Finding(
                    id=str(uuid4()),
                    source="fraud_engine",
                    severity=pattern.severity.value,
                    title=f"Fraud Pattern: {pattern.type}",
                    description=pattern.description or f"Pattern type: {pattern.type}",
                    confidence=pattern.confidence / 100,
                    detected_at=pattern.detected_at,
                    metadata={
                        "pattern_type": pattern.type,
                        "validated": pattern.validated,
                    },
                )
            )
        return findings

    def _risk_to_findings(self, risk: RiskSummary) -> List[Finding]:
        """Convert risk summary to findings."""
        findings = []
        if risk.level and risk.level.value != "unknown":
            findings.append(
                Finding(
                    id=str(uuid4()),
                    source="risk_engine",
                    severity=risk.level.value.upper(),
                    title=f"Risk Level: {risk.level.value.upper()}",
                    description=f"Risk score: {risk.score:.1f}",
                    confidence=risk.score / 100,
                    detected_at=datetime.now(timezone.utc),
                    metadata={
                        "score": risk.score,
                        "anomaly_score": risk.anomaly_score,
                        "collusion_score": risk.collusion_score,
                        "financial_score": risk.financial_score,
                    },
                )
            )
        for rec in risk.recommendations[:3]:
            findings.append(
                Finding(
                    id=str(uuid4()),
                    source="risk_engine",
                    severity="MEDIUM",
                    title="Risk Recommendation",
                    description=rec,
                    confidence=0.5,
                    detected_at=datetime.now(timezone.utc),
                )
            )
        return findings

    def _graph_to_findings(self, graph: GraphSummary) -> List[Finding]:
        """Convert graph summary to findings."""
        findings = []
        if graph.entities > 0:
            findings.append(
                Finding(
                    id=str(uuid4()),
                    source="graph_engine",
                    severity="LOW",
                    title=f"Graph Analysis: {graph.entities} entities, {graph.relationships} relationships",
                    description=f"Network has {graph.entities} entities with {graph.relationships} connections",
                    confidence=0.5,
                    detected_at=datetime.now(timezone.utc),
                    metadata={
                        "entities": graph.entities,
                        "relationships": graph.relationships,
                    },
                )
            )
        return findings

    def _evidence_to_findings(self, evidence: EvidenceSummary) -> List[Finding]:
        """Convert evidence summary to findings."""
        findings = []
        if evidence.total > 0:
            if evidence.rejected > 0:
                severity = "HIGH"
            elif evidence.pending > evidence.verified:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            findings.append(
                Finding(
                    id=str(uuid4()),
                    source="evidence_engine",
                    severity=severity,
                    title=f"Evidence Summary: {evidence.verified}/{evidence.total} verified",
                    description=f"{evidence.verified} verified, {evidence.rejected} rejected, {evidence.pending} pending",
                    confidence=evidence.avg_trust / 100 if evidence.avg_trust > 0 else 0.5,
                    detected_at=datetime.now(timezone.utc),
                    metadata={
                        "total": evidence.total,
                        "verified": evidence.verified,
                        "rejected": evidence.rejected,
                        "pending": evidence.pending,
                        "avg_trust": evidence.avg_trust,
                    },
                )
            )
        return findings

    def _procurement_to_findings(self, procurement: ProcurementSummary) -> List[Finding]:
        """Convert procurement summary to findings."""
        findings = []
        if procurement.packages > 0:
            findings.append(
                Finding(
                    id=str(uuid4()),
                    source="procurement_engine",
                    severity="LOW",
                    title=f"Procurement Summary: {procurement.packages} packages",
                    description=f"{procurement.vendors} vendors, total value {procurement.total_value:,.0f}",
                    confidence=0.5,
                    detected_at=datetime.now(timezone.utc),
                    metadata={
                        "packages": procurement.packages,
                        "vendors": procurement.vendors,
                        "total_value": procurement.total_value,
                        "avg_value": procurement.avg_value,
                    },
                )
            )
        return findings

    def _assemble_case_intelligence(
        self,
        case_id: UUID,
        fraud_summary: FraudSummary,
        graph_summary: GraphSummary,
        risk_summary: RiskSummary,
        evidence_summary: EvidenceSummary,
        procurement_summary: ProcurementSummary,
        context: ExecutionContext,
    ) -> CaseIntelligence:
        """Pure assembly logic — shared by both collector and read model paths.
        
        This is the SINGLE SOURCE OF TRUTH for CaseIntelligence construction.
        """
        # Build findings from summaries
        findings = self._build_findings(
            fraud_summary,
            graph_summary,
            risk_summary,
            evidence_summary,
            procurement_summary,
        )

        # Calculate confidence & status
        confidence_result = self._confidence_calculator.calculate(
            fraud_summary,
            graph_summary,
            risk_summary,
            evidence_summary,
            procurement_summary,
        )

        status_result = self._status_calculator.calculate(
            fraud_summary,
            graph_summary,
            risk_summary,
            evidence_summary,
            procurement_summary,
        )

        # Serialize findings
        serialized_findings = FindingPresenter.present_list(findings)

        # Aggregate stats
        total = len(findings)
        critical = sum(1 for f in findings if f.severity == "CRITICAL")
        high = sum(1 for f in findings if f.severity == "HIGH")
        medium = sum(1 for f in findings if f.severity == "MEDIUM")

        return CaseIntelligence(
            case_id=str(case_id),
            total=total,
            critical=critical,
            high=high,
            medium=medium,
            findings=serialized_findings,
            fraud=fraud_summary,
            graph=graph_summary,
            risk=risk_summary,
            evidence=evidence_summary,
            procurement=procurement_summary,
            recovery=RecoverySummary(),
            confidence=confidence_result.score,
            status=status_result.status.value,
            generated_at=datetime.now(timezone.utc),
            request_id=context.request_id,
            trace_id=context.trace_id,
            version=context.version.to_dict() if context.version else None,
        )

    def create_from_results(
        self,
        case_id: UUID,
        results: CollectorResultRegistry,
        context: ExecutionContext,
    ) -> CaseIntelligence:
        """Create CaseIntelligence from CollectorResultRegistry."""
        # Build summaries from results
        fraud_summary = self._build_fraud(results)
        graph_summary = self._build_graph(results)
        risk_summary = self._build_risk(results)
        evidence_summary = self._build_evidence(results)
        procurement_summary = self._build_procurement(results)

        # Delegate to shared assembly
        return self._assemble_case_intelligence(
            case_id=case_id,
            fraud_summary=fraud_summary,
            graph_summary=graph_summary,
            risk_summary=risk_summary,
            evidence_summary=evidence_summary,
            procurement_summary=procurement_summary,
            context=context,
        )

    def create_from_snapshot(
        self,
        case_id: UUID,
        snapshot: DashboardSnapshot,
        context: ExecutionContext,
    ) -> CaseIntelligence:
        """Create CaseIntelligence from DashboardSnapshot (CQRS read model).
        
        This method extracts summaries from the snapshot and delegates
        to the same assembly logic used by the collector path.
        """
        # Extract summaries from snapshot
        return self._assemble_case_intelligence(
            case_id=case_id,
            fraud_summary=snapshot.fraud_summary,
            graph_summary=snapshot.graph_summary,
            risk_summary=snapshot.risk_summary,
            evidence_summary=snapshot.evidence_summary,
            procurement_summary=snapshot.procurement_summary,
            context=context,
        )