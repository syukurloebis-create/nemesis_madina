"""
NEMESIS Madina - Case Intelligence Aggregate
✅ Explicit dispatch table (not singledispatchmethod)
✅ IDE-friendly, refactoring-safe
✅ Extensible via registration
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable, Type
from functools import wraps

from backend.domain.aggregates.base import AggregateRoot
from backend.domain.value_objects.case_id import CaseId
from backend.domain.value_objects.fraud_analysis import FraudAnalysis
from backend.domain.value_objects.risk_assessment import RiskAssessment
from backend.domain.value_objects.evidence_verification import EvidenceVerification
from backend.domain.value_objects.graph_analysis import GraphAnalysis
from backend.domain.value_objects.procurement_analysis import ProcurementAnalysis
from backend.domain.value_objects.analysis_bundle import AnalysisBundle
from backend.domain.events.fraud_events import FraudAnalysisRecorded
from backend.domain.events.risk_events import RiskAssessmentRecorded
from backend.domain.events.evidence_events import EvidenceVerified
from backend.domain.events.graph_events import GraphAnalysisPerformed
from backend.domain.events.procurement_events import ProcurementAnalysisPerformed


# Analysis type keys (strings for flexibility, not Enum)
ANALYSIS_TYPE_FRAUD = "fraud"
ANALYSIS_TYPE_RISK = "risk"
ANALYSIS_TYPE_EVIDENCE = "evidence"
ANALYSIS_TYPE_GRAPH = "graph"
ANALYSIS_TYPE_PROCUREMENT = "procurement"


@dataclass
class CaseIntelligenceAggregate(AggregateRoot):
    """
    Case Intelligence Aggregate.
    ✅ Explicit dispatch table
    ✅ String keys for flexibility
    ✅ Extensible via registration
    """
    
    case_id: CaseId
    _latest_results: Dict[str, Any] = field(default_factory=dict)
    
    # ✅ Explicit dispatch table - IDE-friendly, refactoring-safe
    _handlers: Dict[Type, Callable] = field(init=False, repr=False, default_factory=dict)
    
    def __post_init__(self):
        # Build dispatch table explicitly
        self._handlers = {
            FraudAnalysis: self._record_fraud_analysis,
            RiskAssessment: self._record_risk_assessment,
            EvidenceVerification: self._record_evidence_verification,
            GraphAnalysis: self._record_graph_analysis,
            ProcurementAnalysis: self._record_procurement_analysis,
        }
    
    @property
    def id(self) -> CaseId:
        """Get aggregate identifier as CaseId (type-safe)."""
        return self.case_id

    @classmethod
    def rehydrate(
        cls,
        case_id: CaseId,
        fraud: Optional[FraudAnalysis] = None,
        risk: Optional[RiskAssessment] = None,
        evidence: Optional[EvidenceVerification] = None,
        graph: Optional[GraphAnalysis] = None,
        procurement: Optional[ProcurementAnalysis] = None,
        version: int = 0,
    ) -> "CaseIntelligenceAggregate":
        """Rehydrate aggregate from persistence."""
        aggregate = cls(case_id=case_id)
        if fraud:
            aggregate._latest_results[ANALYSIS_TYPE_FRAUD] = fraud
        if risk:
            aggregate._latest_results[ANALYSIS_TYPE_RISK] = risk
        if evidence:
            aggregate._latest_results[ANALYSIS_TYPE_EVIDENCE] = evidence
        if graph:
            aggregate._latest_results[ANALYSIS_TYPE_GRAPH] = graph
        if procurement:
            aggregate._latest_results[ANALYSIS_TYPE_PROCUREMENT] = procurement
        aggregate._version = version
        return aggregate
    
    def record_analysis(self, analysis: Any) -> None:
        """
        Record analysis result using explicit dispatch table.
        ✅ Explicit dispatch (not singledispatch)
        ✅ IDE can navigate to handlers
        """
        handler = self._handlers.get(type(analysis))
        if handler is None:
            raise ValueError(f"Unknown analysis type: {type(analysis).__name__}")
        handler(analysis)
    
    def _record_fraud_analysis(self, analysis: FraudAnalysis) -> None:
        self._latest_results[ANALYSIS_TYPE_FRAUD] = analysis
        self._record(FraudAnalysisRecorded(
            case_id=self.case_id,
            analysis=analysis
        ))
    
    def _record_risk_assessment(self, assessment: RiskAssessment) -> None:
        self._latest_results[ANALYSIS_TYPE_RISK] = assessment
        self._record(RiskAssessmentRecorded(
            case_id=self.case_id,
            assessment=assessment
        ))
    
    def _record_evidence_verification(self, verification: EvidenceVerification) -> None:
        self._latest_results[ANALYSIS_TYPE_EVIDENCE] = verification
        self._record(EvidenceVerified(
            case_id=self.case_id,
            verification=verification
        ))
    
    def _record_graph_analysis(self, analysis: GraphAnalysis) -> None:
        self._latest_results[ANALYSIS_TYPE_GRAPH] = analysis
        self._record(GraphAnalysisPerformed(
            case_id=self.case_id,
            analysis=analysis
        ))
    
    def _record_procurement_analysis(self, analysis: ProcurementAnalysis) -> None:
        self._latest_results[ANALYSIS_TYPE_PROCUREMENT] = analysis
        self._record(ProcurementAnalysisPerformed(
            case_id=self.case_id,
            analysis=analysis
        ))
    
    def get_latest_analyses(self) -> AnalysisBundle:
        """Get all latest analyses as a bundle."""
        return AnalysisBundle(
            fraud=self._latest_results.get(ANALYSIS_TYPE_FRAUD),
            risk=self._latest_results.get(ANALYSIS_TYPE_RISK),
            evidence=self._latest_results.get(ANALYSIS_TYPE_EVIDENCE),
            graph=self._latest_results.get(ANALYSIS_TYPE_GRAPH),
            procurement=self._latest_results.get(ANALYSIS_TYPE_PROCUREMENT),
        )
    
    def get_analysis(self, analysis_type: str) -> Optional[Any]:
        """Get specific analysis by type key."""
        return self._latest_results.get(analysis_type)
    
    def has_any_analysis(self) -> bool:
        return len(self._latest_results) > 0
    
    def has_analysis_type(self, analysis_type: str) -> bool:
        return analysis_type in self._latest_results
    
    @property
    def latest_fraud(self) -> Optional[FraudAnalysis]:
        return self._latest_results.get(ANALYSIS_TYPE_FRAUD)
    
    @property
    def latest_risk(self) -> Optional[RiskAssessment]:
        return self._latest_results.get(ANALYSIS_TYPE_RISK)
    
    @property
    def latest_evidence(self) -> Optional[EvidenceVerification]:
        return self._latest_results.get(ANALYSIS_TYPE_EVIDENCE)
    
    @property
    def latest_graph(self) -> Optional[GraphAnalysis]:
        return self._latest_results.get(ANALYSIS_TYPE_GRAPH)
    
    @property
    def latest_procurement(self) -> Optional[ProcurementAnalysis]:
        return self._latest_results.get(ANALYSIS_TYPE_PROCUREMENT)
