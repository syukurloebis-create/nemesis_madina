from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from backend.infrastructure.database import get_db
from backend.security.auth import decode_token

router = APIRouter(prefix="/temporal", tags=["Temporal Query"])

def get_user_info(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header[7:]
    payload = decode_token(token)
    return payload.get("sub") if payload else None


@router.get("/test")
async def test_temporal():
    return {"status": "Temporal API is working"}


@router.get("/case/{case_id}/trace-chain")
async def trace_chain(
    case_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    user_id = get_user_info(request)
    return {
        "case_id": case_id,
        "message": "Trace chain endpoint - under construction",
        "status": "ok"
    }
