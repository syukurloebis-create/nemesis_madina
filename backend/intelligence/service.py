"""
Intelligence Service — Canonical Risk Engine v3.

One calculation → one result → one persistence → many consumers.

Formula (source-based, no recursion):
    Risk = (
        findings_risk * 0.30 +
        graph_risk    * 0.25 +
        fraud_risk    * 0.30 +
        evidence_risk * 0.15
    )

All inputs are risk-direction (0 = no risk, 100 = max risk).
"""

import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)


# ============================================================================
# 1. RISK RESULT — Immutable Value Object
# ============================================================================

@dataclass(frozen=True)
class RiskResult:
    """Risk Result — Immutable Value Object."""
    score: float
    level: str
    components: Dict[str, float]
    weights: Dict[str, float]
    factors: List[str] = None
    recommendations: List[str] = None

    def __post_init__(self):
        if not (0 <= self.score <= 100):
            raise ValueError(f"score must be between 0 and 100, got {self.score}")
        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if self.level not in valid_levels:
            raise ValueError(f"level must be one of {valid_levels}, got {self.level}")
        if self.factors is None:
            object.__setattr__(self, 'factors', [])
        if self.recommendations is None:
            object.__setattr__(self, 'recommendations', [])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "score": self.score,
            "level": self.level,
            "components": self.components,
            "weights": self.weights,
            "factors": self.factors or [],
            "recommendations": self.recommendations or [],
        }


# ============================================================================
# 2. INTELLIGENCE SERVICE — Canonical Risk Engine v3
# ============================================================================

