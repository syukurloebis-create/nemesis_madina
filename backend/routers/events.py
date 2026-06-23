from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from infrastructure.database import get_db
from security.auth import decode_token

router = APIRouter(prefix="/events", tags=["events"])

def get_user_info(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    payload = decode_token(token)
    return payload.get("sub") if payload else None

@router.get("/case/{case_id}")
async def get_case_events(case_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Get all events for a case with hash chain"""
    user_id = get_user_info(request)
    
    result = await db.execute(text("""
        SELECT event_id, event_type, version, event_hash, previous_hash, timestamp, user_id, data
        FROM events
        WHERE case_id = CAST(:case_id AS UUID)
        ORDER BY timestamp
    """), {"case_id": case_id})
    
    events = result.fetchall()
    
    return [
        {
            "event_id": str(e[0]),
            "event_type": e[1],
            "version": e[2],
            "event_hash": e[3],
            "previous_hash": e[4],
            "timestamp": e[5].isoformat() if e[5] else None,
            "user_id": e[6],
            "data": e[7]
        }
        for e in events
    ]
