# backend/domain/event_registry.py
from typing import Dict, Callable, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """Standardized event types"""
    CASE_CREATED = "case_created"
    CASE_ASSIGNED = "case_assigned"
    EVIDENCE_ADDED = "evidence_added"
    EVIDENCE_VERIFIED = "evidence_verified"
    FINDING_CREATED = "finding_created"
    STATUS_CHANGED = "status_changed"
    CASE_ESCALATED = "case_escalated"
    CASE_REVIEWED = "case_reviewed"
    CASE_CLOSED = "case_closed"


@dataclass
class EventMetadata:
    """Metadata for event type"""
    version: int
    handler_name: str
    required_fields: list
    optional_fields: list
    description: str


class EventRegistry:
    """
    Explicit event registry for handling domain events.
    Centralizes event type mapping and validation.
    """
    
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}
        self._metadata: Dict[str, EventMetadata] = {}
        self._register_default_handlers()
    
    def _register_default_handlers(self) -> None:
        """Register all default event handlers"""
        
        # Case Created
        self.register(
            EventType.CASE_CREATED,
            handler_name="handle_case_created",
            required_fields=["title", "priority"],
            optional_fields=["description", "institution_id"],
            description="Emitted when a new case is created"
        )
        
        # Case Assigned
        self.register(
            EventType.CASE_ASSIGNED,
            handler_name="handle_case_assigned",
            required_fields=["assignee"],
            optional_fields=["assigned_by", "role"],
            description="Emitted when a case is assigned to an investigator"
        )
        
        # Evidence Added
        self.register(
            EventType.EVIDENCE_ADDED,
            handler_name="handle_evidence_added",
            required_fields=["evidence_id", "title"],
            optional_fields=["type", "hash", "source"],
            description="Emitted when evidence is added to a case"
        )
        
        # Evidence Verified
        self.register(
            EventType.EVIDENCE_VERIFIED,
            handler_name="handle_evidence_verified",
            required_fields=["evidence_id", "status"],
            optional_fields=["verified_by", "notes"],
            description="Emitted when evidence is verified"
        )
        
        # Finding Created
        self.register(
            EventType.FINDING_CREATED,
            handler_name="handle_finding_created",
            required_fields=["finding_id", "title", "severity"],
            optional_fields=["description", "evidence_ids"],
            description="Emitted when a finding is created"
        )
        
        # Status Changed
        self.register(
            EventType.STATUS_CHANGED,
            handler_name="handle_status_changed",
            required_fields=["old_status", "new_status"],
            optional_fields=["reason", "changed_by"],
            description="Emitted when case status changes"
        )
        
        # Case Escalated
        self.register(
            EventType.CASE_ESCALATED,
            handler_name="handle_case_escalated",
            required_fields=["reason"],
            optional_fields=["escalated_by", "escalated_to"],
            description="Emitted when a case is escalated"
        )
        
        # Case Reviewed
        self.register(
            EventType.CASE_REVIEWED,
            handler_name="handle_case_reviewed",
            required_fields=["reviewer"],
            optional_fields=["comments", "decision"],
            description="Emitted when a case is reviewed"
        )
        
        # Case Closed
        self.register(
            EventType.CASE_CLOSED,
            handler_name="handle_case_closed",
            required_fields=["resolution"],
            optional_fields=["closed_by", "reason"],
            description="Emitted when a case is closed"
        )
    
    def register(
        self,
        event_type: EventType,
        handler_name: str,
        required_fields: list,
        optional_fields: list,
        description: str = ""
    ) -> None:
        """Register an event type with its metadata"""
        
        self._metadata[event_type.value] = EventMetadata(
            version=1,
            handler_name=handler_name,
            required_fields=required_fields,
            optional_fields=optional_fields,
            description=description
        )
        
        logger.debug(f"Registered event type: {event_type.value}")
    
    def register_handler(
        self, 
        event_type: str, 
        handler: Callable
    ) -> None:
        """Register a handler function for an event type"""
        self._handlers[event_type] = handler
        logger.debug(f"Registered handler for: {event_type}")
    
    def get_handler(self, event_type: str) -> Optional[Callable]:
        """Get handler for event type"""
        return self._handlers.get(event_type)
    
    def get_metadata(self, event_type: str) -> Optional[EventMetadata]:
        """Get metadata for event type"""
        return self._metadata.get(event_type)
    
    def validate_event(self, event_type: str, data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate event data against required fields.
        Returns (is_valid, error_message)
        """
        metadata = self._metadata.get(event_type)
        
        if not metadata:
            return False, f"Unknown event type: {event_type}"
        
        # Check required fields
        missing_fields = []
        for field in metadata.required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return False, f"Missing required fields: {', '.join(missing_fields)}"
        
        return True, None
    
    def has_handler(self, event_type: str) -> bool:
        """Check if handler exists for event type"""
        return event_type in self._handlers
    
    def list_event_types(self) -> list:
        """List all registered event types"""
        return list(self._metadata.keys())
    
    def get_event_summary(self) -> dict:
        """Get summary of all registered events"""
        return {
            event_type: {
                "handler": self._metadata[event_type].handler_name,
                "required_fields": self._metadata[event_type].required_fields,
                "optional_fields": self._metadata[event_type].optional_fields,
                "description": self._metadata[event_type].description
            }
            for event_type in self._metadata
        }


# =========================================================
# Singleton instance for global access
# =========================================================

_event_registry: Optional[EventRegistry] = None


def get_event_registry() -> EventRegistry:
    """Get singleton event registry instance"""
    global _event_registry
    if _event_registry is None:
        _event_registry = EventRegistry()
    return _event_registry


# =========================================================
# Decorator for automatic handler registration
# =========================================================

def handles(event_type: str):
    """Decorator to automatically register event handlers"""
    def decorator(func):
        registry = get_event_registry()
        registry.register_handler(event_type, func)
        return func
    return decorator