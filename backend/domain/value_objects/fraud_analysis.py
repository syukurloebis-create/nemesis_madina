"""
NEMESIS Madina - Fraud Analysis Value Object
✅ Pure Value Object - no aggregate knowledge
✅ Immutable collections (Sequence)
"""

from dataclasses import dataclass
from typing import Sequence

from backend.domain.value_objects.fraud_pattern import FraudPattern
from backend.domain.enums.risk_level import RiskLevel


@dataclass(frozen=True)
class FraudAnalysis:
    """Fraud analysis result - Pure Value Object."""

    case_id: str
    patterns: Sequence[FraudPattern]
    overall_risk: RiskLevel
    score: float
    total_patterns: int
    active_alerts: int
    high_confidence: int
    validated_patterns: int
    highest_confidence: float
    average_confidence: float

    def __post_init__(self):
        """Validate value object invariants."""
        if not (0 <= self.score <= 100):
            raise ValueError(
                f"Score must be between 0 and 100, got {self.score}"
            )
        if not (0 <= self.highest_confidence <= 100):
            raise ValueError(
                f"Highest confidence must be between 0 and 100, "
                f"got {self.highest_confidence}"
            )
        if not (0 <= self.average_confidence <= 100):
            raise ValueError(
                f"Average confidence must be between 0 and 100, "
                f"got {self.average_confidence}"
            )

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "case_id": self.case_id,
            "patterns": [
                p.to_dict() if hasattr(p, "to_dict") else p
                for p in self.patterns
            ],
            "overall_risk": self.overall_risk.value if hasattr(self.overall_risk, "value") else str(self.overall_risk),
            "score": self.score,
            "total_patterns": self.total_patterns,
            "active_alerts": self.active_alerts,
            "high_confidence": self.high_confidence,
            "validated_patterns": self.validated_patterns,
            "highest_confidence": self.highest_confidence,
            "average_confidence": self.average_confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FraudAnalysis":
        """Create from dictionary."""
        from backend.domain.value_objects.fraud_pattern import FraudPattern
        
        return cls(
            case_id=data["case_id"],
            patterns=[
                FraudPattern.from_dict(p) if isinstance(p, dict) else p
                for p in data.get("patterns", [])
            ],
            overall_risk=RiskLevel.from_string(data.get("overall_risk", "UNKNOWN")),
            score=data.get("score", 0.0),
            total_patterns=data.get("total_patterns", 0),
            active_alerts=data.get("active_alerts", 0),
            high_confidence=data.get("high_confidence", 0),
            validated_patterns=data.get("validated_patterns", 0),
            highest_confidence=data.get("highest_confidence", 0.0),
            average_confidence=data.get("average_confidence", 0.0),
        )