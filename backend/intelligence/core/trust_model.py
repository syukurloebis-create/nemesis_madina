"""
Trust Model – Stable trust aggregation engine (V8+)
Trust = f(risk_score, business_score) dengan stabilizer
"""

from typing import Dict, Optional


class TrustModel:
    """
    Trust computation dengan business reinforcement dan stabilizer
    Output: trust_score (0-1) + trust_level (HIGH/MEDIUM/LOW)
    """

    def __init__(self):
        self.business_min = 0.30
        self.business_max = 0.90
        self.trust_high_threshold = 0.75
        self.trust_medium_threshold = 0.50

    def compute(
        self,
        risk_score: float,
        business_score: float,
        previous_trust: Optional[float] = None,
        alpha: float = 0.85
    ) -> Dict[str, any]:
        """
        Compute trust score dari risk dan business

        Args:
            risk_score: Risk score dari RiskModel (0-1)
            business_score: Raw business score (bisa 0-1 atau skala lain)
            previous_trust: Previous trust untuk smoothing
            alpha: Smoothing factor (higher = lebih stabil)

        Returns:
            Dictionary dengan trust_score, trust_level, dan metadata
        """
        # 1. Stabilize business score
        stabilized_business = self._stabilize_business_score(business_score)

        # 2. Base trust = inverse risk
        base_trust = 1.0 - risk_score

        # 3. Business reinforcement (trust naik jika business bagus)
        # Formula: trust = (weight_risk * base_trust) + (weight_business * business)
        weight_risk = 0.55
        weight_business = 0.45

        raw_trust = (weight_risk * base_trust) + (weight_business * stabilized_business)

        # 4. Clamp ke range [0.1, 0.95] – tidak pernah 0 atau 1
        clamped_trust = max(0.1, min(raw_trust, 0.95))

        # 5. Temporal smoothing
        if previous_trust is not None:
            smoothed_trust = (alpha * previous_trust) + ((1 - alpha) * clamped_trust)
        else:
            smoothed_trust = clamped_trust

        final_trust = round(smoothed_trust, 4)

        # 6. Determine trust level
        if final_trust >= self.trust_high_threshold:
            trust_level = "HIGH"
        elif final_trust >= self.trust_medium_threshold:
            trust_level = "MEDIUM"
        else:
            trust_level = "LOW"

        return {
            "trust_score": final_trust,
            "trust_level": trust_level,
            "components": {
                "base_trust": round(base_trust, 4),
                "stabilized_business": round(stabilized_business, 4),
                "risk_contribution": round(weight_risk * base_trust, 4),
                "business_contribution": round(weight_business * stabilized_business, 4),
            }
        }

    def _stabilize_business_score(self, raw_score: float) -> float:
        """
        Stabilize business score agar tidak ekstrem

        Raw business score sering:
        - 0.0 (error)
        - >1.0 (scale mismatch)
        - Fluktuatif liar

        Output selalu di range [0.3, 0.9]
        """
        if raw_score is None or raw_score <= 0:
            return 0.50  # Default neutral

        if raw_score > 1.0:
            # Scale down jika >1
            raw_score = raw_score / 10.0

        # Clamp ke range yang stabil
        clamped = max(self.business_min, min(raw_score, self.business_max))

        # Round to 4 decimals
        return round(clamped, 4)