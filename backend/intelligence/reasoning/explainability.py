"""
Hybrid Explainability Engine
Rule + ML + Evidence + Expert explanation
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)


class ExplanationType(str, Enum):
    """Jenis explanation"""
    RULE = "rule"
    ML = "ml"
    EVIDENCE = "evidence"
    EXPERT = "expert"
    GRAPH = "graph"
    TEMPORAL = "temporal"


@dataclass
class ExplanationFactor:
    """Faktor dalam explanation"""
    type: ExplanationType
    factor_name: str
    description: str
    impact: float
    confidence: float
    evidence_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "factor_name": self.factor_name,
            "description": self.description,
            "impact": self.impact,
            "confidence": self.confidence,
            "evidence_ids": self.evidence_ids,
            "metadata": self.metadata
        }


@dataclass
class ExplanationResult:
    """Hasil explanation"""
    score: float
    confidence: float
    factors: List[ExplanationFactor]
    summary: str
    timestamp: datetime = field(default_factory=datetime.now)
    case_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "confidence": self.confidence,
            "factors": [f.to_dict() for f in self.factors],
            "summary": self.summary,
            "timestamp": self.timestamp.isoformat(),
            "case_id": self.case_id
        }


class HybridExplainabilityEngine:
    """Hybrid Explainability Engine"""

    def __init__(self):
        self.rule_engine = None
        self.ml_engine = None
        self.evidence_engine = None
        self.expert_engine = None
        self.factor_weights = {
            ExplanationType.RULE: 0.30,
            ExplanationType.ML: 0.25,
            ExplanationType.EVIDENCE: 0.25,
            ExplanationType.EXPERT: 0.10,
            ExplanationType.GRAPH: 0.10,
        }

    def explain(
        self,
        case_data: Dict[str, Any],
        ml_prediction: Optional[Dict[str, Any]] = None,
        graph_data: Optional[Dict[str, Any]] = None,
        evidence_data: Optional[List[Dict[str, Any]]] = None
    ) -> ExplanationResult:
        """Generate hybrid explanation"""
        factors = []

        rule_factors = self._get_rule_factors(case_data)
        factors.extend(rule_factors)

        if ml_prediction:
            ml_factors = self._get_ml_factors(ml_prediction)
            factors.extend(ml_factors)

        if evidence_data:
            evidence_factors = self._get_evidence_factors(evidence_data)
            factors.extend(evidence_factors)

        if graph_data:
            graph_factors = self._get_graph_factors(graph_data)
            factors.extend(graph_factors)

        expert_factors = self._get_expert_factors(case_data)
        factors.extend(expert_factors)

        total_score = self._calculate_weighted_score(factors)
        confidence = self._calculate_confidence(factors)
        summary = self._generate_summary(factors, total_score)

        return ExplanationResult(
            score=total_score,
            confidence=confidence,
            factors=factors,
            summary=summary,
            case_id=case_data.get("case_id")
        )

    def _get_rule_factors(self, data: Dict[str, Any]) -> List[ExplanationFactor]:
        """Get rule-based factors"""
        factors = []
        rules = [
            {
                "id": "R001",
                "name": "Tender Split",
                "description": "Proyek dipecah menjadi beberapa paket kecil",
                "impact": 25,
                "condition": data.get("tender_split", False)
            },
            {
                "id": "R002",
                "name": "Vendor Concentration",
                "description": "Vendor dominan di banyak proyek",
                "impact": 20,
                "condition": data.get("vendor_concentration", 0) > 0.5
            },
            {
                "id": "R003",
                "name": "Abnormal Price",
                "description": "Harga di atas rata-rata pasar",
                "impact": 15,
                "condition": data.get("price_deviation", 0) > 0.2
            },
        ]

        for rule in rules:
            if rule["condition"]:
                factors.append(ExplanationFactor(
                    type=ExplanationType.RULE,
                    factor_name=rule["name"],
                    description=rule["description"],
                    impact=rule["impact"],
                    confidence=0.8,
                    metadata={"rule_id": rule["id"]}
                ))

        return factors

    def _get_ml_factors(self, prediction: Dict[str, Any]) -> List[ExplanationFactor]:
        """Get ML-based factors"""
        factors = []
        ml_features = prediction.get("features", {})

        top_features = sorted(
            ml_features.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]

        for feature_name, importance in top_features:
            factors.append(ExplanationFactor(
                type=ExplanationType.ML,
                factor_name=feature_name,
                description=f"Feature importance: {feature_name}",
                impact=importance * 100,
                confidence=prediction.get("confidence", 0.7),
                metadata={"feature_value": importance}
            ))

        return factors

    def _get_evidence_factors(self, evidence_list: List[Dict[str, Any]]) -> List[ExplanationFactor]:
        """Get evidence-based factors"""
        factors = []
        for evidence in evidence_list[:5]:
            factors.append(ExplanationFactor(
                type=ExplanationType.EVIDENCE,
                factor_name=evidence.get("type", "unknown"),
                description=evidence.get("description", ""),
                impact=evidence.get("impact", 0),
                confidence=evidence.get("trust_score", 0.5),
                evidence_ids=[evidence.get("id")],
                metadata={"source": evidence.get("source")}
            ))
        return factors

    def _get_graph_factors(self, graph_data: Dict[str, Any]) -> List[ExplanationFactor]:
        """Get graph-based factors"""
        factors = []

        if graph_data.get("collusion_score", 0) > 0.5:
            factors.append(ExplanationFactor(
                type=ExplanationType.GRAPH,
                factor_name="Collusion Detection",
                description="Detected suspicious relationships",
                impact=graph_data.get("collusion_score", 0) * 30,
                confidence=0.8,
                metadata={"source": graph_data.get("source"), "target": graph_data.get("target")}
            ))

        return factors

    def _get_expert_factors(self, data: Dict[str, Any]) -> List[ExplanationFactor]:
        """Get expert-based factors"""
        factors = []
        high_risk_sectors = ["Construction", "Procurement", "Infrastructure"]
        sector = data.get("sector", "")

        if sector in high_risk_sectors:
            factors.append(ExplanationFactor(
                type=ExplanationType.EXPERT,
                factor_name="High Risk Sector",
                description=f"{sector} is known to have higher fraud risk",
                impact=15,
                confidence=0.75,
                metadata={"sector": sector}
            ))

        return factors

    def _calculate_weighted_score(self, factors: List[ExplanationFactor]) -> float:
        if not factors:
            return 0

        total_impact = 0
        total_weight = 0

        for factor in factors:
            weight = self.factor_weights.get(factor.type, 0.1)
            impact = factor.impact * factor.confidence
            total_impact += impact * weight
            total_weight += weight

        return total_impact / total_weight if total_weight > 0 else 0

    def _calculate_confidence(self, factors: List[ExplanationFactor]) -> float:
        if not factors:
            return 0
        avg_confidence = sum(f.confidence for f in factors) / len(factors)
        return min(avg_confidence, 1.0)

    def _generate_summary(self, factors: List[ExplanationFactor], score: float) -> str:
        if not factors:
            return "No risk factors identified."

        sorted_factors = sorted(factors, key=lambda x: abs(x.impact), reverse=True)
        top_3 = sorted_factors[:3]
        risk_level = "HIGH" if score > 70 else "MEDIUM" if score > 40 else "LOW"

        summary = f"Risk Level: {risk_level} (Score: {score:.1f})\n\n"
        summary += "Key contributing factors:\n"

        for i, factor in enumerate(top_3, 1):
            summary += f"{i}. {factor.factor_name}: {factor.impact:.1f}% impact\n"
            summary += f"   {factor.description} (Confidence: {factor.confidence:.0%})\n"

        return summary


explainability_engine = HybridExplainabilityEngine()
