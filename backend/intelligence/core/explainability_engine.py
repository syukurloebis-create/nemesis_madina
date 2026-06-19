"""
Explainability Engine V8+
Menjelaskan kenapa risk score muncul
"""

from typing import Dict, List


class ExplainabilityEngine:

    def explain(self, features: Dict, risk: float, confidence: float) -> Dict:

        factors: List[Dict] = []

        # Pagu contribution
        pagu = features.get("avg_pagu", 0)
        if pagu > 100_000_000:
            factors.append({
                "feature": "avg_pagu",
                "impact": "HIGH",
                "reason": "Nilai kontrak besar meningkatkan risk"
            })
        elif pagu > 10_000_000:
            factors.append({
                "feature": "avg_pagu",
                "impact": "MEDIUM",
                "reason": "Nilai kontrak sedang"
            })
        else:
            factors.append({
                "feature": "avg_pagu",
                "impact": "LOW",
                "reason": "Nilai kontrak kecil menurunkan risk"
            })

        # volatility
        cv = features.get("pagu_coef_var", 0)
        if cv > 0.5:
            factors.append({
                "feature": "volatility",
                "impact": "HIGH",
                "reason": "Variasi anggaran tinggi"
            })

        # event count
        if features.get("event_count", 0) > 10:
            factors.append({
                "feature": "event_count",
                "impact": "LOW_RISK",
                "reason": "Data historis stabil"
            })

        return {
            "risk": risk,
            "confidence": confidence,
            "factors": factors
        }