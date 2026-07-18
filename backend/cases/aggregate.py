"""Case aggregate with event sourcing"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from backend.events.types import Event, EventType


class CaseState(BaseModel):
    """Current state of a case reconstructed from events"""
    case_id: str
    title: str
    description: str = ""
    status: str = "draft"
    assigned_to: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    finding_ids: List[str] = Field(default_factory=list)
    current_version: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "case_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Fraud Investigation",
                "status": "active",
                "assigned_to": "investigator_01",
                "evidence_ids": ["evid_001", "evid_002"],
                "finding_ids": ["find_001"],
                "current_version": 5
            }
        }


class CaseAggregate:
    """Case aggregate that rebuilds state from event history"""
    
    def __init__(self, events: Optional[List[Event]] = None):
        self._events = events or []
        self._state: Optional[CaseState] = None
        
        if self._events:
            self._rebuild_state()
    
    def _rebuild_state(self) -> None:
        """Rebuild aggregate state from all events"""
        if not self._events:
            return
        
        # Sort events by version
        sorted_events = sorted(self._events, key=lambda e: e.version)
        
        state = None
        for event in sorted_events:
            state = self._apply_event(state, event)
        
        self._state = state
    
    def _apply_event(
        self, 
        state: Optional[CaseState], 
        event: Event
    ) -> CaseState:
        """Apply a single event to the current state"""
        
        # First event must be CASE_CREATED
        if state is None:
            if event.event_type != EventType.CASE_CREATED:
                raise ValueError(
                    f"Cannot apply {event.event_type} without existing state"
                )
            
            return CaseState(
                case_id=event.case_id,
                title=event.data.get("title", ""),
                description=event.data.get("description", ""),
                status="draft",
                assigned_to=None,
                evidence_ids=[],
                finding_ids=[],
                current_version=event.version
            )
        
        # Apply event to existing state
        if event.event_type == EventType.CASE_ASSIGNED:
            state.assigned_to = event.data.get("assignee")
            state.status = "active"
            
        elif event.event_type == EventType.STATUS_CHANGED:
            state.status = event.data.get("new_status", state.status)
            
        elif event.event_type == EventType.EVIDENCE_ADDED:
            evidence_id = event.data.get("evidence_id")
            if evidence_id and evidence_id not in state.evidence_ids:
                state.evidence_ids.append(evidence_id)
                
        elif event.event_type == EventType.FINDING_CREATED:
            finding_id = event.data.get("finding_id")
            if finding_id and finding_id not in state.finding_ids:
                state.finding_ids.append(finding_id)
                
        elif event.event_type == EventType.CASE_CLOSED:
            state.status = "closed"
        
        # Update version
        state.current_version = event.version
        
        return state
    
    def get_state(self) -> Optional[CaseState]:
        """Get current aggregate state"""
        return self._state
    
    def get_events(self) -> List[Event]:
        """Get all events in the aggregate"""
        return self._events
    
    @property
    def version(self) -> int:
        """Get current version number"""
        return self._state.current_version if self._state else 0
    
    @property
    def is_dirty(self) -> bool:
        """Check if aggregate has uncommitted changes"""
        return len(self._events) > (self._state.current_version if self._state else 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert aggregate to dictionary for API response"""
        if not self._state:
            return {}
        
        return {
            "case_id": self._state.case_id,
            "title": self._state.title,
            "description": self._state.description,
            "status": self._state.status,
            "assigned_to": self._state.assigned_to,
            "evidence_count": len(self._state.evidence_ids),
            "finding_count": len(self._state.finding_ids),
            "version": self._state.current_version,
            "total_events": len(self._events)
        }
