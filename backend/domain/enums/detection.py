# backend/domain/enums/detection.py
"""
Detection Domain Enums

Matches PostgreSQL ENUM 'detectiontype' values.
"""

import enum


class DetectionType(str, enum.Enum):
    """Detection type. Matches PostgreSQL ENUM 'detectiontype'."""
    
    STATISTICAL = "STATISTICAL"
    GRAPH = "GRAPH"
    ML = "ML"
    RULE = "RULE"
    TEMPORAL = "TEMPORAL"