# backend/events/snapshot.py
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select


class SnapshotStrategy(Enum):
    """Strategy untuk mengambil snapshot"""
    NEVER = "never"           # No snapshots
    VERSION_INTERVAL = "version_interval"  # Every N versions
    TIME_INTERVAL = "time_interval"       # Every N minutes
    HYBRID = "hybrid"         # Combination


class SnapshotConfig:
    """Configuration untuk snapshot strategy"""
    
    def __init__(
        self,
        strategy: SnapshotStrategy = SnapshotStrategy.VERSION_INTERVAL,
        version_interval: int = 100,
        time_interval_minutes: int = 60,
        enabled_aggregate_types: List[str] = None
    ):
        self.strategy = strategy
        self.version_interval = version_interval
        self.time_interval_minutes = time_interval_minutes
        self.enabled_aggregate_types = enabled_aggregate_types or ["CASE", "ENTITY"]


class Snapshot:
    """Snapshot of aggregate state"""
    
    def __init__(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        state: Dict[str, Any],
        version: int,
        snapshot_id: Optional[uuid.UUID] = None,
        created_at: Optional[datetime] = None
    ):
        self.snapshot_id = snapshot_id or uuid.uuid4()
        self.aggregate_id = aggregate_id
        self.aggregate_type = aggregate_type
        self.state = state
        self.version = version
        self.created_at = created_at or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": str(self.snapshot_id),
            "aggregate_id": str(self.aggregate_id),
            "aggregate_type": self.aggregate_type,
            "state": self.state,
            "version": self.version,
            "created_at": self.created_at.isoformat()
        }


class SnapshotManager:
    """Manager untuk snapshot operations"""
    
    def __init__(self, session: AsyncSession, config: SnapshotConfig = None):
        self.session = session
        self.config = config or SnapshotConfig()
    
    async def should_take_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        current_version: int
    ) -> bool:
        """Check if snapshot should be taken"""
        
        if aggregate_type not in (self.config.enabled_aggregate_types or []):
            return False
        
        if self.config.strategy == SnapshotStrategy.NEVER:
            return False
        
        # Get last snapshot version
        last_snapshot = await self.get_last_snapshot(aggregate_id, aggregate_type)
        last_version = last_snapshot.version if last_snapshot else 0
        last_time = last_snapshot.created_at if last_snapshot else None
        
        if self.config.strategy == SnapshotStrategy.VERSION_INTERVAL:
            return (current_version - last_version) >= self.config.version_interval
        
        if self.config.strategy == SnapshotStrategy.TIME_INTERVAL:
            if last_time:
                delta = datetime.utcnow() - last_time
                return delta.total_seconds() >= (self.config.time_interval_minutes * 60)
            return True
        
        if self.config.strategy == SnapshotStrategy.HYBRID:
            version_check = (current_version - last_version) >= self.config.version_interval
            time_check = False
            if last_time:
                delta = datetime.utcnow() - last_time
                time_check = delta.total_seconds() >= (self.config.time_interval_minutes * 60)
            return version_check or time_check
        
        return False
    
    async def take_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        state: Dict[str, Any],
        version: int
    ) -> Snapshot:
        """Create and store snapshot"""
        
        snapshot = Snapshot(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            state=state,
            version=version
        )
        
        # Store in database
        await self.session.execute(
            text("""
                INSERT INTO snapshots (id, aggregate_id, aggregate_type, state, version, created_at)
                VALUES (:id, :aggregate_id, :aggregate_type, :state, :version, :created_at)
            """),
            {
                "id": snapshot.snapshot_id,
                "aggregate_id": snapshot.aggregate_id,
                "aggregate_type": snapshot.aggregate_type,
                "state": snapshot.state,
                "version": snapshot.version,
                "created_at": snapshot.created_at
            }
        )
        
        await self.session.commit()
        
        # Clean old snapshots (keep only last 10)
        await self._clean_old_snapshots(aggregate_id, aggregate_type, keep_count=10)
        
        return snapshot
    
    async def get_last_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str
    ) -> Optional[Snapshot]:
        """Get most recent snapshot"""
        
        result = await self.session.execute(
            text("""
                SELECT id, aggregate_id, aggregate_type, state, version, created_at
                FROM snapshots
                WHERE aggregate_id = :aggregate_id AND aggregate_type = :aggregate_type
                ORDER BY version DESC
                LIMIT 1
            """),
            {
                "aggregate_id": aggregate_id,
                "aggregate_type": aggregate_type
            }
        )
        row = result.fetchone()
        
        if not row:
            return None
        
        return Snapshot(
            snapshot_id=row[0],
            aggregate_id=row[1],
            aggregate_type=row[2],
            state=row[3],
            version=row[4],
            created_at=row[5]
        )
    
    async def get_snapshot_at_version(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        version: int
    ) -> Optional[Snapshot]:
        """Get snapshot at or before specific version"""
        
        result = await self.session.execute(
            text("""
                SELECT id, aggregate_id, aggregate_type, state, version, created_at
                FROM snapshots
                WHERE aggregate_id = :aggregate_id 
                  AND aggregate_type = :aggregate_type
                  AND version <= :version
                ORDER BY version DESC
                LIMIT 1
            """),
            {
                "aggregate_id": aggregate_id,
                "aggregate_type": aggregate_type,
                "version": version
            }
        )
        row = result.fetchone()
        
        if not row:
            return None
        
        return Snapshot(
            snapshot_id=row[0],
            aggregate_id=row[1],
            aggregate_type=row[2],
            state=row[3],
            version=row[4],
            created_at=row[5]
        )
    
    async def _clean_old_snapshots(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        keep_count: int = 10
    ):
        """Delete old snapshots, keep only most recent N"""
        
        await self.session.execute(
            text("""
                DELETE FROM snapshots
                WHERE id IN (
                    SELECT id FROM snapshots
                    WHERE aggregate_id = :aggregate_id 
                      AND aggregate_type = :aggregate_type
                    ORDER BY version DESC
                    OFFSET :keep_count
                )
            """),
            {
                "aggregate_id": aggregate_id,
                "aggregate_type": aggregate_type,
                "keep_count": keep_count
            }
        )
        await self.session.commit()
    
    async def restore_from_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str
    ) -> Optional[Dict[str, Any]]:
        """Restore aggregate state from latest snapshot"""
        
        snapshot = await self.get_last_snapshot(aggregate_id, aggregate_type)
        if not snapshot:
            return None
        
        return snapshot.state


class HybridReplayService:
    """Replay service with snapshot optimization"""
    
    def __init__(self, event_store, snapshot_manager: SnapshotManager, replay_service):
        self.event_store = event_store
        self.snapshot_manager = snapshot_manager
        self.replay_service = replay_service
    
    async def replay_aggregate_optimized(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        target_version: Optional[int] = None
    ) -> Dict[str, Any]:
        """Replay aggregate using snapshot for optimization"""
        
        # Try to load from snapshot
        snapshot = await self.snapshot_manager.get_snapshot_at_version(
            aggregate_id, aggregate_type, target_version or 999999
        )
        
        if snapshot:
            # Replay only events after snapshot
            events = await self.event_store.get_events(
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                from_version=snapshot.version
            )
            
            state = snapshot.state
            for event in events:
                if target_version and event.event_version > target_version:
                    break
                state = await self.replay_service._apply_event_to_state(state, event)
            
            return state
        else:
            # No snapshot, full replay
            return await self.replay_service.replay_aggregate(
                aggregate_id, aggregate_type, target_version
            )