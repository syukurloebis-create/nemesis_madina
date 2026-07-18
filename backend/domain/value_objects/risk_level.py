"""
NEMESIS Madina - Risk Level Value Object
"""

from enum import Enum
from typing import Union


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    
    @classmethod
    def from_score(cls, score: Union[int, float]) -> "RiskLevel":
        """
        Convert numeric score to RiskLevel.
        ✅ Single source of truth for risk level mapping
        
        0.0 - 0.3: LOW
        0.3 - 0.6: MEDIUM
        0.6 - 0.8: HIGH
        0.8 - 1.0: CRITICAL
        """
        if score < 0.3:
            return RiskLevel.LOW
        elif score < 0.6:
            return RiskLevel.MEDIUM
        elif score < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    @classmethod
    def from_string(cls, value: str) -> "RiskLevel":
        try:
            return RiskLevel(value.upper())
        except ValueError:
            return RiskLevel.MEDIUM  # Safe default
    
    def __str__(self) -> str:
        return self.value
    
    def __lt__(self, other: "RiskLevel") -> bool:
        order = [RiskLevel.LOW, RiskLevel.MEDIUM, RiskLevel.HIGH, RiskLevel.CRITICAL]
        return order.index(self) < order.index(other)
    
    def __le__(self, other: "RiskLevel") -> bool:
        return self < other or self == other
    
    def __gt__(self, other: "RiskLevel") -> bool:
        return other < self
    
    def __ge__(self, other: "RiskLevel") -> bool:
        return self > other or self == other