"""
Audit Logging System
Merekam semua aktivitas untuk kepentingan audit dan compliance
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from uuid import UUID, uuid4
import json
import logging

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Action types untuk audit"""
    # Authentication
    LOGIN = "auth.login"
    LOGOUT = "auth.logout"
    LOGIN_FAILED = "auth.login_failed"
    TOKEN_REFRESH = "auth.token_refresh"
    PASSWORD_CHANGE = "auth.password_change"

    # Case Management
    CASE_CREATED = "case.created"
    CASE_UPDATED = "case.updated"
    CASE_DELETED = "case.deleted"
    CASE_VIEWED = "case.viewed"
    CASE_STATUS_CHANGED = "case.status_changed"
    CASE_ASSIGNED = "case.assigned"

    # Evidence
    EVIDENCE_ADDED = "evidence.added"
    EVIDENCE_UPDATED = "evidence.updated"
    EVIDENCE_VERIFIED = "evidence.verified"
    EVIDENCE_DELETED = "evidence.deleted"
    EVIDENCE_VIEWED = "evidence.viewed"

    # Intelligence
    AI_RECOMMENDATION_CREATED = "ai.recommendation_created"
    AI_RECOMMENDATION_APPROVED = "ai.recommendation_approved"
    AI_RECOMMENDATION_REJECTED = "ai.recommendation_rejected"
    AI_SCORE_CALCULATED = "ai.score_calculated"
    AI_PREDICTION_GENERATED = "ai.prediction_generated"

    # Graph
    GRAPH_ENTITY_ADDED = "graph.entity_added"
    GRAPH_ENTITY_UPDATED = "graph.entity_updated"
    GRAPH_EDGE_ADDED = "graph.edge_added"
    GRAPH_ANALYSIS_RUN = "graph.analysis_run"
    COLLUSION_DETECTED = "graph.collusion_detected"

    # User Management
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_ROLE_CHANGED = "user.role_changed"

    # System
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    SYSTEM_WARNING = "system.warning"


@dataclass
class AuditEvent:
    """Audit event record"""
    id: UUID = field(default_factory=uuid4)
    action: Optional[AuditAction] = None
    actor_id: Optional[str] = None
    actor_name: Optional[str] = None
    actor_role: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    changes: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "action": self.action.value if self.action else None,
            "actor_id": self.actor_id,
            "actor_name": self.actor_name,
            "actor_role": self.actor_role,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "resource_name": self.resource_name,
            "changes": self.changes,
            "metadata": self.metadata,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "status": self.status,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat()
        }

    def to_json(self) -> str:
        """Convert to JSON"""
        return json.dumps(self.to_dict(), default=str)


class AuditLogger:
    """Audit logging service"""

    def __init__(self):
        self.events: List[AuditEvent] = []
        self._storage = None
        self.enabled = True

    def log(
        self,
        action: AuditAction,
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None,
        actor_role: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> Optional[AuditEvent]:
        """Log an audit event"""
        if not self.enabled:
            return None

        event = AuditEvent(
            action=action,
            actor_id=actor_id,
            actor_name=actor_name,
            actor_role=actor_role,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            changes=changes,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_id=request_id,
            status=status,
            error_message=error_message
        )

        self.events.append(event)

        # Log to console
        logger.info(f"AUDIT: {action.value} | {actor_name or actor_id} | {resource_type} | {status}")

        self._save_event(event)
        return event

    def _save_event(self, event: AuditEvent) -> None:
        """Save event to storage"""
        logger.debug(f"Audit event saved: {event.id}")

    def log_error(
        self,
        action: AuditAction,
        error_message: str,
        actor_id: Optional[str] = None,
        actor_name: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AuditEvent:
        """Log an error event"""
        return self.log(
            action=action,
            actor_id=actor_id,
            actor_name=actor_name,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata,
            status="error",
            error_message=error_message,
            **kwargs
        )

    def get_events(
        self,
        action: Optional[AuditAction] = None,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """Get audit events with filters"""
        events = self.events

        if action:
            events = [e for e in events if e.action == action]
        if actor_id:
            events = [e for e in events if e.actor_id == actor_id]
        if resource_type:
            events = [e for e in events if e.resource_type == resource_type]
        if resource_id:
            events = [e for e in events if e.resource_id == resource_id]
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]

        return events[:limit]

    def get_stats(self) -> Dict[str, Any]:
        """Get audit statistics"""
        total = len(self.events)
        by_action = {}
        by_status = {"success": 0, "error": 0}
        by_actor = {}

        for event in self.events:
            action_key = event.action.value if event.action else "unknown"
            by_action[action_key] = by_action.get(action_key, 0) + 1
            by_status[event.status] = by_status.get(event.status, 0) + 1
            actor_key = event.actor_name or event.actor_id or "system"
            by_actor[actor_key] = by_actor.get(actor_key, 0) + 1

        return {
            "total_events": total,
            "by_action": by_action,
            "by_status": by_status,
            "by_actor": by_actor,
            "last_hour": len([e for e in self.events if (datetime.now() - e.timestamp).seconds < 3600]),
            "last_day": len([e for e in self.events if (datetime.now() - e.timestamp).days < 1])
        }

    def export_to_report(self) -> Dict[str, Any]:
        """Export audit data to report format"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_stats(),
            "recent_events": [e.to_dict() for e in self.events[-50:]]
        }


# Singleton instance
audit_logger = AuditLogger()
