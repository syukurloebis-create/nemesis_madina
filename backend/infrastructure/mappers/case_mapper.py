"""
NEMESIS Madina - Case Data Mapper
✅ Pure DI - no defaults
✅ True Inversion of Control
"""

from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.value_objects.case_id import CaseId
from backend.cases.models import Case
from backend.infrastructure.mappers.fraud_mapper import FraudAnalysisMapper
from backend.infrastructure.mappers.risk_mapper import RiskAssessmentMapper
from backend.infrastructure.mappers.evidence_mapper import EvidenceVerificationMapper
from backend.infrastructure.mappers.graph_mapper import GraphAnalysisMapper
from backend.infrastructure.mappers.procurement_mapper import ProcurementAnalysisMapper


class CaseMapper:
    """
    Case Data Mapper - Pure DI.
    ✅ All dependencies injected (no defaults)
    ✅ True Inversion of Control
    ✅ Testable with mocks/stubs
    """
    
    def __init__(
        self,
        fraud_mapper: FraudAnalysisMapper,
        risk_mapper: RiskAssessmentMapper,
        evidence_mapper: EvidenceVerificationMapper,
        graph_mapper: GraphAnalysisMapper,
        procurement_mapper: ProcurementAnalysisMapper,
    ):
        self._fraud_mapper = fraud_mapper
        self._risk_mapper = risk_mapper
        self._evidence_mapper = evidence_mapper
        self._graph_mapper = graph_mapper
        self._procurement_mapper = procurement_mapper
    
    def to_model(self, aggregate: CaseIntelligenceAggregate) -> Case:
        """Map aggregate to SQLAlchemy model."""
        return Case(
            id=str(aggregate.case_id),
            version=aggregate.version,
            latest_fraud=self._fraud_mapper.to_dict(aggregate.latest_fraud),
            latest_risk=self._risk_mapper.to_dict(aggregate.latest_risk),
            latest_evidence=self._evidence_mapper.to_dict(aggregate.latest_evidence),
            latest_graph=self._graph_mapper.to_dict(aggregate.latest_graph),
            latest_procurement=self._procurement_mapper.to_dict(aggregate.latest_procurement),
        )
    
    def to_aggregate(self, model: Case) -> CaseIntelligenceAggregate:
        """Map SQLAlchemy model to aggregate."""
        return CaseIntelligenceAggregate.rehydrate(
            case_id=CaseId(model.id),
            fraud=self._fraud_mapper.from_dict(model.latest_fraud),
            risk=self._risk_mapper.from_dict(model.latest_risk),
            evidence=self._evidence_mapper.from_dict(model.latest_evidence),
            graph=self._graph_mapper.from_dict(model.latest_graph),
            procurement=self._procurement_mapper.from_dict(model.latest_procurement),
            version=model.version,
        )