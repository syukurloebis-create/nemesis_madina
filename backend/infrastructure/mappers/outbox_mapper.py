"""
Outbox Mapper — DomainEvent → OutboxModel
✅ Uses event.event_name as single source of truth
✅ Defensive UUID conversion with explicit InvalidAggregateIdError
"""

from typing import Union
from uuid import UUID, uuid4

from backend.domain.events.base import DomainEvent
from backend.infrastructure.models.outbox import OutboxModel, OutboxStatus


class InvalidAggregateIdError(ValueError):
    """Raised when aggregate_id cannot be extracted from an event."""
    pass


class OutboxMapper:
    def _as_uuid(self, value: Union[str, UUID, None]) -> UUID:
        """Convert to UUID with explicit error."""
        if value is None:
            return uuid4()
        if isinstance(value, UUID):
            return value
        try:
            return UUID(str(value))
        except (ValueError, TypeError) as e:
            raise InvalidAggregateIdError(
                f"Invalid UUID value: {value} (type: {type(value).__name__})"
            ) from e

    def _extract_aggregate_id(self, event: DomainEvent) -> UUID:
        """Extract aggregate_id defensively."""
        # 1. Try payload.case_id (modern events)
        payload = getattr(event, 'payload', None)
        if payload is not None:
            case_id = getattr(payload, 'case_id', None)
            if case_id is not None:
                return self._as_uuid(case_id)

        # 2. Try direct case_id (compatibility events)
        case_id = getattr(event, 'case_id', None)
        if case_id is not None:
            return self._as_uuid(case_id)

        # 3. Try metadata (fallback)
        metadata = getattr(event, 'metadata', None)
        if metadata is not None:
            case_id = metadata.get('aggregate_id') or metadata.get('case_id')
            if case_id is not None:
                return self._as_uuid(case_id)

        raise InvalidAggregateIdError(
            f"Could not extract aggregate_id from {event.__class__.__name__}"
        )

    def to_model(self, event: DomainEvent) -> OutboxModel:
        event_id = self._as_uuid(getattr(event, 'event_id', None))
        aggregate_id = self._extract_aggregate_id(event)

        # Use event_name as single source of truth
        event_type = getattr(event, 'event_name', event.__class__.__name__)

        # Use full event envelope
        payload = event.to_dict() if hasattr(event, 'to_dict') else {}

        return OutboxModel(
            id=uuid4(),
            event_id=event_id,
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload,
            status=OutboxStatus.PENDING,
            retry_count=0,
        )