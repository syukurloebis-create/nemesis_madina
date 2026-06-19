# backend/domain/value_objects/timeline_event.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class EventSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    FORENSIC = "forensic"


class EventCategory(str, Enum):
    CASE_LIFECYCLE = "case_lifecycle"
    STATUS_CHANGE = "status_change"
    ASSIGNMENT = "assignment"
    EVIDENCE = "evidence"
    FINDING = "finding"
    RISK_UPDATE = "risk_update"
    DECISION = "decision"
    AUDIT = "audit"


@dataclass
class TimelineEvent:
    id: str
    case_id: str
    version: int
    event_type: str
    category: EventCategory
    severity: EventSeverity
    title: str
    description: str
    timestamp: datetime
    created_by: str
    changes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "case_id": self.case_id,
            "version": self.version,
            "event_type": self.event_type,
            "category": self.category.value,
            "severity": self.severity.value,
            "title": self.title,
            "description": self.description,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "created_by": self.created_by,
            "changes": self.changes,
            "metadata": self.metadata
        }
