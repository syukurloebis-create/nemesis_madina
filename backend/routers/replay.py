# backend/routers/replay.py (temporary without auth for testing)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import datetime

from infrastructure.database import get_db
from services.replay_service import ReplayService

router = APIRouter(prefix="/replay", tags=["Event Replay"])


@router.get("/case/{case_id}/timeline")
async def get_event_timeline(
    case_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get event timeline for a case"""
    service = ReplayService(db)

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    return await service.get_event_timeline(case_id, limit, offset)


@router.get("/case/{case_id}/replay")
async def replay_events(
    case_id: str,
    from_version: Optional[int] = Query(None, ge=1),
    to_version: Optional[int] = Query(None, ge=1),
    speed: float = Query(1.0, ge=0.1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """Replay events for a case"""
    service = ReplayService(db)

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    if from_version is None:
        from_version = 1

    return await service.replay_events(case_id, from_version, to_version, speed)


@router.get("/case/{case_id}/version/{version}")
async def get_event_by_version(
    case_id: str,
    version: int,
    db: AsyncSession = Depends(get_db)
):
    """Get specific event by version"""
    service = ReplayService(db)

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    event = await service.get_event_by_version(case_id, version)
    if not event:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")

    return event


@router.get("/case/{case_id}/state/version/{version}")
async def get_state_at_version(
    case_id: str,
    version: int,
    db: AsyncSession = Depends(get_db)
):
    """Get aggregate state at specific version"""
    service = ReplayService(db)

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    state = await service.get_state_at_version(case_id, version)
    if not state:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")

    return state


@router.get("/case/{case_id}/state/timestamp/{timestamp}")
async def get_state_at_timestamp(
    case_id: str,
    timestamp: str,
    db: AsyncSession = Depends(get_db)
):
    """Get aggregate state at specific timestamp"""
    service = ReplayService(db)

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid timestamp format")

    state = await service.get_state_at_timestamp(case_id, dt)
    if not state:
        raise HTTPException(status_code=404, detail="No events found before timestamp")

    return state


@router.get("/case/{case_id}/compare")
async def compare_versions(
    case_id: str,
    version_a: int = Query(..., ge=1),
    version_b: int = Query(..., ge=1),
    db: AsyncSession = Depends(get_db)
):
    """Compare two versions of a case"""
    service = ReplayService(db)

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    return await service.compare_versions(case_id, version_a, version_b)


@router.get("/case/{case_id}/history")
async def get_version_history(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get version history summary"""
    service = ReplayService(db)

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    return await service.get_version_history(case_id)

@router.get("/case/{case_id}/timeline")
async def get_event_timeline_debug(
    case_id: str,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    print("=" * 50)
    print("TIMELINE ENDPOINT HIT!")
    print(f"Case ID: {case_id}")
    print("=" * 50)
    return {"debug": "endpoint reached", "case_id": case_id}
