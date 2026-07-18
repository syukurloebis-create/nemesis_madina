from fastapi import APIRouter, Depends
from sqlalchemy import text
from backend.infrastructure.database import get_db
from backend.security.dependencies import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/procurement", tags=["procurement"])

@router.get("/list")
async def list_procurement(
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(text("""
        SELECT id, procurement_id, title, vendor, amount, date, created_at
        FROM procurement_records
        ORDER BY date DESC
        LIMIT :limit
    """), {"limit": limit})
    
    records = [dict(r._mapping) for r in result.fetchall()]
    return {"records": records, "count": len(records)}
