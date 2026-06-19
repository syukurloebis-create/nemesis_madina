"""Replay API for rebuilding aggregate state from events"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import get_db
from backend.events.event_store import EventStore
from backend.cases.aggregate import CaseAggregate
import uuid

router = APIRouter(prefix="/api/v1/replay", tags=["replay"])


@router.post("/case/{case_id}")
async def replay_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Rebuild case state from event store.
    Returns the complete current state of the case.
    """
    # Validate UUID format
    try:
        uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case_id format")
    
    # Get events from event store
    event_store = EventStore(db)
    events = await event_store.get_events(case_id)
    
    if not events:
        raise HTTPException(
            status_code=404, 
            detail=f"No events found for case {case_id}"
        )
    
    # Rebuild aggregate from events
    aggregate = CaseAggregate(events)
    state = aggregate.get_state()
    
    if not state:
        raise HTTPException(
            status_code=500,
            detail="Failed to rebuild aggregate state"
        )
    
    return {
        "success": True,
        "case_id": case_id,
        "state": state.dict(),
        "metadata": {
            "total_events": len(events),
            "current_version": state.current_version,
            "rebuilt_at": str(events[-1].timestamp) if events else None
        }
    }


@router.get("/case/{case_id}/events")
async def get_case_events(
    case_id: str,
    from_version: int = None,
    to_version: int = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all events for a case, optionally filtered by version range.
    """
    # Validate UUID format
    try:
        uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case_id format")
    
    event_store = EventStore(db)
    events = await event_store.get_events(case_id, from_version, to_version)
    
    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"No events found for case {case_id}"
        )
    
    return {
        "success": True,
        "case_id": case_id,
        "total_events": len(events),
        "events": [
            {
                "event_id": e.event_id,
                "event_type": e.event_type.value,
                "version": e.version,
                "timestamp": e.timestamp.isoformat(),
                "user_id": e.user_id,
                "data": e.data
            }
            for e in events
        ]
    }


@router.get("/case/{case_id}/version/{version}")
async def get_case_at_version(
    case_id: str,
    version: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get case state at a specific version (historical reconstruction).
    """
    # Validate UUID format
    try:
        uuid.UUID(case_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid case_id format")
    
    event_store = EventStore(db)
    
    # Get events only up to specified version
    events = await event_store.get_events(case_id, to_version=version)
    
    if not events:
        raise HTTPException(
            status_code=404,
            detail=f"No events found for case {case_id} up to version {version}"
        )
    
    # Rebuild aggregate from events
    aggregate = CaseAggregate(events)
    state = aggregate.get_state()
    
    if not state:
        raise HTTPException(
            status_code=500,
            detail="Failed to rebuild aggregate state"
        )
    
    return {
        "success": True,
        "case_id": case_id,
        "version": version,
        "state": state.dict(),
        "metadata": {
            "events_used": len(events),
            "actual_version": state.current_version
        }
    }
