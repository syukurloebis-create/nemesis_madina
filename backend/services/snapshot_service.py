"""
Snapshot Service - CACHE ONLY (Canonical Contract)

Snapshot adalah cache dari replay result, BUKAN source of truth.

Canonical persistence contract:
- ORM: backend.models.event.Snapshot
- aggregate_id: UUID
- aggregate_type: str
- snapshot_version: int
- snapshot_data: dict
- tenant_id: UUID (mandatory)
- created_by: UUID | None
- created_at: database-managed timestamp

Phase 1 scope:
- Consolidate SnapshotService onto canonical Snapshot ORM.
- Enforce tenant scoping on every snapshot operation.
- Provide the service methods required by the snapshot router.
- Do not modify router, SnapshotManager, EventEnvelope, or auth/RBAC.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import desc, func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.event import Snapshot


class SnapshotService:
    """
    Snapshot as CACHE, NOT source of truth.

    This service persists and retrieves replay snapshots.
    The event store remains the authoritative source of truth.
    """

    def __init__(self, db: AsyncSession, tenant_id: UUID):
        """
        Args:
            db: Active async database session.
            tenant_id: Mandatory tenant scope supplied by the
                       authenticated caller.
        """
        self.db = db
        self.tenant_id = tenant_id

    async def create_snapshot(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        state: Dict[str, Any],
        version: int,
        created_by: Optional[UUID] = None,
    ) -> Snapshot:
        """
        Create a new snapshot.

        The snapshot stores the replayed aggregate state at the
        supplied aggregate version.
        """
        snapshot = Snapshot(
            aggregate_id=aggregate_id,
            aggregate_type=aggregate_type,
            snapshot_version=version,
            snapshot_data=state,
            tenant_id=self.tenant_id,
            created_by=created_by,
        )

        self.db.add(snapshot)
        await self.db.commit()
        await self.db.refresh(snapshot)

        return snapshot

    async def get_latest_snapshot(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
    ) -> Optional[Snapshot]:
        """
        Get the most recent snapshot for an aggregate.

        Tenant isolation is mandatory.
        """
        stmt = (
            select(Snapshot)
            .where(
                Snapshot.aggregate_id == aggregate_id,
                Snapshot.aggregate_type == aggregate_type,
                Snapshot.tenant_id == self.tenant_id,
            )
            .order_by(desc(Snapshot.snapshot_version))
            .limit(1)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_snapshot_at_version(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        version: int,
    ) -> Optional[Snapshot]:
        """
        Get the latest snapshot at or before the requested version.

        Method name is retained as the router/API contract:
        get_snapshot_at_version().
        """
        stmt = (
            select(Snapshot)
            .where(
                Snapshot.aggregate_id == aggregate_id,
                Snapshot.aggregate_type == aggregate_type,
                Snapshot.tenant_id == self.tenant_id,
                Snapshot.snapshot_version <= version,
            )
            .order_by(desc(Snapshot.snapshot_version))
            .limit(1)
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_snapshots_for_aggregate(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Snapshot]:
        """
        List snapshots for an aggregate.

        Results are ordered newest-first.
        """
        stmt = (
            select(Snapshot)
            .where(
                Snapshot.aggregate_id == aggregate_id,
                Snapshot.aggregate_type == aggregate_type,
                Snapshot.tenant_id == self.tenant_id,
            )
            .order_by(desc(Snapshot.snapshot_version))
            .offset(offset)
            .limit(limit)
        )

        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def delete_old_snapshots(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
        keep_count: int = 10,
    ) -> int:
        """
        Delete snapshots older than the most recent keep_count.

        Selection and deletion are both tenant-scoped.
        """
        stmt = (
            select(Snapshot.id)
            .where(
                Snapshot.aggregate_id == aggregate_id,
                Snapshot.aggregate_type == aggregate_type,
                Snapshot.tenant_id == self.tenant_id,
            )
            .order_by(desc(Snapshot.snapshot_version))
            .offset(keep_count)
        )

        result = await self.db.execute(stmt)
        ids_to_delete = list(result.scalars().all())

        if not ids_to_delete:
            return 0

        await self.db.execute(
            text(
                """
                DELETE FROM snapshots
                WHERE id = ANY(:ids)
                  AND tenant_id = :tenant_id
                """
            ),
            {
                "ids": ids_to_delete,
                "tenant_id": self.tenant_id,
            },
        )

        await self.db.commit()

        return len(ids_to_delete)

    async def get_snapshot_stats(
        self,
        aggregate_id: UUID,
        aggregate_type: str,
    ) -> Dict[str, Any]:
        """
        Get aggregate snapshot statistics.

        Uses SQL aggregation and remains tenant-scoped.
        """
        stmt = (
            select(
                func.count(Snapshot.id).label("total"),
                func.max(Snapshot.snapshot_version).label("latest_version"),
                func.min(Snapshot.snapshot_version).label("oldest_version"),
                func.max(Snapshot.created_at).label("latest_created_at"),
            )
            .where(
                Snapshot.aggregate_id == aggregate_id,
                Snapshot.aggregate_type == aggregate_type,
                Snapshot.tenant_id == self.tenant_id,
            )
        )

        result = await self.db.execute(stmt)
        row = result.fetchone()

        if not row or row.total == 0:
            return {
                "total": 0,
                "latest_version": None,
                "oldest_version": None,
                "latest_created_at": None,
            }

        latest_created_at = row.latest_created_at

        return {
            "total": row.total,
            "latest_version": row.latest_version,
            "oldest_version": row.oldest_version,
            "latest_created_at": (
                latest_created_at.isoformat()
                if isinstance(latest_created_at, datetime)
                else str(latest_created_at)
                if latest_created_at is not None
                else None
            ),
        }