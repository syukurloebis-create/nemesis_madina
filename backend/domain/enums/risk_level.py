"""
NEMESIS Madina - Risk Level Enum
Pure DDD Value Object
"""

from enum import Enum
from typing import Union
from backend.domain.enums.severity import Severity


class RiskLevel(str, Enum):
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def from_string(cls, value: str) -> "RiskLevel":
        if not value:
            return cls.UNKNOWN

        try:
            return cls(value.strip().upper())
        except ValueError:
            return cls.UNKNOWN
    
    @classmethod
    def from_score(cls, score: Union[int, float]) -> "RiskLevel":
        """Convert numeric score to RiskLevel."""
        if score >= 0.8:
            return cls.CRITICAL
        elif score >= 0.6:
            return cls.HIGH
        elif score >= 0.3:
            return cls.MEDIUM
        elif score >= 0.1:
            return cls.LOW
        return cls.UNKNOWN

    @classmethod
    def from_severity(cls, severity: "Severity") -> "RiskLevel":
        """Convert Severity enum to RiskLevel."""
        mapping = {
            Severity.UNKNOWN: cls.UNKNOWN,
            Severity.LOW: cls.LOW,
            Severity.MEDIUM: cls.MEDIUM,
            Severity.HIGH: cls.HIGH,
            Severity.CRITICAL: cls.CRITICAL,
        }
        return mapping.get(severity, cls.UNKNOWN)
    
    def __lt__(self, other: "RiskLevel") -> bool:
        """Compare risk levels."""
        order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        return order.index(self) < order.index(other)
    
    def __le__(self, other: "RiskLevel") -> bool:
        return self < other or self == other
    
    def __gt__(self, other: "RiskLevel") -> bool:
        return not (self <= other)
    
    def __ge__(self, other: "RiskLevel") -> bool:
        return not (self < other)