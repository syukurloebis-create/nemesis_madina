from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.infrastructure.database import get_db
from backend.cases.event_store import get_case_events, compute_event_hash

router = APIRouter(prefix="/integrity", tags=["integrity"])

@router.get("/events/{case_id}/verify-chain")
async def verify_event_chain(case_id: str, session: AsyncSession = Depends(get_db)):
    """Verify entire event hash chain for a case"""
    events = await get_case_events(session, case_id)
    
    if not events:
        return {"case_id": case_id, "valid": True, "total_events": 0, "message": "No events"}
    
    for i, event in enumerate(events):
        computed_hash = compute_event_hash(
            case_id=event.aggregate_id,
            event_id=event.id,
            event_type=event.event_type,
            version=event.event_version,
            data=event.payload,
            previous_hash=event.previous_hash
        )
        
        if computed_hash != event.event_hash:
            return {
                "valid": False,
                "broken_at_index": i,
                "event_id": str(event.id),
                "expected_hash": computed_hash,
                "actual_hash": event.event_hash
            }
    
    return {
        "valid": True,
        "total_events": len(events),
        "case_id": case_id
    }
