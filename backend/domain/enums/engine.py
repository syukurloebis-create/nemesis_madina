"""
Engine Enums — Standard untuk semua intelligence engines.
"""

from enum import Enum


class EngineName(str, Enum):
    """
    Engine Name — Enum untuk semua intelligence engines.
    """
    FRAUD = "fraud"
    RISK = "risk"
    GRAPH = "graph"
    EVIDENCE = "evidence"
    PROCUREMENT = "procurement"
    RECOVERY = "recovery"
    
    @classmethod
    def list_all(cls) -> tuple[str, ...]:
        return tuple(e.value for e in cls)


class EngineStatus(str, Enum):
    """Engine Status — Standard untuk semua intelligence engines."""
    OK = "OK"
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    SKIPPED = "SKIPPED"
    
    @classmethod
    def from_string(cls, value: str) -> "EngineStatus":
        try:
            return cls(value.upper())
        except (ValueError, AttributeError):
            return cls.FAILED


# ============================================================================
# BACKWARD COMPATIBILITY — Phase B (akan dihapus di Phase E)
# ============================================================================

# EngineType adalah alias untuk EngineName (API lama)
EngineType = EngineName

# Ekspor agar bisa diimpor
__all__ = [
    "EngineName",
    "EngineStatus",
    "EngineType",
]