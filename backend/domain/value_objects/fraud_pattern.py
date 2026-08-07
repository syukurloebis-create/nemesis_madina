from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class FraudPatternType(Enum):
    """Types of fraud patterns"""
    COLLUSION = "COLLUSION"
    ANOMALY = "anomaly"
    SYNDICATE = "syndicate"
    SHELL_COMPANY = "shell_company"
    BID_RIGGING = "bid_rigging"
    CONFLICT_OF_INTEREST = "conflict_of_interest"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, value: str) -> "FraudPatternType":
        if not value:
            return cls.UNKNOWN
        normalized = value.lower()
        mapping = {
            "collusion": cls.COLLUSION,
            "anomaly": cls.ANOMALY,
            "syndicate": cls.SYNDICATE,
            "shell_company": cls.SHELL_COMPANY,
            "bid_rigging": cls.BID_RIGGING,
            "conflict_of_interest": cls.CONFLICT_OF_INTEREST,
        }
        return mapping.get(normalized, cls.UNKNOWN)


class FraudPatternSeverity(Enum):
    """Severity levels for fraud patterns"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @classmethod
    def from_string(cls, value: str) -> "FraudPatternSeverity":
        if not value:
            return cls.LOW
        normalized = value.lower()
        mapping = {
            "low": cls.LOW,
            "medium": cls.MEDIUM,
            "high": cls.HIGH,
            "critical": cls.CRITICAL,
        }
        return mapping.get(normalized, cls.LOW)


@dataclass(frozen=True)
class FraudPattern:
    """Fraud pattern value object."""
    
    # Core fields
    pattern_type: FraudPatternType = FraudPatternType.UNKNOWN
    severity: FraudPatternSeverity = FraudPatternSeverity.LOW
    confidence: float = 0.0  # 0-100 scale
    validated: bool = False
    indicators: List[str] = field(default_factory=list)
    pattern_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    detected_at: Optional[datetime] = None

    def __post_init__(self):
        """Validate value object invariants."""
        # Validate confidence (0-100 scale)
        if not (0 <= self.confidence <= 100):
            raise ValueError(
                f"Confidence must be between 0 and 100, got {self.confidence}"
            )

    # Compatibility property for legacy code
    @property
    def confidence_score(self) -> float:
        """Legacy alias for confidence."""
        return self.confidence

    def is_high_confidence(self) -> bool:
        return self.confidence >= 80

    def is_critical(self) -> bool:
        return self.severity == FraudPatternSeverity.CRITICAL

    def get_indicator_count(self) -> int:
        return len(self.indicators)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "pattern_id": self.pattern_id,
            "name": self.name,
            "pattern_type": self.pattern_type.value if hasattr(self.pattern_type, "value") else str(self.pattern_type),
            "severity": self.severity.value if hasattr(self.severity, "value") else str(self.severity),
            "description": self.description,
            "confidence": self.confidence,
            "confidence_score": self.confidence,  # Legacy compatibility
            "validated": self.validated,
            "indicators": self.indicators,
            "detected_at": self.detected_at.isoformat() if self.detected_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FraudPattern":
        """Create from dictionary."""
        return cls(
            pattern_type=FraudPatternType.from_string(data.get("pattern_type", "UNKNOWN")),
            severity=FraudPatternSeverity.from_string(data.get("severity", "low")),
            confidence=data.get("confidence", data.get("confidence_score", 0.0)),
            validated=data.get("validated", False),
            indicators=data.get("indicators", []),
            pattern_id=data.get("pattern_id"),
            name=data.get("name"),
            description=data.get("description"),
            detected_at=datetime.fromisoformat(data["detected_at"]) if data.get("detected_at") else None,
        )