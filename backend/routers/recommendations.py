# backend/routers/recommendations.py
from typing import Dict, Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/recommendations", tags=["recommendations"])


@router.get("/")
async def get_recommendations(
    case_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """
    Get recommendations for a case or all recommendations.
    """
    try:
        if case_id:
            query = """
                SELECT 
                    id,
                    case_id,
                    recommendation_text,
                    priority,
                    status,
                    timeline_days,
                    potential_impact,
                    created_at
                FROM recommendations
                WHERE case_id = :case_id AND status != 'COMPLETED'
                ORDER BY 
                    CASE priority 
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                    END
                LIMIT :limit
            """
            result = await db.execute(text(query), {"case_id": case_id, "limit": limit})
        else:
            query = """
                SELECT 
                    id,
                    case_id,
                    recommendation_text,
                    priority,
                    status,
                    timeline_days,
                    potential_impact,
                    created_at
                FROM recommendations
                WHERE status != 'COMPLETED'
                ORDER BY 
                    CASE priority 
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                    END
                LIMIT :limit
            """
            result = await db.execute(text(query), {"limit": limit})
        
        rows = result.fetchall()
        
        return [
            {
                "id": str(row[0]),
                "case_id": str(row[1]) if row[1] else None,
                "recommendation_text": row[2],
                "priority": row[3],
                "status": row[4],
                "timeline_days": row[5],
                "potential_impact": float(row[6]) if row[6] else None,
                "created_at": row[7].isoformat() if row[7] else None
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# RECOMMENDATIONS SUMMARY ENDPOINT
# ============================================================

@router.get("/summary")
async def get_recommendation_summary(
    db: AsyncSession = Depends(get_db)
):
    """
    Get summary of recommendations by priority level.
    
    Returns:
        Dict with priority levels as keys and counts as values.
        Example: {"CRITICAL": 2, "HIGH": 1, "MEDIUM": 1, "LOW": 0}
    """
    try:
        query = """
            SELECT 
                priority,
                COUNT(*) as count
            FROM recommendations
            WHERE status != 'COMPLETED'
            GROUP BY priority
        """
        
        result = await db.execute(text(query))
        rows = result.fetchall()
        
        # Initialize with all priorities
        summary = {
            "CRITICAL": 0,
            "HIGH": 0,
            "MEDIUM": 0,
            "LOW": 0
        }
        
        # Fill with actual data
        for row in rows:
            priority = row[0]
            count = row[1]
            if priority in summary:
                summary[priority] = count
        
        return summary
        
    except Exception as e:
        logger.error(f"Error getting recommendation summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting recommendation summary: {str(e)}"
        )


@router.post("/")
async def create_recommendation(
    case_id: str,
    recommendation_text: str,
    priority: str = "MEDIUM",
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new recommendation for a case.
    """
    try:
        query = """
            INSERT INTO recommendations (
                id,
                case_id,
                recommendation_text,
                priority,
                status,
                created_at
            )
            VALUES (
                gen_random_uuid(),
                :case_id,
                :recommendation_text,
                :priority,
                'PENDING',
                NOW()
            )
            RETURNING id
        """
        
        result = await db.execute(
            text(query),
            {
                "case_id": case_id,
                "recommendation_text": recommendation_text,
                "priority": priority
            }
        )
        await db.commit()
        
        new_id = result.scalar()
        return {"id": str(new_id), "message": "Recommendation created successfully"}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating recommendation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
