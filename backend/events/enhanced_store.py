# backend/events/enhanced_store.py
from typing import Optional, Dict, Any, List
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from .store import EventStore
from .versioning import EventVersionManager, VersionedEvent
from .tracing import TraceManager
from .replay import ReplayService
from .snapshot import SnapshotManager, HybridReplayService, SnapshotConfig


class EnhancedEventStore(EventStore):
    """Event store dengan versioning, tracing, dan snapshot support"""
    
    def __init__(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        snapshot_config: SnapshotConfig = None
    ):
        super().__init__(session, tenant_id)
        self.version_manager = EventVersionManager()
        self.trace_manager = TraceManager()
        self.snapshot_manager = SnapshotManager(session, snapshot_config)
        self.replay_service = ReplayService(self)
        self.hybrid_replay = HybridReplayService(
            self, self.snapshot_manager, self.replay_service
        )
    
    async def append_with_trace(self, event, trace_context=None):
        """Append event with tracing context"""
        
        if not trace_context:
            trace_context = self.trace_manager.get_current_context()
        
        if trace_context:
            # Add tracing info to metadata
            if not hasattr(event, 'metadata'):
                event.metadata = {}
            event.metadata['correlation_id'] = str(trace_context.correlation_id)
            event.metadata['causation_id'] = str(trace_context.causation_id) if trace_context.causation_id else None
        
        # Store event
        event_model = await self.append(event)
        
        # Check if snapshot should be taken
        should_snapshot = await self.snapshot_manager.should_take_snapshot(
            event.aggregate_id,
            event.aggregate_type,
            event.event_version
        )
        
        if should_snapshot:
            # Rebuild state and take snapshot
            state = await self.hybrid_replay.replay_aggregate_optimized(
                event.aggregate_id,
                event.aggregate_type
            )
            await self.snapshot_manager.take_snapshot(
                event.aggregate_id,
                event.aggregate_type,
                state,
                event.event_version
            )
        
        return event_model
    
    async def get_with_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str
    ) -> Dict[str, Any]:
        """Get aggregate state using snapshot optimization"""
        
        return await self.hybrid_replay.replay_aggregate_optimized(
            aggregate_id, aggregate_type
        )
    
    async def get_version_history(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str
    ) -> List[Dict[str, Any]]:
        """Get version history dengan snapshot info"""
        
        events = await self.get_events(aggregate_id, aggregate_type)
        snapshots = []
        
        # Get snapshots for this aggregate
        result = await self.session.execute(
            text("""
                SELECT snapshot_version, created_at
                FROM snapshots
                WHERE aggregate_id = :aggregate_id
                  AND aggregate_type = :aggregate_type
                  AND tenant_id = :tenant_id
                ORDER BY snapshot_version DESC
            """),
            {
                "aggregate_id": aggregate_id,
                "aggregate_type": aggregate_type,
                "tenant_id": self.tenant_id
            }
        )
        snapshot_rows = result.fetchall()
        snapshot_versions = {row[0]: row[1] for row in snapshot_rows}
        
        history = []
        for event in events:
            history.append({
                "event_id": str(event.id),
                "event_type": event.event_type,
                "event_version": event.event_version,
                "created_at": event.created_at.isoformat(),
                "has_snapshot": event.event_version in snapshot_versions,
                "snapshot_created_at": snapshot_versions[event.event_version].isoformat() 
                    if event.event_version in snapshot_versions else None
            })
        
        return history