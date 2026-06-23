# backend/routers/historical.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime
from typing import Optional, List
import logging

from infrastructure.database import get_db
from services.historical_service import HistoricalService
from security.dependencies import require_role
from cases.event_store import get_case_events

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/historical", tags=["Historical Reconstruction"])


@router.get("/case/{case_id}/state-at-time")
async def get_case_state_at_time(
    case_id: str,
    timestamp: str = Query(..., description="ISO format timestamp e.g., 2026-06-15T04:00:00"),
    session: AsyncSession = Depends(get_db)
):
    """Get case state at specific timestamp (Time Travel)"""
    from services.replay_service import ReplayService

    try:
        target_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        service = ReplayService(session)

        # Get events before timestamp
        events = await get_case_events(session, case_id)
        events_before = [e for e in events if e.created_at <= target_time]

        if not events_before:
            return {
                "case_id": case_id,
                "timestamp": timestamp,
                "state": {},
                "events_found": 0,
                "message": "No events found before timestamp"
            }

        # Rebuild state from events before timestamp
        state = service._reduce_events(events_before)

        return {
            "case_id": case_id,
            "timestamp": timestamp,
            "state": state,
            "events_applied": len(events_before),
            "last_event_version": events_before[-1].event_version if events_before else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {e}")
    except Exception as e:
        logger.error(f"Error in state at time: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/case/{case_id}/state")
async def get_state_at_timestamp(
    case_id: str,
    timestamp: str = Query(..., description="ISO format timestamp"),
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_role(["ADMIN", "AUDITOR", "INVESTIGATOR"]))
):
    """Get case state at a specific historical timestamp"""

    # Check if case exists
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

    service = HistoricalService(db)
    state = await service.get_state_at_timestamp(case_id, dt)

    if not state:
        raise HTTPException(status_code=404, detail="No events found before timestamp")

    return state


@router.get("/case/{case_id}/timeline")
async def get_forensic_timeline(
    case_id: str,
    from_date: Optional[str] = Query(None, description="Start date (ISO format)"),
    to_date: Optional[str] = Query(None, description="End date (ISO format)"),
    categories: Optional[List[str]] = Query(None, description="Filter by categories"),
    severity: Optional[List[str]] = Query(None, description="Filter by severity"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_role(["ADMIN", "AUDITOR", "INVESTIGATOR"]))
):
    """Get forensic timeline for a case"""

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    from_dt = None
    to_dt = None

    if from_date:
        try:
            from_dt = datetime.fromisoformat(from_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid from_date format")

    if to_date:
        try:
            to_dt = datetime.fromisoformat(to_date.replace("Z", "+00:00"))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid to_date format")

    service = HistoricalService(db)
    timeline = await service.get_timeline(
        case_id,
        from_date=from_dt,
        to_date=to_dt,
        categories=categories,
        severity=severity,
        limit=limit,
        offset=offset
    )

    return timeline


@router.get("/case/{case_id}/compare-versions")
async def compare_versions(
    case_id: str,
    version_a: int = Query(..., ge=1),
    version_b: int = Query(..., ge=1),
    db: AsyncSession = Depends(get_db),
    _: any = Depends(require_role(["ADMIN", "INVESTIGATOR"]))
):
    """Compare two versions of a case with detailed diff"""
    from services.replay_service import ReplayService

    result = await db.execute(
        text("SELECT id FROM cases WHERE id = :id"),
        {"id": case_id}
    )
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Case not found")

    service = ReplayService(db)
    diff = await service.compare_versions(case_id, version_a, version_b)

    return diff
