"""
Risk Level Enum.
"""

from enum import Enum


class RiskLevel(str, Enum):
    """Risk level untuk risk score."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"