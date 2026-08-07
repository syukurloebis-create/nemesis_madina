# backend/domain/enums/__init__.py
"""
Domain Enums Registry

This module exports all domain enums used across the NEMESIS system.
All enums are defined in separate files and imported here for convenience.

Note: RiskLevel is imported from risk_level.py (canonical owner).
Do not import from risk.py (duplicate definition).
"""

# ============================================
# Imports from each module
# ============================================

from .alerts import AlertSeverity, AlertStatus
from .classification import DataClassification
from .dashboard import DashboardStatus, RecoveryState
from .detection import DetectionType
from .engine import EngineName, EngineStatus, EngineType
from .evidence import EvidenceLevel
from .fallback import FallbackReason
from .finding import FindingStatus
from .risk_calculation_source import RiskCalculationSource
from .risk_level import RiskLevel
from .severity import Severity, SeverityRank

# ============================================
# Public API
# ============================================

__all__ = [
    # Alerts
    "AlertSeverity",
    "AlertStatus",
    
    # Classification
    "DataClassification",
    
    # Dashboard
    "DashboardStatus",
    "RecoveryState",
    
    # Detection
    "DetectionType",
    
    # Engine
    "EngineName",
    "EngineStatus",
    "EngineType",
    
    # Evidence
    "EvidenceLevel",
    
    # Fallback
    "FallbackReason",
    
    # Finding
    "FindingStatus",
    
    # Risk
    "RiskCalculationSource",
    "RiskLevel",  # From risk_level.py (canonical)
    
    # Severity
    "Severity",
    "SeverityRank",
]

# ============================================
# Notes
# ============================================

# RiskLevel.UNKNOWN is domain-only, NOT stored in database
# Database uses: CRITICAL, HIGH, MEDIUM, LOW, INFO
# Mapping: UNKNOWN ↔ INFO is pending ADR decision (E2.2A-3)

# Do NOT export from risk.py (duplicate RiskLevel)
# Canonical RiskLevel is in risk_level.py