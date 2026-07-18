"""
Intelligence Policy - Domain Policy (BUKAN Application Config)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class IntelligencePolicy:
    """
    Intelligence Policy - Domain Policy untuk scoring.

    Ini adalah Business Rule, BUKAN Application Config.
    """

    # Base score
    BASE_SCORE: float = 50.0
    SCORE_DELTA: float = 10.0
    MIN_SCORE: float = 0.0
    MAX_SCORE: float = 100.0

    # Evidence weights
    EVIDENCE_WEIGHT: float = 0.3
    MAX_EVIDENCE_BONUS: float = 30.0
    NO_EVIDENCE_PENALTY: float = 10.0

    # Decision weights
    DECISION_CONFIRMED_BONUS: float = 20.0
    DECISION_REJECTED_PENALTY: float = 10.0
    DEFAULT_DECISION_STATUS: str = "PENDING"

    # SLA weights
    SLA_BREACH_WEIGHT: float = 10.0
    MAX_SLA_PENALTY: float = 20.0

    # Level thresholds
    LEVEL_CRITICAL_THRESHOLD: float = 80.0
    LEVEL_HIGH_THRESHOLD: float = 60.0
    LEVEL_MEDIUM_THRESHOLD: float = 40.0