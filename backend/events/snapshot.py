# backend/events/snapshot.py

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func

from backend.models.event import Snapshot


class SnapshotStrategy(Enum):
    """Strategy untuk mengambil snapshot."""

    NEVER = "never"
    VERSION_INTERVAL = "version_interval"
    TIME_INTERVAL = "time_interval"
    HYBRID = "hybrid"


class SnapshotConfig:
    """Configuration untuk snapshot strategy."""

    def __init__(
        self,
        strategy: SnapshotStrategy = SnapshotStrategy.VERSION_INTERVAL,
        version_interval: int = 100,
        time_interval_minutes: int = 60,
        enabled_aggregate_types: Optional[List[str]] = None,
    ):
        self.strategy = strategy
        self.version_interval = version_interval
        self.time_interval_minutes = time_interval_minutes
        self.enabled_aggregate_types = (
            enabled_aggregate_types or ["CASE", "ENTITY"]
        )


class SnapshotManager:
    """
    Manager untuk snapshot operations.

    Snapshot adalah cache/replay optimization.
    Source of truth tetap event store.

    Canonical persistence contract:
        backend.models.event.Snapshot

    Tenant isolation:
        Semua read/write/delete operation wajib
        dibatasi oleh self.tenant_id.
    """

    def __init__(
        self,
        session: AsyncSession,
        tenant_id: uuid.UUID,
        config: Optional[SnapshotConfig] = None,
    ):
        self.session = session
        self.tenant_id = tenant_id
        self.config = config or SnapshotConfig()

    async def should_take_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        current_version: int,
    ) -> bool:
        """Check if snapshot should be taken."""

        if aggregate_type not in self.config.enabled_aggregate_types:
            return False

        if self.config.strategy == SnapshotStrategy.NEVER:
            return False

        last_snapshot = await self.get_last_snapshot(
            aggregate_id,
            aggregate_type,
        )

        last_version = (
            last_snapshot.snapshot_version
            if last_snapshot
            else 0
        )

        last_time = (
            last_snapshot.created_at
            if last_snapshot
            else None
        )

        if self.config.strategy == SnapshotStrategy.VERSION_INTERVAL:
            return (
                current_version - last_version
            ) >= self.config.version_interval

        if self.config.strategy == SnapshotStrategy.TIME_INTERVAL:
            if last_time:
                delta = datetime.utcnow() - last_time
                return (
                    delta.total_seconds()
                    >= self.config.time_interval_minutes * 60
                )

            return True

        if self.config.strategy == SnapshotStrategy.HYBRID:
            version_check = (
                current_version - last_version
            ) >= self.config.version_interval

            time_check = False

            if last_time:
                delta = datetime.utcnow() - last_time
                time_check = (
                    delta.total_seconds()
                    >= self.config.time_interval_minutes * 60
                )

            return version_check or time_check

        return False

    async def take_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        state: Dict[str, Any],
        version: int,
    ) -> Snapshot:
        """
        Create and store a canonical snapshot.

        Persistence uses the canonical Snapshot ORM.
        """

        snapshot = Snapshot(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            snapshot_version=version,
            snapshot_data=state,
            tenant_id=self.tenant_id,
        )

        self.session.add(snapshot)

        await self.session.commit()
        await self.session.refresh(snapshot)

        # Keep only the most recent snapshots.
        await self._clean_old_snapshots(
            aggregate_id,
            aggregate_type,
            keep_count=10,
        )

        return snapshot

    async def get_last_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
    ) -> Optional[Snapshot]:
        """Get the most recent snapshot for the aggregate."""

        stmt = (
            select(Snapshot)
            .where(
                Snapshot.aggregate_id == aggregate_id,
                Snapshot.aggregate_type == aggregate_type,
                Snapshot.tenant_id == self.tenant_id,
            )
            .order_by(
                Snapshot.snapshot_version.desc()
            )
            .limit(1)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def get_snapshot_at_version(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        version: int,
    ) -> Optional[Snapshot]:
        """
        Get the latest snapshot at or before a target version.
        """

        stmt = (
            select(Snapshot)
            .where(
                Snapshot.aggregate_id == aggregate_id,
                Snapshot.aggregate_type == aggregate_type,
                Snapshot.tenant_id == self.tenant_id,
                Snapshot.snapshot_version <= version,
            )
            .order_by(
                Snapshot.snapshot_version.desc()
            )
            .limit(1)
        )

        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()

    async def _clean_old_snapshots(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        keep_count: int = 10,
    ) -> int:
        """
        Delete old snapshots while retaining the newest N.

        Tenant isolation is mandatory.
        """

        if keep_count < 0:
            raise ValueError("keep_count must be >= 0")

        stmt = (
            select(Snapshot.id)
            .where(
                Snapshot.aggregate_id == aggregate_id,
                Snapshot.aggregate_type == aggregate_type,
                Snapshot.tenant_id == self.tenant_id,
            )
            .order_by(
                Snapshot.snapshot_version.desc()
            )
            .offset(keep_count)
        )

        result = await self.session.execute(stmt)
        ids_to_delete = result.scalars().all()

        if not ids_to_delete:
            return 0

        delete_stmt = delete(Snapshot).where(
            Snapshot.id.in_(ids_to_delete),
            Snapshot.tenant_id == self.tenant_id,
        )

        delete_result = await self.session.execute(delete_stmt)
        await self.session.commit()

        return delete_result.rowcount or 0

    async def restore_from_snapshot(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Restore aggregate state from the latest snapshot."""

        snapshot = await self.get_last_snapshot(
            aggregate_id,
            aggregate_type,
        )

        if not snapshot:
            return None

        return snapshot.snapshot_data


class HybridReplayService:
    """
    Replay service with snapshot optimization.

    Snapshot remains a cache. Events remain the source of truth.
    """

    def __init__(
        self,
        event_store,
        snapshot_manager: SnapshotManager,
        replay_service,
    ):
        self.event_store = event_store
        self.snapshot_manager = snapshot_manager
        self.replay_service = replay_service

    async def replay_aggregate_optimized(
        self,
        aggregate_id: uuid.UUID,
        aggregate_type: str,
        target_version: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Replay aggregate using the latest applicable snapshot.
        """

        snapshot = await self.snapshot_manager.get_snapshot_at_version(
            aggregate_id,
            aggregate_type,
            target_version if target_version is not None else 999999,
        )

        if snapshot:
            events = await self.event_store.get_events(
                aggregate_id=aggregate_id,
                aggregate_type=aggregate_type,
                from_version=snapshot.snapshot_version,
            )

            state = snapshot.snapshot_data

            for event in events:
                if (
                    target_version is not None
                    and event.event_version > target_version
                ):
                    break

                state = await self.replay_service._apply_event_to_state(
                    state,
                    event,
                )

            return state

        return await self.replay_service.replay_aggregate(
            aggregate_id,
            aggregate_type,
            target_version,
        )