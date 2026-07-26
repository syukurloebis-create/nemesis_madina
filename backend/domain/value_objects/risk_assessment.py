# backend/domain/value_objects/risk_assessment.py
"""
NEMESIS Madina - Risk Assessment Value Object
✅ Pure Value Object - no aggregate knowledge
✅ Immutable
✅ Enhanced with all required fields
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from backend.domain.enums.risk_level import RiskLevel


@dataclass(frozen=True)
class RiskAssessment:
    """Risk assessment result - Pure Value Object."""

    case_id: str = ""
    score: float = 0.0
    level: RiskLevel = RiskLevel.UNKNOWN  # ← CHANGED: RiskLevel, not str
    confidence: float = 0.0
    anomaly_score: float = 0.0
    collusion_score: float = 0.0
    financial_score: float = 0.0
    status: str = "SUCCESS"
    factors: List[str] = field(default_factory=list)

    @property
    def is_high_risk(self) -> bool:
        return self.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    def __post_init__(self):
        # ✅ FIX: 0-100, bukan 0-1
        if not (0 <= self.score <= 100):
            raise ValueError(f"Risk score must be between 0 and 100, got {self.score}")
        if not (0 <= self.confidence <= 100):
            raise ValueError(f"Confidence must be between 0 and 100, got {self.confidence}")

    def is_low_risk(self) -> bool:
        """Check if risk is low or medium"""
        return self.level in (RiskLevel.LOW, RiskLevel.MEDIUM)
