from backend.intelligence.core.registry import EventRegistry
from backend.intelligence.core.feature_engine import FeatureEngine
from backend.intelligence.core.risk_model import RiskModel
from backend.intelligence.core.trust_model import TrustModel
from backend.intelligence.core.confidence_model import ConfidenceModel
from backend.intelligence.core.calibration import Calibration
from backend.intelligence.core.explainability_engine import ExplainabilityEngine
from backend.intelligence.core.chain_of_custody import ChainOfCustody
from backend.intelligence.core.entity_memory import EntityMemory

class IntelligenceEngine:
    """
    Sprint 5: Core Intelligence Orchestrator
    Menghubungkan Risk + Trust + Confidence + Explainability + Lineage
    """

    def __init__(self):

        # Core ML / deterministic engines
        self.feature_engine = FeatureEngine()
        self.risk_model = RiskModel()
        self.trust_model = TrustModel()
        self.confidence_model = ConfidenceModel()
        self.calibration = Calibration()
        self.explainability = ExplainabilityEngine()
        self.memory = EntityMemory()

        # ✅ FIX: registry wajib diberikan
        self.registry = EventRegistry()

        # FIX: ChainOfCustody sekarang dependency-injected
        self.chain = ChainOfCustody(self.registry)

    def evaluate(self, entity_id: str, events: list, anomaly_score: float = 0.0):
        """
        Full intelligence pipeline:
        events → features → risk → trust → confidence → explainability
        """

        # 1. Feature extraction
        features = self.feature_engine.extract(events)

        # 2. Risk computation
        raw_risk = self.risk_model.compute(features, anomaly_score=anomaly_score)

        # 3. Calibration (stateful smoothing)
        risk = self.calibration.smooth_risk(entity_id, raw_risk)

        # 4. Trust computation
        trust = self.trust_model.compute(
            risk_score=risk,
            business_score=features.get("business_score", 0.5)
        )

        # 5. Confidence model
        confidence = self.confidence_model.compute(features)

        # 6. Explainability
        explanation = self.explainability.explain(
            features=features,
            risk=risk,
            confidence=confidence,
        )

        # 7. Store lineage (optional audit)
        self.chain.record(entity_id, features, risk, trust)

        # 8. Persist memory
        self.memory.add_score(entity_id, risk, trust)

        return {
            "entity_id": entity_id,
            "features": features,
            "risk": risk,
            "trust": trust,
            "confidence": confidence,
            "explanation": explanation
        }