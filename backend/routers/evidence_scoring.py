"""
Evidence Scoring Router - Fixed
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.database import get_db
from backend.services.evidence_scoring import calculate_score

router = APIRouter(prefix="/evidence", tags=["evidence"])

@router.get("/{evidence_id}/score")
async def get_evidence_score(evidence_id: str):
    try:
        result = calculate_score(evidence_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_evidence_stats(db: AsyncSession = Depends(get_db)):
    try:
        # Total evidence
        result = await db.execute(text("SELECT COUNT(*) FROM evidence"))
        total = result.scalar()
        
        # Verified count
        result = await db.execute(text("SELECT COUNT(*) FROM evidence WHERE status = 'verified'"))
        verified = result.scalar()
        
        # Pending count
        result = await db.execute(text("SELECT COUNT(*) FROM evidence WHERE status = 'pending'"))
        pending = result.scalar()
        
        # Rejected count
        result = await db.execute(text("SELECT COUNT(*) FROM evidence WHERE status = 'rejected'"))
        rejected = result.scalar()
        
        return {
            "total": total,
            "verified": verified,
            "pending": pending,
            "rejected": rejected
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
