from typing import Dict, Any


class RiskScorer:
    def __init__(self):
        self.weights = {
            "anomaly_score": 0.3,
            "collusion_risk": 0.25,
            "historical_risk": 0.2,
            "velocity": 0.15,
            "volume": 0.1
        }
    
    def compute_score(self, features: Dict[str, float]) -> float:
        score = 0.0
        total = 0.0
        for k, v in features.items():
            if k in self.weights:
                score += v * self.weights[k]
                total += self.weights[k]
        return min(max(score / total if total > 0 else 0, 0.0), 1.0)
    
    def get_severity(self, score: float) -> str:
        if score >= 0.8: return "critical"
        if score >= 0.6: return "high"
        if score >= 0.4: return "medium"
        if score >= 0.2: return "low"
        return "info"
