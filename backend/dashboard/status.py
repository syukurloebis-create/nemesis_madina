# backend/dashboard/status.py

from enum import StrEnum


class DashboardStatus(StrEnum):
    """Dashboard overall status."""
    EMPTY = "EMPTY"
    OK = "OK"
    PARTIAL = "PARTIAL"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"
