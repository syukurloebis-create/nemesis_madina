"""
Unified Intelligence Score
"""
from typing import Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class UnifiedScore:
    """Unified intelligence score"""
    case_id: str
    risk_score: float
    fraud_score: float
    graph_risk: float
    evidence_trust: float
    overall: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    version: str = "2.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "risk_score": self.risk_score,
            "fraud_score": self.fraud_score,
            "graph_risk": self.graph_risk,
            "evidence_trust": self.evidence_trust,
            "overall": self.overall,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version
        }


class UnifiedScoreEngine:
    """Unified Intelligence Score Engine"""

    def __init__(self):
        self.weights = {
            "risk_score": 0.30,
            "fraud_score": 0.25,
            "graph_risk": 0.20,
            "evidence_trust": 0.15,
            "history_score": 0.10,
        }

    async def calculate(
        self,
        case_id: str,
        risk_score: float,
        fraud_score: float,
        graph_risk: float,
        evidence_trust: float,
        history_score: float = 0
    ) -> UnifiedScore:
        """Calculate unified score"""
        overall = self._calculate_overall(
            risk_score, fraud_score, graph_risk, evidence_trust, history_score
        )
        confidence = self._calculate_confidence(
            risk_score, fraud_score, graph_risk, evidence_trust
        )

        return UnifiedScore(
            case_id=case_id,
            risk_score=risk_score,
            fraud_score=fraud_score,
            graph_risk=graph_risk,
            evidence_trust=evidence_trust,
            overall=overall,
            confidence=confidence
        )

    def _calculate_overall(
        self,
        risk_score: float,
        fraud_score: float,
        graph_risk: float,
        evidence_trust: float,
        history_score: float
    ) -> float:
        weighted_sum = (
            risk_score * self.weights["risk_score"] +
            fraud_score * self.weights["fraud_score"] +
            graph_risk * self.weights["graph_risk"] +
            (100 - evidence_trust) * self.weights["evidence_trust"] +
            history_score * self.weights["history_score"]
        )
        total_weight = sum(self.weights.values())
        return weighted_sum / total_weight if total_weight > 0 else 0

    def _calculate_confidence(self, risk_score: float, fraud_score: float, graph_risk: float, evidence_trust: float) -> float:
        scores = [risk_score, fraud_score, graph_risk, evidence_trust]
        valid_scores = [s for s in scores if s > 0]

        if not valid_scores:
            return 0

        avg = sum(valid_scores) / len(valid_scores)
        variance = sum((s - avg) ** 2 for s in valid_scores) / len(valid_scores)
        confidence = 1 - (variance / 10000) * 0.5

        return max(0, min(confidence, 1))


unified_score_engine = UnifiedScoreEngine()
