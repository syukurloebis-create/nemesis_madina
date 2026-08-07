# backend/domain/enums/alerts.py
"""
Alert Domain Enums

Matches PostgreSQL ENUM 'alertseverity' and 'alertstatus' values.
"""

import enum


class AlertSeverity(str, enum.Enum):
    """Alert severity. Matches PostgreSQL ENUM 'alertseverity'."""
    
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AlertStatus(str, enum.Enum):
    """Alert status. Matches PostgreSQL ENUM 'alertstatus'."""
    
    PENDING = "PENDING"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"
    DISMISSED = "DISMISSED"