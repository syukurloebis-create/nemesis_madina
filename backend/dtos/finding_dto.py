"""
Finding DTO - Data Transfer Objects (IMMUTABLE)
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class FindingDTO:
    """Finding data transfer object - IMMUTABLE."""
    id: str
    title: str
    description: str
    finding_type: str
    severity: str
    status: str
    detection_method: str
    anomaly_score: float
    confidence: float
    risk_score: float
    created_at: datetime


@dataclass(frozen=True)
class TimelineEventDTO:
    """Timeline event data transfer object - IMMUTABLE."""
    id: str
    finding_id: str
    event: str
    old_status: Optional[str]
    new_status: Optional[str]
    actor: str
    notes: Optional[str]
    created_at: datetime


@dataclass(frozen=True)
class EvidenceDTO:
    """Evidence data transfer object - IMMUTABLE."""
    id: str
    finding_id: str
    title: str
    status: str
    confidence_score: float
    created_at: datetime


@dataclass(frozen=True)
class DecisionDTO:
    """Decision data transfer object - IMMUTABLE."""
    id: str
    finding_id: str
    status: str
    confidence: float
    actor: Optional[str]
    created_at: datetime


@dataclass(frozen=True)
class ActionLogDTO:
    """Action log data transfer object - IMMUTABLE."""
    id: str
    finding_id: str
    action_type: str
    actor: str
    created_at: datetime


@dataclass(frozen=True)
class SLADTO:
    """SLA event data transfer object - IMMUTABLE."""
    id: str
    finding_id: str
    event_type: str
    created_at: datetime