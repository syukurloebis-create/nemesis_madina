"""
Domain Event Handler untuk True Event Sourcing
Bukan sekadar JSON merge, tapi benar-benar menerapkan business logic
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import json


class CaseAggregate:
    """Aggregate root untuk Case dengan event sourcing"""

    def __init__(self, case_id: str):
        self.id = case_id
        self.title = ""
        self.description = ""
        self.status = "DRAFT"
        self.priority = "MEDIUM"
        self.assigned_to: Optional[str] = None
        self.evidence_list: List[Dict] = []
        self.resolution = ""
        self.version = 0
        self.created_at: Optional[datetime] = None
        self.updated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Konversi aggregate ke dictionary untuk snapshot"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "evidence_list": self.evidence_list,
            "resolution": self.resolution,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, case_id: str, data: Dict[str, Any]) -> "CaseAggregate":
        """Restore aggregate dari dictionary"""
        aggregate = cls(case_id)
        aggregate.title = data.get("title", "")
        aggregate.description = data.get("description", "")
        aggregate.status = data.get("status", "DRAFT")
        aggregate.priority = data.get("priority", "MEDIUM")
        aggregate.assigned_to = data.get("assigned_to")
        aggregate.evidence_list = data.get("evidence_list", [])
        aggregate.resolution = data.get("resolution", "")
        aggregate.version = data.get("version", 0)
        return aggregate

    def apply_case_created(self, data: Dict[str, Any]):
        """Event: Case dibuat"""
        self.title = data.get("title", "")
        self.description = data.get("description", "")
        self.priority = data.get("priority", "MEDIUM").upper()
        self.status = "OPEN"
        self.version = 1
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def apply_case_assigned(self, data: Dict[str, Any]):
        """Event: Case diassign ke investigator"""
        self.assigned_to = data.get("assignee")
        self.status = "INVESTIGATING"
        self.version += 1
        self.updated_at = datetime.now()

    def apply_evidence_added(self, data: Dict[str, Any]):
        """Event: Evidence ditambahkan"""
        evidence = {
            "evidence_id": data.get("evidence_id"),
            "title": data.get("title"),
            "added_by": data.get("added_by"),
            "added_by_username": data.get("added_by_username"),
            "added_at": datetime.now().isoformat()
        }
        self.evidence_list.append(evidence)
        self.version += 1
        self.updated_at = datetime.now()

    def apply_status_changed(self, data: Dict[str, Any]):
        """Event: Status case berubah"""
        old_status = self.status
        self.status = data.get("new_status")
        self.version += 1
        self.updated_at = datetime.now()

    def apply_case_closed(self, data: Dict[str, Any]):
        """Event: Case ditutup"""
        self.status = "CLOSED"
        self.resolution = data.get("resolution", "RESOLVED")
        self.version += 1
        self.updated_at = datetime.now()


class EventApplier:
    """Mengaplikasikan event ke aggregate"""

    @staticmethod
    def apply(aggregate: CaseAggregate, event_type: str, data: Dict[str, Any]) -> CaseAggregate:
        """Apply event berdasarkan event_type"""
        handlers = {
            "case_created": aggregate.apply_case_created,
            "case_assigned": aggregate.apply_case_assigned,
            "evidence_added": aggregate.apply_evidence_added,
            "status_changed": aggregate.apply_status_changed,
            "case_closed": aggregate.apply_case_closed,
        }

        handler = handlers.get(event_type)
        if handler:
            handler(data)
        else:
            print(f"Unknown event type: {event_type}")

        return aggregate

    @staticmethod
    def rebuild_from_events(events: List[Dict]) -> Optional[CaseAggregate]:
        """
        TRUE DOMAIN EVENT SOURCING - Rebuild aggregate dari events
        Menggunakan domain event handler, BUKAN JSON merge!
        """
        if not events:
            return None

        # Initialize aggregate dengan case_id dari event pertama
        aggregate = CaseAggregate(events[0].get("case_id"))

        for event in events:
            EventApplier.apply(
                aggregate,
                event.get("event_type"),
                event.get("data", {})
            )

        return aggregate

    @staticmethod
    def rebuild_from_events_json(events_json: str) -> Optional[CaseAggregate]:
        """Rebuild aggregate dari JSON string events"""
        events = json.loads(events_json) if isinstance(events_json, str) else events_json
        return EventApplier.rebuild_from_events(events)


def rebuild_case_from_events(events: List[Dict]) -> Dict[str, Any]:
    """
    Utility function untuk rebuild case state dari events
    Returns dictionary state yang bisa digunakan oleh API
    """
    aggregate = EventApplier.rebuild_from_events(events)
    if aggregate:
        return aggregate.to_dict()
    return {}
