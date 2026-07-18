# backend/domain/event_sourcing_repository.py
from typing import Optional, List, Dict, Any  # ← TAMBAHKAN
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid
import json
import logging

from .aggregate_root import AggregateRoot
from backend.events.repository import EventRepository

logger = logging.getLogger(__name__)


class EventSourcingRepository:
    """Repository for saving and loading aggregates using event sourcing"""
    
    def __init__(self, session: AsyncSession, tenant_id: str = None):
        self.session = session
        self.event_repo = EventRepository(session, tenant_id)
    
    async def save(self, aggregate: AggregateRoot):
        """Save aggregate pending events"""
        if not aggregate.has_pending_events:
            return
        
        for event in aggregate.get_pending_events():
            await self.event_repo.append(
                aggregate_id=str(aggregate.id),
                aggregate_type=aggregate.__class__.__name__,
                event_type=event['event_type'],
                payload=event['payload'],
                metadata=event.get('metadata', {}),
                created_by=event['metadata'].get('actor_id')
            )
        
        aggregate.clear_pending_events()
        logger.debug(f"Saved {len(aggregate.get_pending_events())} events for aggregate {aggregate.id}")
    
    async def load(self, aggregate_class, aggregate_id: str) -> Optional[AggregateRoot]:
        """Load aggregate from event history"""
        events = await self.event_repo.get_events(aggregate_id)
        
        if not events:
            return None
        
        aggregate = aggregate_class(uuid.UUID(aggregate_id))
        aggregate.load_from_history(events)
        
        return aggregate