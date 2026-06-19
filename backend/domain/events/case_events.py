# backend/domain/events/case_events.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4

from backend.domain.value_objects import CaseStatus, CasePriority


@dataclass
class DomainEvent:
    """Base class for all domain events"""
    event_id: str
    aggregate_id: str
    event_type: str
    occurred_at: datetime
    version: int
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "aggregate_id": self.aggregate_id,
            "event_type": self.event_type,
            "occurred_at": self.occurred_at.isoformat(),
            "version": self.version,
            "data": self.data
        }


@dataclass
class CaseCreated(DomainEvent):
    """Event when a case is created"""
    def __init__(
        self,
        aggregate_id: str,
        title: str,
        description: Optional[str],
        priority: CasePriority,
        created_by: str,
        institution_id: Optional[str],
        version: int = 1
    ):
        super().__init__(
            event_id=str(uuid4()),
            aggregate_id=aggregate_id,
            event_type="case_created",
            occurred_at=datetime.utcnow(),
            version=version,
            data={
                "title": title,
                "description": description,
                "priority": priority.value,
                "created_by": created_by,
                "institution_id": institution_id
            }
        )


@dataclass
class CaseUpdated(DomainEvent):
    """Event when a case is updated"""
    def __init__(
        self,
        aggregate_id: str,
        changes: Dict[str, Any],
        updated_by: str,
        version: int
    ):
        super().__init__(
            event_id=str(uuid4()),
            aggregate_id=aggregate_id,
            event_type="case_updated",
            occurred_at=datetime.utcnow(),
            version=version,
            data={
                "changes": changes,
                "updated_by": updated_by
            }
        )


@dataclass
class CaseStatusChanged(DomainEvent):
    """Event when case status changes"""
    def __init__(
        self,
        aggregate_id: str,
        old_status: CaseStatus,
        new_status: CaseStatus,
        changed_by: str,
        reason: Optional[str],
        version: int
    ):
        super().__init__(
            event_id=str(uuid4()),
            aggregate_id=aggregate_id,
            event_type="case_status_changed",
            occurred_at=datetime.utcnow(),
            version=version,
            data={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "changed_by": changed_by,
                "reason": reason
            }
        )


@dataclass
class CaseAssigned(DomainEvent):
    """Event when a case is assigned to a user"""
    def __init__(
        self,
        aggregate_id: str,
        assigned_to: str,
        assigned_by: str,
        version: int
    ):
        super().__init__(
            event_id=str(uuid4()),
            aggregate_id=aggregate_id,
            event_type="case_assigned",
            occurred_at=datetime.utcnow(),
            version=version,
            data={
                "assigned_to": assigned_to,
                "assigned_by": assigned_by
            }
        )


@dataclass
class CaseClosed(DomainEvent):
    """Event when a case is closed"""
    def __init__(
        self,
        aggregate_id: str,
        closed_by: str,
        reason: Optional[str],
        resolution: Optional[str],
        version: int
    ):
        super().__init__(
            event_id=str(uuid4()),
            aggregate_id=aggregate_id,
            event_type="case_closed",
            occurred_at=datetime.utcnow(),
            version=version,
            data={
                "closed_by": closed_by,
                "reason": reason,
                "resolution": resolution
            }
        )


def get_case_id(event) -> str:
    """
    Unified accessor for all event types
    """
    return getattr(event, "aggregate_id", None) or getattr(event, "case_id", None)