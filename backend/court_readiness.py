# backend/intelligence/legal/court_readiness.py

class CourtReadiness:

    def evaluate(
        self,
        confidence_score: float,
        lineage_verified: bool,
        evidence_verified: bool
    ):

        score = 0

        if confidence_score >= 0.70:
            score += 40

        if lineage_verified:
            score += 30

        if evidence_verified:
            score += 30

        if score >= 90:
            level = "HIGH"

        elif score >= 60:
            level = "MEDIUM"

        else:
            level = "LOW"

        return {
            "readiness_score": score,
            "readiness_level": level
        }