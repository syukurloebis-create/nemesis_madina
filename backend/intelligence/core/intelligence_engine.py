"""
Intelligence Engine V8+ (Sprint 5)
Orchestrator untuk Risk + Trust + Confidence + Explainability
"""

from typing import Dict

from backend.intelligence.core.risk_model import RiskModel
from backend.intelligence.core.confidence_model import ConfidenceModel
from backend.intelligence.core.explainability_engine import ExplainabilityEngine
from backend.intelligence.legal.court_readiness import CourtReadiness


class IntelligenceEngine:

    def __init__(self):
        self.risk_model = RiskModel()
        self.confidence_model = ConfidenceModel()
        self.explainer = ExplainabilityEngine()
        self.court = CourtReadiness()

    def evaluate(self, entity_id: str, features: Dict, anomaly_score: float = 0.0) -> Dict:
        """
        Full intelligence evaluation pipeline
        """

        # 1. Risk scoring
        risk = self.risk_model.compute(features, anomaly_score)

        # 2. Confidence scoring
        confidence = self.confidence_model.compute(features)

        # 3. Court readiness
        court = self.court.compute(features, risk)

        # 4. Explainability (feature attribution)
        explanation = self.explainer.explain(features, risk, confidence)

        # 5. Final intelligence score
        intelligence_score = (
            (1 - risk) * 0.4 +
            confidence * 0.4 +
            court["court_score"] * 0.2
        )

        return {
            "entity_id": entity_id,
            "risk_score": round(risk, 4),
            "confidence_score": round(confidence, 4),
            "court": court,
            "intelligence_score": round(intelligence_score, 4),
            "explanation": explanation
        }