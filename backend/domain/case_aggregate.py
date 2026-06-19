# backend/domain/case_aggregate.py
from typing import Dict, Any, Optional, List  # ← TAMBAHKAN
from datetime import datetime
import uuid

from .aggregate_root import AggregateRoot


class CaseAggregate(AggregateRoot):
    """Case aggregate with domain logic"""
    
    def __init__(self, case_id: uuid.UUID):
        super().__init__(case_id)
        self.title: Optional[str] = None
        self.description: Optional[str] = None
        self.status: str = "DRAFT"
        self.priority: str = "MEDIUM"
        self.assigned_to: Optional[str] = None
        self.tags: List[str] = []
        self.closed_at: Optional[datetime] = None
    
    def create(self, title: str, description: str, created_by: str):
        """Create new case"""
        self.add_event(
            event_type="CASE_CREATED",
            payload={
                "title": title,
                "description": description,
                "created_by": created_by,
                "created_at": datetime.utcnow().isoformat()
            },
            metadata={"actor_id": created_by}
        )
    
    def update(self, title: str = None, description: str = None, actor_id: str = None):
        """Update case information"""
        updates = {}
        if title and title != self.title:
            updates["title"] = title
        if description and description != self.description:
            updates["description"] = description
        
        if updates:
            self.add_event(
                event_type="CASE_UPDATED",
                payload=updates,
                metadata={"actor_id": actor_id or "system"}
            )
    
    def change_status(self, new_status: str, reason: str, actor_id: str):
        """Change case status"""
        valid_statuses = ["DRAFT", "OPEN", "IN_PROGRESS", "ON_HOLD", "CLOSED", "ARCHIVED"]
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}")
        
        self.add_event(
            event_type="CASE_STATUS_CHANGED",
            payload={
                "old_status": self.status,
                "new_status": new_status,
                "reason": reason,
                "changed_at": datetime.utcnow().isoformat()
            },
            metadata={"actor_id": actor_id}
        )
    
    def assign(self, assignee_id: str, assigned_by: str):
        """Assign case to investigator"""
        self.add_event(
            event_type="CASE_ASSIGNED",
            payload={
                "assigned_to": assignee_id,
                "assigned_by": assigned_by,
                "assigned_at": datetime.utcnow().isoformat()
            },
            metadata={"actor_id": assigned_by}
        )
    
    def close(self, reason: str, closed_by: str):
        """Close case"""
        if self.status == "CLOSED":
            raise ValueError("Case already closed")
        
        self.add_event(
            event_type="CASE_CLOSED",
            payload={
                "reason": reason,
                "closed_by": closed_by,
                "closed_at": datetime.utcnow().isoformat()
            },
            metadata={"actor_id": closed_by}
        )
    
    def _apply_event(self, event: Dict[str, Any]):
        """Apply event to aggregate state"""
        event_type = event['event_type']
        payload = event['payload']
        
        if event_type == "CASE_CREATED":
            self.title = payload.get('title')
            self.description = payload.get('description')
            self.status = "OPEN"
        
        elif event_type == "CASE_UPDATED":
            if 'title' in payload:
                self.title = payload['title']
            if 'description' in payload:
                self.description = payload['description']
        
        elif event_type == "CASE_STATUS_CHANGED":
            self.status = payload.get('new_status', self.status)
        
        elif event_type == "CASE_ASSIGNED":
            self.assigned_to = payload.get('assigned_to')
        
        elif event_type == "CASE_CLOSED":
            self.status = "CLOSED"
            if payload.get('closed_at'):
                self.closed_at = datetime.fromisoformat(payload.get('closed_at'))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregate to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "tags": self.tags,
            "version": self.version,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None
        }