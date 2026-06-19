from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db

router = APIRouter(prefix="/risk", tags=["risk"])


@router.get("/stats")
async def get_risk_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get risk statistics summary"""
    try:
        result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN priority IN ('HIGH', 'CRITICAL') THEN 1 END) as high_risk,
                    COUNT(CASE WHEN priority = 'MEDIUM' THEN 1 END) as medium_risk,
                    COUNT(CASE WHEN priority = 'LOW' THEN 1 END) as low_risk
                FROM cases
            """)
        )
        row = result.fetchone()
        
        total = row[0] or 0
        high = row[1] or 0
        
        return {
            "total_cases": total,
            "high_risk_cases": high,
            "medium_risk_cases": row[2] or 0,
            "low_risk_cases": row[3] or 0,
            "risk_percentage": round((high / total * 100), 1) if total > 0 else 0
        }
    except Exception as e:
        return {"error": str(e)}


@router.get("/case/{case_id}")
async def get_case_risk_by_id(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get risk score for a specific case"""
    try:
        result = await db.execute(
            text("SELECT id, title, priority, status FROM cases WHERE id = :case_id"),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        if not row:
            return {"error": "Case not found"}
        
        priority_scores = {"LOW": 25, "MEDIUM": 50, "HIGH": 75, "CRITICAL": 95}
        risk_score = priority_scores.get(row[2], 50)
        
        risk_level = "HIGH" if risk_score >= 75 else "MEDIUM" if risk_score >= 50 else "LOW"
        
        return {
            "case_id": case_id,
            "title": row[1],
            "priority": row[2],
            "status": row[3],
            "risk_score": risk_score,
            "risk_level": risk_level
        }
    except Exception as e:
        return {"error": str(e)}
