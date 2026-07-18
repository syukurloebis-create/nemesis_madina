"""
Severity Enum — Level untuk fraud.
"""

from enum import Enum, IntEnum


class Severity(str, Enum):
    """Severity levels."""
    UNKNOWN = "UNKNOWN"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    
    @classmethod
    def from_string(cls, value: str) -> "Severity":
        try:
            return cls(value.upper())
        except (ValueError, AttributeError):
            return cls.UNKNOWN    

    @classmethod
    def from_db(cls, value: str) -> "Severity":
        """
        Normalize severity from database value.
        
        Handles:
            - 'critical' → CRITICAL
            - 'Critical' → CRITICAL
            - 'CRITICAL' → CRITICAL
            - None → UNKNOWN
            - 'HIGH' → HIGH
            - 'high' → HIGH
            - etc.
        """
        if value is None:
            return cls.UNKNOWN
        
        normalized = value.upper().strip()
        
        if normalized == "CRITICAL":
            return cls.CRITICAL
        elif normalized == "HIGH":
            return cls.HIGH
        elif normalized == "MEDIUM":
            return cls.MEDIUM
        elif normalized == "LOW":
            return cls.LOW
        else:
            return cls.UNKNOWN


class SeverityRank(IntEnum):
    """Rank untuk perhitungan severity — scalable."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    UNKNOWN = 0
    
    @classmethod
    def from_string(cls, value: str) -> "SeverityRank":
        mapping = {
            "LOW": cls.LOW,
            "MEDIUM": cls.MEDIUM,
            "HIGH": cls.HIGH,
            "CRITICAL": cls.CRITICAL,
            "UNKNOWN": cls.UNKNOWN
        }
        return mapping.get(value.upper(), cls.UNKNOWN)
    
    @classmethod
    def to_severity(cls, rank: int) -> Severity:
        mapping = {
            4: Severity.CRITICAL,
            3: Severity.HIGH,
            2: Severity.MEDIUM,
            1: Severity.LOW,
            0: Severity.UNKNOWN
        }
        return mapping.get(rank, Severity.UNKNOWN)