class IntelligenceService:
    """
    Canonical Risk Engine — Stateless, Pure Function.

    All inputs are risk-direction (0 = no risk, 100 = max risk).
    No recursion, no semantic inversion.
    """

    DEFAULT_WEIGHTS = {
        "findings": 0.30,
        "graph": 0.25,
        "fraud": 0.30,
        "evidence": 0.15,
    }

    THRESHOLDS = {
        "CRITICAL": 80,
        "HIGH": 60,
        "MEDIUM": 40,
        "LOW": 0,
    }

    @classmethod
    def calculate(
        cls,
        findings_risk: float = 0,
        graph_risk: float = 0,
        fraud_risk: float = 0,
        evidence_risk: float = 0,
        weights: Optional[Dict[str, float]] = None,
    ) -> RiskResult:
        """
        Calculate canonical risk score.

        All inputs are risk-direction (0-100):
        - findings_risk: severity mix from findings table
        - graph_risk: network density/complexity
        - fraud_risk: fraud pattern score
        - evidence_risk: 100 - evidence_trust (high trust → low risk)
        """
        findings_risk = cls._validate_score(findings_risk, "findings_risk")
        graph_risk = cls._validate_score(graph_risk, "graph_risk")
        fraud_risk = cls._validate_score(fraud_risk, "fraud_risk")
        evidence_risk = cls._validate_score(evidence_risk, "evidence_risk")

        if weights is None:
            weights = cls.DEFAULT_WEIGHTS.copy()
        else:
            weights = cls._validate_weights(weights)

        final_score = (
            findings_risk * weights["findings"] +
            graph_risk * weights["graph"] +
            fraud_risk * weights["fraud"] +
            evidence_risk * weights["evidence"]
        )

        final_score = min(max(final_score, 0), 100)
        level = cls._determine_level(final_score)

        factors = cls._generate_factors(
            findings_risk=findings_risk,
            graph_risk=graph_risk,
            fraud_risk=fraud_risk,
            evidence_risk=evidence_risk,
        )

        recommendations = cls._generate_recommendations(
            level=level,
            findings_risk=findings_risk,
            graph_risk=graph_risk,
            fraud_risk=fraud_risk,
            evidence_risk=evidence_risk,
        )

        return RiskResult(
            score=round(final_score, 2),
            level=level,
            components={
                "findings_risk": round(findings_risk, 2),
                "graph_risk": round(graph_risk, 2),
                "fraud_risk": round(fraud_risk, 2),
                "evidence_risk": round(evidence_risk, 2),
            },
            weights=weights,
            factors=factors,
            recommendations=recommendations,
        )

    @classmethod
    def _validate_score(cls, value: float, name: str) -> float:
        if value < 0 or value > 100:
            logger.warning(f"{name}={value} out of range (0-100), clamping")
            return min(max(value, 0), 100)
        return value

    @classmethod
    def _validate_weights(cls, weights: Dict[str, float]) -> Dict[str, float]:
        required_keys = {"findings", "graph", "fraud", "evidence"}
        missing = required_keys - set(weights.keys())
        if missing:
            raise ValueError(f"Missing weights: {missing}")
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return weights

    @classmethod
    def _determine_level(cls, score: float) -> str:
        if score >= cls.THRESHOLDS["CRITICAL"]:
            return "CRITICAL"
        elif score >= cls.THRESHOLDS["HIGH"]:
            return "HIGH"
        elif score >= cls.THRESHOLDS["MEDIUM"]:
            return "MEDIUM"
        return "LOW"

    @classmethod
    def _generate_factors(
        cls,
        findings_risk: float,
        graph_risk: float,
        fraud_risk: float,
        evidence_risk: float,
    ) -> List[str]:
        factors = []

        if findings_risk > 70:
            factors.append(f"High findings risk ({findings_risk:.1f})")
        elif findings_risk > 50:
            factors.append(f"Moderate findings risk ({findings_risk:.1f})")

        if graph_risk > 70:
            factors.append(f"High graph risk ({graph_risk:.1f})")
        elif graph_risk > 50:
            factors.append(f"Moderate graph risk ({graph_risk:.1f})")

        if fraud_risk > 70:
            factors.append(f"High fraud risk ({fraud_risk:.1f})")
        elif fraud_risk > 50:
            factors.append(f"Moderate fraud risk ({fraud_risk:.1f})")

        if evidence_risk > 70:
            factors.append(f"High evidence risk ({evidence_risk:.1f})")
        elif evidence_risk > 50:
            factors.append(f"Moderate evidence risk ({evidence_risk:.1f})")

        if not factors:
            factors.append("No significant risk factors detected")

        return factors

    @classmethod
    def _generate_recommendations(
        cls,
        level: str,
        findings_risk: float,
        graph_risk: float,
        fraud_risk: float,
        evidence_risk: float,
    ) -> List[str]:
        recommendations = []

        if level == "CRITICAL":
            recommendations.append("🚨 Immediate investigation required")
            recommendations.append("📋 Escalate to senior investigator")
            recommendations.append("🔒 Secure all evidence immediately")
        elif level == "HIGH":
            recommendations.append("🔍 Prioritize investigation")
            recommendations.append("📊 Review all connected entities")
            recommendations.append("📝 Document all findings")
        elif level == "MEDIUM":
            recommendations.append("📋 Schedule follow-up review")
            recommendations.append("🔎 Monitor for escalation")
        else:
            recommendations.append("✅ Routine monitoring continues")
            recommendations.append("📝 Schedule periodic risk reassessment")

        if evidence_risk > 70:
            recommendations.append("📎 Collect additional evidence to reduce evidence risk")
        if graph_risk > 70:
            recommendations.append("🔗 Investigate network connections for collusion patterns")
        if findings_risk > 70:
            recommendations.append("⚠️ Review high-severity findings immediately")

        return recommendations


# ============================================================================
# 3. FORMAT RESPONSE (Utility)
# ============================================================================

def format_risk_response(case_id: str, result: RiskResult) -> Dict[str, Any]:
    """Format RiskResult as API response."""
    return {
        "case_id": case_id,
        "risk_score": result.score,
        "risk_level": result.level,
        "components": result.components,
        "factors": result.factors,
        "recommendations": result.recommendations,
        "timestamp": datetime.now().isoformat(),
        "version": "v3.0",
    }
