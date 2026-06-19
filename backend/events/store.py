# backend/events/store.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from typing import List, Optional, Dict, Any
import uuid
import hashlib
import json

from .base import BaseEvent, EventMetadata
from .registry import AggregateType, EventType
from ..models.event import Event as EventModel


class EventStore:
    """Event store untuk menyimpan dan mengambil events"""
    
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self.session = session
        self.tenant_id = tenant_id
    
    async def append(self, event: BaseEvent) -> EventModel:
        """Simpan event ke event store"""
        
        # Compute hash
        event.event_hash = event.compute_hash()
        
        # Get previous hash from last event of this aggregate
        previous_hash = await self._get_last_hash(
            event.aggregate_type,
            event.aggregate_id
        )
        event.previous_hash = previous_hash
        
        # Create event model
        event_model = EventModel(
            id=event.event_id,
            aggregate_id=event.aggregate_id,
            aggregate_type=event.aggregate_type,
            event_type=event.event_type,
            event_version=event.event_version,
            event_hash=event.event_hash,
            previous_hash=event.previous_hash,
            payload=event.payload,
            metadata=event.metadata.dict(),
            created_at=event.metadata.timestamp,
            created_by=event.metadata.actor_id,
            tenant_id=self.tenant_id
        )
        
        self.session.add(event_model)
        await self.session.flush()
        
        return event_model
    
    async def _get_last_hash(self, aggregate_type: str, aggregate_id: uuid.UUID) -> Optional[str]:
        """Get hash dari event terakhir aggregate"""
        result = await self.session.execute(
            select(EventModel.event_hash)
            .where(
                EventModel.aggregate_type == aggregate_type,
                EventModel.aggregate_id == aggregate_id
            )
            .order_by(EventModel.created_at.desc())
            .limit(1)
        )
        last = result.scalar_one_or_none()
        return last
    
    async def get_events(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: Optional[str] = None,
        from_version: int = 0,
        limit: int = 100
    ) -> List[EventModel]:
        """Get events untuk suatu aggregate"""
        query = select(EventModel).where(
            EventModel.aggregate_id == aggregate_id,
            EventModel.tenant_id == self.tenant_id
        )
        
        if aggregate_type:
            query = query.where(EventModel.aggregate_type == aggregate_type)
        
        query = query.where(EventModel.event_version > from_version)
        query = query.order_by(EventModel.commit_position).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_events_by_type(
        self,
        event_type: str,
        limit: int = 100
    ) -> List[EventModel]:
        """Get events by type"""
        query = select(EventModel).where(
            EventModel.event_type == event_type,
            EventModel.tenant_id == self.tenant_id
        ).order_by(EventModel.created_at.desc()).limit(limit)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def replay_aggregate(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str
    ) -> Dict[str, Any]:
        """Replay semua events untuk rebuild state"""
        events = await self.get_events(aggregate_id, aggregate_type)
        
        state = {}
        for event in events:
            # Apply event to state
            event_type = event.event_type
            payload = event.payload
            
            if event_type == EventType.CASE_CREATED:
                state["title"] = payload.get("title")
                state["description"] = payload.get("description")
                state["priority"] = payload.get("priority")
            elif event_type == EventType.CASE_STATUS_CHANGED:
                state["status"] = payload.get("new_status")
            elif event_type == EventType.CASE_PRIORITY_CHANGED:
                state["priority"] = payload.get("new_priority")
            # ... other event types
        
        return state
    
    async def verify_chain_integrity(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str
    ) -> Dict[str, Any]:
        """Verifikasi hash chain integrity"""
        events = await self.get_events(aggregate_id, aggregate_type)
        
        is_valid = True
        broken_at = None
        
        for i, event in enumerate(events):
            # Recompute hash
            # Simplified: actual implementation needs to rebuild event from stored data
            if i > 0:
                prev_event = events[i-1]
                if event.previous_hash != prev_event.event_hash:
                    is_valid = False
                    broken_at = i
                    break
        
        return {
            "aggregate_id": str(aggregate_id),
            "aggregate_type": aggregate_type,
            "total_events": len(events),
            "chain_intact": is_valid,
            "broken_at_version": broken_at
        }