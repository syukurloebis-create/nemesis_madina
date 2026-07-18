"""
Dashboard Enums — Status agregasi dan recovery.
"""

from enum import Enum


class DashboardStatus(str, Enum):
    """Dashboard overall status — hasil aggregasi engine_status."""
    OK = "OK"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"


class RecoveryState(str, Enum):
    """Business state for Recovery engine."""
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"