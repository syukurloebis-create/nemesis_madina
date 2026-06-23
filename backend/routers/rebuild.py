from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from infrastructure.database import get_db
from security.auth import decode_token

router = APIRouter(prefix="/rebuild", tags=["Event Rebuild"])

def get_user_info(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    payload = decode_token(token)
    return payload.get("sub") if payload else None

@router.get("/case/{case_id}/state")
async def get_rebuilt_state(case_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Get case state using simple replay"""
    user_id = get_user_info(request)
    
    # Get all events for the case
    result = await db.execute(text("""
        SELECT event_type, data, version
        FROM events
        WHERE case_id = CAST(:case_id AS UUID)
        ORDER BY timestamp
    """), {"case_id": case_id})
    
    events = result.fetchall()
    
    # Rebuild state by applying events in order
    state = {
        "case_id": case_id,
        "title": None,
        "description": None,
        "status": "OPEN",
        "priority": "MEDIUM",
        "version": 0
    }
    
    for event in events:
        event_type = event[0]
        data = event[1]
        version = event[2]
        state["version"] = version
        
        if event_type == "case_created":
            state["title"] = data.get("title")
            state["description"] = data.get("description")
            state["priority"] = data.get("priority", "MEDIUM")
        elif event_type == "status_changed":
            state["status"] = data.get("status")
        elif event_type == "priority_changed":
            state["priority"] = data.get("priority")
    
    return state

@router.get("/case/{case_id}/verify-chain")
async def verify_chain(case_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Verify hash chain integrity for a case"""
    user_id = get_user_info(request)
    
    result = await db.execute(text("""
        SELECT event_hash, previous_hash, version
        FROM events
        WHERE case_id = CAST(:case_id AS UUID)
        ORDER BY timestamp
    """), {"case_id": case_id})
    
    events = result.fetchall()
    
    is_valid = True
    broken_at = None
    
    for i in range(1, len(events)):
        if events[i][1] != events[i-1][0]:
            is_valid = False
            broken_at = i
            break
    
    return {
        "case_id": case_id,
        "chain_valid": is_valid,
        "total_events": len(events),
        "broken_at_sequence": broken_at
    }
