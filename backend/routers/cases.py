from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from backend.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

@router.get("/")
async def get_all_cases(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("""
            SELECT id, title, description, status, priority, 
                   risk_score, risk_level, workflow_stage, created_at
            FROM cases
            ORDER BY created_at DESC
        """))
        rows = result.fetchall()
        return [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "priority": row[4],
                "risk_score": float(row[5]) if row[5] else 0,
                "risk_level": row[6],
                "workflow_stage": row[7],
                "created_at": row[8].isoformat() if row[8] else None
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# CASE ACTIONS
# ============================================================

@router.post("/{case_id}/action")
async def case_action(
    case_id: str,
    action: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Perform action on a case: investigate, assign, close
    """
    try:
        # Check if case exists
        check_query = "SELECT id, status FROM cases WHERE id = :case_id"
        result = await db.execute(text(check_query), {"case_id": case_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        current_status = row[1]
        new_status = current_status
        
        # Determine new status based on action
        if action == "investigate":
            if current_status == "OPEN":
                new_status = "INVESTIGATING"
            else:
                return {
                    "id": case_id,
                    "status": current_status,
                    "message": f"Case already {current_status}, cannot investigate"
                }
        elif action == "assign":
            # Assign to current user (simplified)
            new_status = "INVESTIGATING"
        elif action == "close":
            if current_status in ["INVESTIGATING", "REVIEW"]:
                new_status = "CLOSED"
            else:
                return {
                    "id": case_id,
                    "status": current_status,
                    "message": f"Case must be in INVESTIGATING or REVIEW to close"
                }
        else:
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
        
        # Update case status
        update_query = """
            UPDATE cases 
            SET status = :new_status,
                updated_at = NOW()
            WHERE id = :case_id
            RETURNING id
        """
        
        await db.execute(
            text(update_query),
            {"new_status": new_status, "case_id": case_id}
        )
        await db.commit()
        
        return {
            "id": case_id,
            "action": action,
            "status": new_status,
            "previous_status": current_status,
            "message": f"Case {action} successful"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error performing case action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
