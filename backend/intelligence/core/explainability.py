from typing import Dict, List


class ExplainabilityEngine:

    def explain(
        self,
        features: Dict,
        risk_score: float,
        anomaly_score: float
    ) -> List[Dict]:

        factors = []

        avg_pagu = features.get("avg_pagu", 0)

        if avg_pagu >= 1_000_000_000:
            factors.append({
                "factor": "large_budget",
                "impact": "HIGH",
                "value": avg_pagu
            })

        elif avg_pagu >= 100_000_000:
            factors.append({
                "factor": "medium_budget",
                "impact": "MEDIUM",
                "value": avg_pagu
            })

        coef_var = features.get("pagu_coef_var", 0)

        if coef_var > 0.5:
            factors.append({
                "factor": "high_volatility",
                "impact": "HIGH",
                "value": coef_var
            })

        elif coef_var > 0.2:
            factors.append({
                "factor": "moderate_volatility",
                "impact": "MEDIUM",
                "value": coef_var
            })

        if anomaly_score > 5:
            factors.append({
                "factor": "anomaly_detected",
                "impact": "HIGH",
                "value": anomaly_score
            })

        if not factors:
            factors.append({
                "factor": "stable_behavior",
                "impact": "LOW",
                "value": risk_score
            })

        return factors