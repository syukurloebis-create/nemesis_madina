"""
Domain Enums — Package export.

Semua enum di-export dari sini agar import konsisten.
"""

from .engine import EngineName, EngineStatus, EngineType
from .dashboard import DashboardStatus, RecoveryState
from .severity import Severity
from .risk_level import RiskLevel
from .evidence import EvidenceLevel
from .fallback import FallbackReason

# ============================================================================
# BACKWARD COMPATIBILITY — Phase B (akan dihapus di Phase E)
# ============================================================================

# EngineType sudah di-export dari .engine
# FallbackReason sudah di-export dari .fallback

__all__ = [
    # Engine
    "EngineName",
    "EngineStatus",
    "EngineType",          
    
    # Dashboard
    "DashboardStatus",
    "RecoveryState",
    
    # Severity
    "Severity",
    "RiskLevel",
    "EvidenceLevel",
    
    # Fallback
    "FallbackReason",      
]