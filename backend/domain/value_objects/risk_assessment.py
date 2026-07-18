# backend/domain/value_objects/risk_assessment.py
"""
NEMESIS Madina - Risk Assessment Value Object
✅ Pure Value Object - no aggregate knowledge
✅ Immutable
✅ Enhanced with all required fields
"""

from dataclasses import dataclass, field
from typing import Optional, List
from backend.domain.enums.risk_level import RiskLevel


@dataclass(frozen=True)
class RiskAssessment:
    """Risk assessment result - Pure Value Object."""
    
    # Core fields (required)
    score: float
    level: str
    confidence: float = 0.0
    factors: List[str] = field(default_factory=list)

    def __post_init__(self):
        # ✅ FIX: 0-100, bukan 0-1
        if not (0 <= self.score <= 100):
            raise ValueError(f"Risk score must be between 0 and 100, got {self.score}")
        if not (0 <= self.confidence <= 100):
            raise ValueError(f"Confidence must be between 0 and 100, got {self.confidence}")

    def is_high_risk(self) -> bool:
        """Check if risk is high or critical"""
        return self.level in (RiskLevel.HIGH, RiskLevel.CRITICAL)

    def is_low_risk(self) -> bool:
        """Check if risk is low or medium"""
        return self.level in (RiskLevel.LOW, RiskLevel.MEDIUM)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'case_id': self.case_id,
            'score': self.score,
            'level': self.level.value,
            'confidence': self.confidence,
            'anomaly_score': self.anomaly_score,
            'collusion_score': self.collusion_score,
            'financial_score': self.financial_score,
            'status': self.status,
            'factors': self.factors,
        }