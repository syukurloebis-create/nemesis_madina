# routers/decisions.py - Decision Support endpoints (FIXED for asyncpg)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.database import get_db
from typing import Optional
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/decisions", tags=["decisions"])

@router.get("/")
async def get_decisions(
    case_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get decisions with optional case filter"""
    try:
        if case_id:
            # Gunakan CAST yang kompatibel dengan asyncpg
            query = """
                SELECT 
                    id,
                    case_id,
                    title,
                    description,
                    priority,
                    action,
                    status,
                    assigned_to,
                    created_at,
                    due_date,
                    completed_at,
                    notes
                FROM decisions
                WHERE case_id = CAST(:case_id AS uuid)
                ORDER BY 
                    CASE priority 
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                    END,
                    created_at DESC
                LIMIT :limit
            """
            result = await db.execute(text(query), {"case_id": case_id, "limit": limit})
        else:
            query = """
                SELECT 
                    id,
                    case_id,
                    title,
                    description,
                    priority,
                    action,
                    status,
                    assigned_to,
                    created_at,
                    due_date,
                    completed_at,
                    notes
                FROM decisions
                ORDER BY 
                    CASE priority 
                        WHEN 'CRITICAL' THEN 1
                        WHEN 'HIGH' THEN 2
                        WHEN 'MEDIUM' THEN 3
                        WHEN 'LOW' THEN 4
                    END,
                    created_at DESC
                LIMIT :limit
            """
            result = await db.execute(text(query), {"limit": limit})
        
        rows = result.fetchall()
        
        decisions = []
        for row in rows:
            # Get justification for this decision
            just_query = """
                SELECT 
                    id,
                    factor,
                    description,
                    weight,
                    contribution
                FROM decision_justifications
                WHERE decision_id = CAST(:decision_id AS uuid)
            """
            just_result = await db.execute(text(just_query), {"decision_id": str(row[0])})
            just_rows = just_result.fetchall()
            
            justification = [
                {
                    "id": str(jr[0]),
                    "factor": jr[1],
                    "description": jr[2],
                    "weight": float(jr[3]) if jr[3] else 0,
                    "contribution": float(jr[4]) if jr[4] else 0,
                    "evidence": []
                }
                for jr in just_rows
            ]
            
            # Get case title
            case_title = "Unknown Case"
            if row[1]:
                try:
                    case_query = "SELECT title FROM cases WHERE id = CAST(:case_id AS uuid)"
                    case_result = await db.execute(text(case_query), {"case_id": str(row[1])})
                    case_row = case_result.fetchone()
                    if case_row:
                        case_title = case_row[0]
                except Exception as e:
                    logger.warning(f"Could not fetch case title: {str(e)}")
            
            decisions.append({
                "id": str(row[0]),
                "case_id": str(row[1]) if row[1] else None,
                "case_title": case_title,
                "title": row[2],
                "description": row[3],
                "priority": row[4],
                "action": row[5],
                "status": row[6],
                "assigned_to": str(row[7]) if row[7] else None,
                "created_at": row[8].isoformat() if row[8] else None,
                "due_date": row[9].isoformat() if row[9] else None,
                "completed_at": row[10].isoformat() if row[10] else None,
                "notes": row[11],
                "justification": justification,
                "evidence": []
            })
        
        return decisions
    except Exception as e:
        logger.error(f"Error getting decisions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_decision_summary(db: AsyncSession = Depends(get_db)):
    """Get decision summary statistics"""
    try:
        # Total count
        total_query = "SELECT COUNT(*) FROM decisions"
        total_result = await db.execute(text(total_query))
        total = total_result.scalar() or 0
        
        # By priority
        priority_query = """
            SELECT priority, COUNT(*) 
            FROM decisions 
            GROUP BY priority
        """
        priority_result = await db.execute(text(priority_query))
        by_priority = {row[0]: row[1] for row in priority_result.fetchall()}
        
        # By status
        status_query = """
            SELECT status, COUNT(*) 
            FROM decisions 
            GROUP BY status
        """
        status_result = await db.execute(text(status_query))
        by_status = {row[0]: row[1] for row in status_result.fetchall()}
        
        # By action
        action_query = """
            SELECT action, COUNT(*) 
            FROM decisions 
            GROUP BY action
        """
        action_result = await db.execute(text(action_query))
        by_action = {row[0]: row[1] for row in action_result.fetchall()}
        
        return {
            "total": total,
            "by_priority": {
                "CRITICAL": by_priority.get("CRITICAL", 0),
                "HIGH": by_priority.get("HIGH", 0),
                "MEDIUM": by_priority.get("MEDIUM", 0),
                "LOW": by_priority.get("LOW", 0)
            },
            "by_status": {
                "PENDING": by_status.get("PENDING", 0),
                "IN_PROGRESS": by_status.get("IN_PROGRESS", 0),
                "COMPLETED": by_status.get("COMPLETED", 0),
                "REJECTED": by_status.get("REJECTED", 0),
                "CANCELLED": by_status.get("CANCELLED", 0)
            },
            "by_action": by_action
        }
    except Exception as e:
        logger.error(f"Error getting decision summary: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/")
async def create_decision(
    case_id: str,
    title: str,
    description: str,
    priority: str = "MEDIUM",
    action: str = "MONITORING",
    db: AsyncSession = Depends(get_db)
):
    """Create a new decision"""
    try:
        decision_id = str(uuid.uuid4())
        query = """
            INSERT INTO decisions (
                id,
                case_id,
                title,
                description,
                priority,
                action,
                status,
                created_at,
                due_date
            )
            VALUES (
                :id,
                CAST(:case_id AS uuid),
                :title,
                :description,
                :priority,
                :action,
                'PENDING',
                NOW(),
                NOW() + INTERVAL '30 days'
            )
            RETURNING id
        """
        result = await db.execute(
            text(query),
            {
                "id": decision_id,
                "case_id": case_id,
                "title": title,
                "description": description,
                "priority": priority,
                "action": action
            }
        )
        await db.commit()
        
        return {
            "id": str(result.scalar()),
            "message": "Decision created successfully"
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{decision_id}/status")
async def update_decision_status(
    decision_id: str,
    status: str,
    db: AsyncSession = Depends(get_db)
):
    """Update decision status"""
    try:
        query = """
            UPDATE decisions 
            SET status = :status,
                completed_at = CASE 
                    WHEN :status = 'COMPLETED' THEN NOW()
                    ELSE completed_at
                END
            WHERE id = CAST(:id AS uuid)
            RETURNING id
        """
        result = await db.execute(
            text(query),
            {"id": decision_id, "status": status}
        )
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Decision not found")
        
        return {
            "id": decision_id,
            "status": status,
            "message": "Decision status updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating decision status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{decision_id}/justification")
async def get_decision_justification(
    decision_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get decision justification"""
    try:
        query = """
            SELECT 
                j.id,
                j.factor,
                j.description,
                j.weight,
                j.contribution,
                e.id as evidence_id,
                e.title as evidence_title,
                e.trust_score as evidence_trust
            FROM decision_justifications j
            LEFT JOIN decision_evidence de ON de.justification_id = j.id
            LEFT JOIN evidence e ON de.evidence_id = e.id
            WHERE j.decision_id = CAST(:decision_id AS uuid)
            ORDER BY j.contribution DESC
        """
        result = await db.execute(text(query), {"decision_id": decision_id})
        rows = result.fetchall()
        
        if not rows:
            return {"justification": []}
        
        # Group by justification
        justification_map = {}
        for row in rows:
            jid = str(row[0])
            if jid not in justification_map:
                justification_map[jid] = {
                    "id": jid,
                    "factor": row[1],
                    "description": row[2],
                    "weight": float(row[3]) if row[3] else 0,
                    "contribution": float(row[4]) if row[4] else 0,
                    "evidence": []
                }
            if row[5]:
                justification_map[jid]["evidence"].append({
                    "id": str(row[5]),
                    "title": row[6],
                    "trust_score": float(row[7]) if row[7] else 0
                })
        
        return {"justification": list(justification_map.values())}
    except Exception as e:
        logger.error(f"Error getting decision justification: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{decision_id}/execute")
async def execute_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Execute a decision action"""
    try:
        # Update status to IN_PROGRESS
        query = """
            UPDATE decisions 
            SET status = 'IN_PROGRESS'
            WHERE id = CAST(:id AS uuid) AND status = 'PENDING'
            RETURNING id
        """
        result = await db.execute(text(query), {"id": decision_id})
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Decision not found or already executed")
        
        return {
            "id": decision_id,
            "status": "IN_PROGRESS",
            "message": "Decision execution started"
        }
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error executing decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
