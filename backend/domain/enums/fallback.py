"""
Fallback Reason — Alasan engine menggunakan fallback.
"""

from enum import Enum


class FallbackReason(str, Enum):
    """Alasan engine menggunakan fallback mode."""
    NONE = "NONE"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"
    NO_DATA = "NO_DATA"
    PARTIAL = "PARTIAL"
    QUERY_ERROR = "QUERY_ERROR" 
    UNKNOWN = "UNKNOWN"
    
    @classmethod
    def from_string(cls, value: str) -> "FallbackReason":
        try:
            return cls(value.upper())
        except (ValueError, AttributeError):
            return cls.UNKNOWN


# ============================================================================
# BACKWARD COMPATIBILITY — Export
# ============================================================================

__all__ = [
    "FallbackReason",
]