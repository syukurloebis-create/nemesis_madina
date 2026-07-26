"""
NEMESIS Madina - Case Data Mapper
✅ Pure DI - no defaults
✅ True Inversion of Control
"""

from sqlalchemy import func
from backend.domain.aggregates.case_intelligence import CaseIntelligenceAggregate
from backend.domain.value_objects.case_id import CaseId
from backend.cases.models import Case
from backend.infrastructure.mappers.fraud_mapper import FraudAnalysisMapper
from backend.infrastructure.mappers.risk_mapper import RiskAssessmentMapper
from backend.infrastructure.mappers.evidence_mapper import EvidenceVerificationMapper
from backend.infrastructure.mappers.graph_mapper import GraphAnalysisMapper
from backend.infrastructure.mappers.procurement_mapper import ProcurementAnalysisMapper


class CaseMapper:
    """Pure data mapper — no business logic."""

    def __init__(self, fraud_mapper, risk_mapper, evidence_mapper, graph_mapper, procurement_mapper):
        self._fraud_mapper = fraud_mapper
        self._risk_mapper = risk_mapper
        self._evidence_mapper = evidence_mapper
        self._graph_mapper = graph_mapper
        self._procurement_mapper = procurement_mapper

    def to_model(self, aggregate: CaseIntelligenceAggregate) -> Case:
        """Aggregate → ORM model."""
        return Case(
            id=aggregate.case_id.value,
            version=aggregate.version,
            latest_fraud=self._fraud_mapper.to_dict(aggregate.latest_fraud),
            latest_risk=self._risk_mapper.to_dict(aggregate.latest_risk),
            latest_evidence=self._evidence_mapper.to_dict(aggregate.latest_evidence),
            latest_graph=self._graph_mapper.to_dict(aggregate.latest_graph),
            latest_procurement=self._procurement_mapper.to_dict(aggregate.latest_procurement),
        )

    def to_aggregate(self, model: Case) -> CaseIntelligenceAggregate:
        """ORM model → Aggregate."""
        return CaseIntelligenceAggregate.rehydrate(
            case_id=CaseId(model.id),
            fraud=self._fraud_mapper.from_dict(model.latest_fraud),
            risk=self._risk_mapper.from_dict(model.latest_risk),
            evidence=self._evidence_mapper.from_dict(model.latest_evidence),
            graph=self._graph_mapper.from_dict(model.latest_graph),
            procurement=self._procurement_mapper.from_dict(model.latest_procurement),
            version=model.version,
        )

    def update_model(self, model: Case, aggregate: CaseIntelligenceAggregate) -> None:
        """Update ORM model from aggregate (for identity map sync)."""
        model.version = aggregate.version
        model.latest_fraud = self._fraud_mapper.to_dict(aggregate.latest_fraud)
        model.latest_risk = self._risk_mapper.to_dict(aggregate.latest_risk)
        model.latest_evidence = self._evidence_mapper.to_dict(aggregate.latest_evidence)
        model.latest_graph = self._graph_mapper.to_dict(aggregate.latest_graph)
        model.latest_procurement = self._procurement_mapper.to_dict(aggregate.latest_procurement)

    def to_update_values(self, aggregate: CaseIntelligenceAggregate) -> dict:
        """Single method for update values."""
        return {
            "version": aggregate.version,
            "latest_fraud": self._fraud_mapper.to_dict(aggregate.latest_fraud),
            "latest_risk": self._risk_mapper.to_dict(aggregate.latest_risk),
            "latest_evidence": self._evidence_mapper.to_dict(aggregate.latest_evidence),
            "latest_graph": self._graph_mapper.to_dict(aggregate.latest_graph),
            "latest_procurement": self._procurement_mapper.to_dict(aggregate.latest_procurement),
            "updated_at": func.now(),
        }