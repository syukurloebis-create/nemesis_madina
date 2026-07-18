"""
NEMESIS Madina - Intelligence Domain Service
✅ Orchestrates bundle recording
✅ Contains business rules (order, dependencies)
"""

from typing import Optional

from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.value_objects.analysis_bundle import AnalysisBundle
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.risk_assessment import RiskAssessment
from backend.domain.value_objects.evidence_verification import EvidenceVerification
from backend.domain.value_objects.graph_analysis import GraphAnalysis
from backend.domain.value_objects.procurement_analysis import ProcurementAnalysis


class IntelligenceDomainService:
    """
    Domain Service for intelligence operations.
    ✅ Contains business rules (order, dependencies)
    ✅ Records bundle to aggregate
    ✅ Application layer doesn't know aggregation logic
    """
    
    @staticmethod
    def record_bundle(
        aggregate: CaseIntelligenceAggregate,
        bundle: AnalysisBundle,
        *,
        require_fraud_first: bool = True,
    ) -> None:
        """
        Record all analyses in a bundle.
        ✅ Business rules: fraud first (if required), then others
        ✅ Domain Service owns the orchestration logic
        """
        # Rule: Fraud must be recorded first if present
        if require_fraud_first and bundle.fraud:
            aggregate.record_analysis(bundle.fraud)
            
            # Then record others
            if bundle.risk:
                aggregate.record_analysis(bundle.risk)
            if bundle.evidence:
                aggregate.record_analysis(bundle.evidence)
            if bundle.graph:
                aggregate.record_analysis(bundle.graph)
            if bundle.procurement:
                aggregate.record_analysis(bundle.procurement)
        else:
            # Record all in natural order
            if bundle.fraud:
                aggregate.record_analysis(bundle.fraud)
            if bundle.risk:
                aggregate.record_analysis(bundle.risk)
            if bundle.evidence:
                aggregate.record_analysis(bundle.evidence)
            if bundle.graph:
                aggregate.record_analysis(bundle.graph)
            if bundle.procurement:
                aggregate.record_analysis(bundle.procurement)
    
    @staticmethod
    def record_fraud_if_present(
        aggregate: CaseIntelligenceAggregate,
        fraud: Optional[FraudAnalysis],
    ) -> None:
        """Record fraud analysis only if present."""
        if fraud:
            aggregate.record_analysis(fraud)
    
    @staticmethod
    def record_risk_if_present(
        aggregate: CaseIntelligenceAggregate,
        risk: Optional[RiskAssessment],
    ) -> None:
        """Record risk assessment only if present."""
        if risk:
            aggregate.record_analysis(risk)
    
    @staticmethod
    def record_evidence_if_present(
        aggregate: CaseIntelligenceAggregate,
        evidence: Optional[EvidenceVerification],
    ) -> None:
        """Record evidence verification only if present."""
        if evidence:
            aggregate.record_analysis(evidence)
    
    @staticmethod
    def record_graph_if_present(
        aggregate: CaseIntelligenceAggregate,
        graph: Optional[GraphAnalysis],
    ) -> None:
        """Record graph analysis only if present."""
        if graph:
            aggregate.record_analysis(graph)
    
    @staticmethod
    def record_procurement_if_present(
        aggregate: CaseIntelligenceAggregate,
        procurement: Optional[ProcurementAnalysis],
    ) -> None:
        """Record procurement analysis only if present."""
        if procurement:
            aggregate.record_analysis(procurement)