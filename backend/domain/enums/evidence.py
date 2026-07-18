"""
Evidence Level Enum.
"""

from enum import Enum


class EvidenceLevel(str, Enum):
    """Evidence level untuk evidence score."""
    NO_DATA = "NO_DATA"
    POOR = "POOR"
    MEDIUM = "MEDIUM"
    GOOD = "GOOD"
    EXCELLENT = "EXCELLENT"