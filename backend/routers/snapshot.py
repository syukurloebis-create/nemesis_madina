# backend/routers/snapshot.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional

from backend.infrastructure.database import get_db
from backend.services.snapshot_service import SnapshotService
from backend.cases.event_store import EventStore
from backend.dependencies.auth import require_permission
from backend.domain.enums.permission import Permission

router = APIRouter(prefix="/snapshots", tags=["Snapshots"])


@router.post("/case/{case_id}")
async def create_snapshot(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_permission(Permission.CASE_UPDATE))
):
    """Create a snapshot for a case"""
    
    # Check if case exists
    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Rebuild aggregate to get current state
    event_service = EventStore(db)
    aggregate = await event_service.rebuild_aggregate(case_id)
    
    if not aggregate:
        raise HTTPException(status_code=404, detail="No events found for this case")
    
    # Create snapshot
    snapshot_service = SnapshotService(db)
    snapshot = await snapshot_service.create_snapshot(aggregate)
    
    return {
        "case_id": case_id,
        "snapshot_id": snapshot.id,
        "version": snapshot.version,
        "created_at": snapshot.created_at.isoformat() if snapshot.created_at else None,
        "message": "Snapshot created successfully"
    }


@router.get("/case/{case_id}/latest")
async def get_latest_snapshot(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_permission(Permission.CASE_VIEW))
):
    """Get latest snapshot for a case"""
    
    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")
    
    snapshot_service = SnapshotService(db)
    snapshot = await snapshot_service.get_latest_snapshot(case_id)
    
    if not snapshot:
        raise HTTPException(status_code=404, detail="No snapshot found for this case")
    
    return snapshot


@router.get("/case/{case_id}/version/{version}")
async def get_snapshot_at_version(
    case_id: str,
    version: int,
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_permission(Permission.CASE_VIEW))
):
    """Get snapshot at specific version"""
    
    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")
    
    snapshot_service = SnapshotService(db)
    snapshot = await snapshot_service.get_snapshot_at_version(case_id, version)
    
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"No snapshot found for version {version}")
    
    return snapshot


@router.get("/case/{case_id}")
async def list_snapshots(
    case_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_permission(Permission.CASE_VIEW))
):
    """List all snapshots for a case"""
    
    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")
    
    snapshot_service = SnapshotService(db)
    snapshots = await snapshot_service.get_snapshots_for_aggregate(case_id, limit, offset)
    
    return {
        "case_id": case_id,
        "total": len(snapshots),
        "limit": limit,
        "offset": offset,
        "snapshots": [s for s in snapshots]
    }


@router.delete("/case/{case_id}/old")
async def delete_old_snapshots(
    case_id: str,
    keep_count: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_permission(Permission.CASE_UPDATE))
):
    """Delete old snapshots, keeping only the most recent ones"""
    
    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")
    
    snapshot_service = SnapshotService(db)
    deleted = await snapshot_service.delete_old_snapshots(case_id, keep_count)
    
    return {
        "case_id": case_id,
        "deleted_count": deleted,
        "kept_count": keep_count,
        "message": f"Deleted {deleted} old snapshots"
    }


@router.get("/case/{case_id}/stats")
async def get_snapshot_stats(
    case_id: str,
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_permission(Permission.CASE_VIEW))
):
    """Get snapshot statistics for a case"""
    
    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")
    
    snapshot_service = SnapshotService(db)
    stats = await snapshot_service.get_snapshot_stats(case_id)
    
    return stats


@router.post("/case/{case_id}/auto")
async def create_auto_snapshot(
    case_id: str,
    interval: int = Query(50, ge=10, le=200),
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_permission(Permission.CASE_UPDATE))
):
    """Create snapshot automatically if needed (every N events)"""
    
    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")
    
    event_service = EventStore(db)
    snapshot_service = SnapshotService(db)
    
    # Get latest snapshot
    latest_snapshot = await snapshot_service.get_latest_snapshot(case_id)
    start_version = latest_snapshot.version if latest_snapshot else 0
    
    # Get current version from events
    events = await event_service.get_events_for_case(case_id)
    current_version = events[-1]["version"] if events else 0
    
    if current_version - start_version >= interval:
        # Create new snapshot
        aggregate = await event_service.rebuild_aggregate(case_id)
        if aggregate:
            snapshot = await snapshot_service.create_snapshot(aggregate)
            return {
                "case_id": case_id,
                "snapshot_created": True,
                "snapshot_id": snapshot.id,
                "version": snapshot.version,
                "events_since_last": current_version - start_version,
                "message": f"Snapshot created at version {snapshot.version}"
            }
    
    return {
        "case_id": case_id,
        "snapshot_created": False,
        "events_since_last": current_version - start_version,
        "threshold": interval,
        "message": "No snapshot needed"
    }
