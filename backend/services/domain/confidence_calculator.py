"""
Confidence Calculator — Domain Service.
"""

from dataclasses import dataclass, field
from typing import Dict

# ✅ PERBAIKAN: Import dari summary_objects
from backend.domain.summary_objects import (
    FraudSummary,
    GraphSummary,
    RiskSummary,
    EvidenceSummary,
    ProcurementSummary
)


@dataclass(frozen=True, slots=True)
class ConfidenceResult:
    """Confidence calculation result."""
    score: float
    components: Dict[str, float] = field(default_factory=dict)


class ConfidenceCalculator:
    """Confidence Calculator — Domain Service."""

    WEIGHTS = {
        "fraud": 0.30,
        "graph": 0.15,
        "risk": 0.25,
        "evidence": 0.20,
        "procurement": 0.10
    }

    @classmethod
    def calculate(
        cls,
        fraud: FraudSummary,
        graph: GraphSummary,
        risk: RiskSummary,
        evidence: EvidenceSummary,
        procurement: ProcurementSummary
    ) -> ConfidenceResult:
        """Calculate aggregate confidence."""
        components = {
            "fraud": cls._fraud_score(fraud),
            "graph": cls._graph_score(graph),
            "risk": cls._risk_score(risk),
            "evidence": cls._evidence_score(evidence),
            "procurement": cls._procurement_score(procurement)
        }

        total_weight = sum(cls.WEIGHTS.values())
        score = sum(components[k] * cls.WEIGHTS[k] for k in components) / total_weight

        return ConfidenceResult(
            score=round(score * 100, 2),
            components=components
        )

    @classmethod
    def _fraud_score(cls, fraud: FraudSummary) -> float:
        return fraud.score / 100 if fraud.score else 0

    @classmethod
    def _graph_score(cls, graph: GraphSummary) -> float:
        return min(graph.entities / 1000, 1.0) if graph.entities else 0

    @classmethod
    def _risk_score(cls, risk: RiskSummary) -> float:
        return risk.score / 100 if risk.score else 0

    @classmethod
    def _evidence_score(cls, evidence: EvidenceSummary) -> float:
        return evidence.score / 100 if evidence.score else 0

    @classmethod
    def _procurement_score(cls, procurement: ProcurementSummary) -> float:
        return min(procurement.vendors / 10, 1.0) if procurement.vendors else 0