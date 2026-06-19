# backend/routers/event_lineage.py
from fastapi import APIRouter, HTTPException, Query
import asyncpg
from typing import Optional

router = APIRouter(prefix="/event_lineage", tags=["event_lineage"])


@router.get("/")
async def get_event_lineage(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    aggregate_id: Optional[str] = None,
):
    """Get event lineage with optional filter by aggregate_id."""
    # Karena ini read-only, kita perlu akses pool dari runtime
    # Sementara return error karena belum diintegrasi dengan runtime
    return {
        "message": "Endpoint under construction. Use /replay/aggregate/{aggregate_id} instead",
        "suggestion": f"Try: /replay/aggregate/{aggregate_id}" if aggregate_id else "Try: /replay/aggregate/rup-65380658"
    }
