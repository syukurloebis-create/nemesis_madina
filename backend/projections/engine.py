# backend/projections/engine.py
from typing import Dict, Any, List, Callable, Awaitable
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import asyncio
import logging

logger = logging.getLogger(__name__)


class ProjectionEngine:
    """CQRS projection engine for building read models"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.handlers: Dict[str, List[Callable]] = {}
        self._running = False
    
    def register_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]):
        """Register event handler for projection"""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)
    
    async def process_event(self, event: Dict[str, Any]):
        """Process single event through all registered handlers"""
        event_type = event.get('event_type')
        
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error processing event {event_type}: {e}")
    
    async def rebuild_projection(self, projection_name: str, batch_size: int = 10000):
        """Rebuild projection from event store"""
        logger.info(f"Rebuilding projection: {projection_name}")
        
        # Clear existing projection data
        await self._clear_projection(projection_name)
        
        # Get all events from event store
        last_id = None
        total_processed = 0
        
        from events.repository import EventRepository
        
        while True:
            # Get batch of events
            query = text("""
                SELECT id, event_id, case_id, event_type, data, timestamp, version,
                       user_id, event_hash, previous_hash, commit_position, created_at
                FROM events
                WHERE id > :last_id
                ORDER BY id ASC
                LIMIT :limit
            """)
            
            result = await self.session.execute(query, {
                "last_id": last_id or 0,
                "limit": batch_size
            })
            
            events = result.fetchall()
            if not events:
                break
            
            for row in events:
                event = {
                    "id": row[0],
                    "event_id": str(row[1]),
                    "case_id": str(row[2]),
                    "event_type": row[3],
                    "data": row[4],
                    "timestamp": row[5].isoformat() if row[5] else None,
                    "version": row[6],
                    "user_id": row[7],
                    "event_hash": row[8],
                    "previous_hash": row[9],
                    "commit_position": row[10],
                    "created_at": row[11].isoformat() if row[11] else None
                }
                
                await self.process_event(event)
                last_id = row[0]
                total_processed += 1
                
                if total_processed % 10000 == 0:
                    logger.info(f"Processed {total_processed} events...")
            
            await self.session.commit()
        
        logger.info(f"Rebuild complete. Processed {total_processed} events.")
    
    async def _clear_projection(self, projection_name: str):
        """Clear projection data (implementation depends on projection)"""
        # This would be overridden by specific projections
        pass