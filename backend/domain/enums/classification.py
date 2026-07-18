"""
NEMESIS Madina - Data Classification
"""

from enum import Enum


class DataClassification(Enum):
    """Data classification levels for event security."""
    
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    RESTRICTED = "RESTRICTED"
    SECRET = "SECRET"
    
    def __str__(self) -> str:
        return self.value