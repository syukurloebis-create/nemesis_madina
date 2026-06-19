# backend/domain/event_handlers.py
from typing import Any, Dict
from backend.domain.event_registry import get_event_registry, handles, EventType
from backend.domain.aggregates.case_aggregate import CaseAggregate, CaseStatus
import logging

logger = logging.getLogger(__name__)


# =========================================================
# Case Event Handlers
# =========================================================

@handles(EventType.CASE_CREATED.value)
def handle_case_created(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle CaseCreated event"""
    aggregate.title = data.get("title", "")
    aggregate.description = data.get("description", "")
    aggregate.status = CaseStatus.OPEN
    
    priority_str = data.get("priority", "medium")
    try:
        from backend.domain.aggregates.case_aggregate import CasePriority
        aggregate.priority = CasePriority(priority_str.lower())
    except ValueError:
        pass
    
    logger.debug(f"Case {aggregate.id} created")


@handles(EventType.CASE_ASSIGNED.value)
def handle_case_assigned(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle CaseAssigned event"""
    aggregate.assigned_to = data.get("assignee")
    aggregate.status = CaseStatus.ASSIGNED
    logger.debug(f"Case {aggregate.id} assigned to {aggregate.assigned_to}")


@handles(EventType.EVIDENCE_ADDED.value)
def handle_evidence_added(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle EvidenceAdded event"""
    evidence_id = data.get("evidence_id")
    if evidence_id and evidence_id not in aggregate.evidence_ids:
        aggregate.evidence_ids.append(evidence_id)
        aggregate.evidence_count = len(aggregate.evidence_ids)
        aggregate.status = CaseStatus.INVESTIGATING
    logger.debug(f"Evidence {evidence_id} added to case {aggregate.id}")


@handles(EventType.EVIDENCE_VERIFIED.value)
def handle_evidence_verified(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle EvidenceVerified event"""
    evidence_id = data.get("evidence_id")
    # Update evidence verification status (implementation depends on evidence service)
    logger.debug(f"Evidence {evidence_id} verified in case {aggregate.id}")


@handles(EventType.FINDING_CREATED.value)
def handle_finding_created(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle FindingCreated event"""
    finding_id = data.get("finding_id")
    if finding_id and finding_id not in aggregate.finding_ids:
        aggregate.finding_ids.append(finding_id)
        aggregate.finding_count = len(aggregate.finding_ids)
    logger.debug(f"Finding {finding_id} created for case {aggregate.id}")


@handles(EventType.STATUS_CHANGED.value)
def handle_status_changed(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle StatusChanged event"""
    new_status = data.get("new_status", "open")
    try:
        aggregate.status = CaseStatus(new_status.lower())
    except ValueError:
        pass
    logger.debug(f"Case {aggregate.id} status changed to {aggregate.status.value}")


@handles(EventType.CASE_ESCALATED.value)
def handle_case_escalated(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle CaseEscalated event"""
    aggregate.status = CaseStatus.INVESTIGATING  # Or a more specific status
    logger.debug(f"Case {aggregate.id} escalated")


@handles(EventType.CASE_REVIEWED.value)
def handle_case_reviewed(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle CaseReviewed event"""
    aggregate.status = CaseStatus.VERIFYING
    logger.debug(f"Case {aggregate.id} reviewed")


@handles(EventType.CASE_CLOSED.value)
def handle_case_closed(aggregate: CaseAggregate, data: Dict[str, Any]) -> None:
    """Handle CaseClosed event"""
    aggregate.status = CaseStatus.CLOSED
    logger.debug(f"Case {aggregate.id} closed")


# =========================================================
# Helper function to apply event using registry
# =========================================================

def apply_event_to_aggregate(
    aggregate: CaseAggregate, 
    event_type: str, 
    data: Dict[str, Any]
) -> bool:
    """
    Apply event to aggregate using the event registry.
    Returns True if successful, False otherwise.
    """
    registry = get_event_registry()
    
    # Validate event
    is_valid, error = registry.validate_event(event_type, data)
    if not is_valid:
        logger.error(f"Invalid event {event_type}: {error}")
        return False
    
    # Get handler
    handler = registry.get_handler(event_type)
    if not handler:
        logger.error(f"No handler registered for event type: {event_type}")
        return False
    
    # Apply event
    try:
        handler(aggregate, data)
        return True
    except Exception as e:
        logger.error(f"Error applying event {event_type}: {e}")
        return False


# =========================================================
# Event Factory
# =========================================================

def create_domain_event(
    aggregate_id: str,
    event_type: str,
    data: Dict[str, Any],
    user_id: str
) -> Dict[str, Any]:
    """Create a domain event dictionary for storage"""
    
    from datetime import datetime
    
    return {
        "event_id": None,  # Will be generated by storage
        "case_id": aggregate_id,
        "event_type": event_type,
        "data": data,
        "timestamp": datetime.utcnow(),
        "user_id": user_id,
        "version": 0  # Will be set by event store
    }