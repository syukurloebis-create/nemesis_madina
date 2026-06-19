from typing import Dict, Any, List


class ReasoningEngine:
    def __init__(self):
        self.templates = {
            "anomaly": "Anomaly detected: {description}",
            "risk": "Risk score {score} indicates {level} risk"
        }
    
    def generate(self, decision_type: str, data: Dict[str, Any]) -> str:
        template = self.templates.get(decision_type, "Decision based on {data}")
        try:
            return template.format(**data)
        except KeyError:
            return f"Decision: {data}"
    
    def generate_detailed(self, decision_type: str, features: Dict[str, float], score: float) -> List[str]:
        reasons = [f"Decision Type: {decision_type}", f"Score: {score:.3f}"]
        reasons.append("Contributing factors:")
        for k, v in sorted(features.items(), key=lambda x: abs(x[1]), reverse=True)[:5]:
            reasons.append(f"  - {k}: {v:.3f}")
        return reasons
