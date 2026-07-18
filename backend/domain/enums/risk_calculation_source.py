"""
Risk Calculation Source — Siapa yang melakukan perhitungan.
"""

from enum import Enum


class RiskCalculationSource(str, Enum):
    """Source of risk calculation."""
    SYSTEM = "SYSTEM"
    USER = "USER"
    API = "API"
    SCHEDULER = "SCHEDULER"
    MIGRATION = "MIGRATION"
    REPLAY = "REPLAY"
    TEST = "TEST"
    
    @classmethod
    def from_string(cls, value: str) -> "RiskCalculationSource":
        """Safe conversion from string."""
        try:
            return cls(value.upper())
        except (ValueError, AttributeError):
            return cls.SYSTEM