"""
Risk Reasoning Engine
Core engine for risk reasoning and scoring
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .explainability import HybridExplainabilityEngine, ExplanationResult, explainability_engine

logger = logging.getLogger(__name__)


@dataclass
class RiskScore:
    """Risk score with components"""
    case_id: str
    overall: float
    components: Dict[str, float]
    explanation: ExplanationResult
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "overall": self.overall,
            "components": self.components,
            "explanation": self.explanation.to_dict(),
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version
        }


class RiskReasoningEngine:
    """Risk Reasoning Engine"""

    def __init__(self):
        self.explainability_engine = explainability_engine
        self.score_config = {
            "fraud_weight": 0.30,
            "graph_weight": 0.25,
            "evidence_weight": 0.20,
            "history_weight": 0.15,
            "expert_weight": 0.10,
        }

    async def assess_case(
        self,
        case_id: str,
        case_data: Dict[str, Any],
        ml_prediction: Optional[Dict[str, Any]] = None,
        graph_data: Optional[Dict[str, Any]] = None,
        evidence_data: Optional[List[Dict[str, Any]]] = None
    ) -> RiskScore:
        """Assess risk for a case"""
        components = await self._calculate_components(
            case_data, ml_prediction, graph_data, evidence_data
        )

        overall = self._calculate_overall(components)
        explanation = self.explainability_engine.explain(
            case_data, ml_prediction, graph_data, evidence_data
        )
        confidence = self._calculate_confidence(components, explanation)

        return RiskScore(
            case_id=case_id,
            overall=overall,
            components=components,
            explanation=explanation,
            confidence=confidence
        )

    async def _calculate_components(
        self,
        case_data: Dict[str, Any],
        ml_prediction: Optional[Dict[str, Any]],
        graph_data: Optional[Dict[str, Any]],
        evidence_data: Optional[List[Dict[str, Any]]]
    ) -> Dict[str, float]:
        """Calculate score components"""
        components = {}

        fraud_score = self._calculate_fraud_score(case_data, ml_prediction)
        components["fraud_score"] = fraud_score

        graph_score = self._calculate_graph_score(case_data, graph_data)
        components["graph_score"] = graph_score

        evidence_score = self._calculate_evidence_score(case_data, evidence_data)
        components["evidence_score"] = evidence_score

        history_score = self._calculate_history_score(case_data)
        components["history_score"] = history_score

        expert_score = self._calculate_expert_score(case_data)
        components["expert_score"] = expert_score

        return components

    def _calculate_fraud_score(self, case_data: Dict[str, Any], ml_prediction: Optional[Dict[str, Any]]) -> float:
        score = 0
        weights = []

        if case_data.get("fraud_indicators"):
            score += case_data.get("fraud_indicators", 0) * 0.5
            weights.append(0.5)

        if ml_prediction:
            score += ml_prediction.get("probability", 0) * 100 * 0.5
            weights.append(0.5)

        return score / sum(weights) if weights else 0

    def _calculate_graph_score(self, case_data: Dict[str, Any], graph_data: Optional[Dict[str, Any]]) -> float:
        if not graph_data:
            return 0

        score = graph_data.get("collusion_score", 0) * 0.5 + graph_data.get("centrality", 0) * 0.3
        return min(score * 100, 100)

    def _calculate_evidence_score(self, case_data: Dict[str, Any], evidence_data: Optional[List[Dict[str, Any]]]) -> float:
        if not evidence_data:
            return 50

        avg_trust = sum(e.get("trust_score", 0) for e in evidence_data) / len(evidence_data)
        return max(0, 100 - avg_trust)

    def _calculate_history_score(self, case_data: Dict[str, Any]) -> float:
        similar_cases = case_data.get("similar_cases", 0)
        avg_risk = case_data.get("avg_similar_risk", 0)

        if similar_cases > 0:
            return avg_risk * 0.6 + min(similar_cases / 10, 1) * 40
        return 0

    def _calculate_expert_score(self, case_data: Dict[str, Any]) -> float:
        score = 0
        high_risk_sectors = ["Construction", "Procurement", "Infrastructure"]

        if case_data.get("sector") in high_risk_sectors:
            score += 30
        if case_data.get("contract_value", 0) > 5_000_000_000:
            score += 20
        if case_data.get("vendor_count", 0) > 3:
            score += 15

        return min(score, 100)

    def _calculate_overall(self, components: Dict[str, float]) -> float:
        weighted_sum = 0
        total_weight = 0

        mapping = {
            "fraud_score": "fraud_weight",
            "graph_score": "graph_weight",
            "evidence_score": "evidence_weight",
            "history_score": "history_weight",
            "expert_score": "expert_weight"
        }

        for key, value in components.items():
            weight_key = mapping.get(key)
            if weight_key:
                weight = self.score_config.get(weight_key, 0.2)
                weighted_sum += value * weight
                total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0

    def _calculate_confidence(self, components: Dict[str, float], explanation: ExplanationResult) -> float:
        base_confidence = explanation.confidence
        component_values = list(components.values())

        if component_values:
            avg = sum(component_values) / len(component_values)
            variance = sum((v - avg) ** 2 for v in component_values) / len(component_values)
            agreement_boost = max(0, 1 - variance / 10000) * 0.1
        else:
            agreement_boost = 0

        return min(base_confidence + agreement_boost, 1.0)


risk_reasoning_engine = RiskReasoningEngine()
