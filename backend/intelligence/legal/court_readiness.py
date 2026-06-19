"""
Court Readiness Module (Stub - Sprint 5)
Dipakai untuk intelligence engine dependency
"""

from typing import Dict


class CourtReadiness:
    """
    Menilai kesiapan kasus untuk eskalasi hukum
    """

    def compute(self, features: Dict, risk_score: float) -> Dict:
        """
        Simple deterministic scoring
        """

        base = 0.5

        # risk tinggi → lebih siap ke court
        risk_factor = risk_score * 0.4

        # event banyak → lebih kuat
        event_factor = min(features.get("event_count", 0) / 20, 0.3)

        score = base + risk_factor + event_factor
        score = max(0.0, min(score, 1.0))

        return {
            "court_score": round(score, 4),
            "ready": score > 0.7,
            "level": (
                "HIGH" if score > 0.75 else
                "MEDIUM" if score > 0.55 else
                "LOW"
            )
        }