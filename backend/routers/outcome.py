from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime

from database import get_db

router = APIRouter(prefix="/outcome", tags=["outcome"])


class OutcomeCreate(BaseModel):
    case_id: str
    estimated_loss: float = 0
    referred_to_aph: bool = False
    aph_institution: Optional[str] = None
    notes: Optional[str] = None


class RecoveryCreate(BaseModel):
    outcome_id: str
    amount: float
    recovery_method: str
    notes: Optional[str] = None


@router.post("/create")
async def create_outcome(
    data: OutcomeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create outcome for a case"""
    try:
        outcome_id = uuid.uuid4()
        
        await db.execute(
            text("""
                INSERT INTO outcome (id, case_id, estimated_loss, referred_to_aph, aph_institution, notes, created_at)
                VALUES (:id, :case_id, :loss, :referred, :aph, :notes, NOW())
            """),
            {
                "id": outcome_id,
                "case_id": data.case_id,
                "loss": data.estimated_loss,
                "referred": data.referred_to_aph,
                "aph": data.aph_institution,
                "notes": data.notes
            }
        )
        await db.commit()
        
        return {
            "success": True,
            "outcome_id": str(outcome_id),
            "message": "Outcome created successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/case/{case_id}")
async def get_outcome_by_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get outcome for a specific case"""
    try:
        result = await db.execute(
            text("""
                SELECT id, estimated_loss, recovered_value, referred_to_aph, aph_institution, notes, created_at
                FROM outcome
                WHERE case_id = :case_id
                ORDER BY created_at DESC
                LIMIT 1
            """),
            {"case_id": case_id}
        )
        row = result.fetchone()
        
        if not row:
            return {
                "case_id": case_id,
                "has_outcome": False,
                "message": "No outcome recorded for this case"
            }
        
        # Get recovery actions
        recovery_result = await db.execute(
            text("""
                SELECT amount, recovery_method, recovered_at
                FROM recovery_actions
                WHERE outcome_id = :outcome_id
                ORDER BY recovered_at DESC
            """),
            {"outcome_id": row[0]}
        )
        recoveries = recovery_result.fetchall()
        
        return {
            "case_id": case_id,
            "has_outcome": True,
            "outcome_id": str(row[0]),
            "estimated_loss": float(row[1]) if row[1] else 0,
            "recovered_value": float(row[2]) if row[2] else 0,
            "referred_to_aph": row[3],
            "aph_institution": row[4],
            "notes": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "recovery_actions": [
                {
                    "amount": float(r[0]),
                    "method": r[1],
                    "recovered_at": r[2].isoformat() if r[2] else None
                }
                for r in recoveries
            ]
        }
    except Exception as e:
        return {"case_id": case_id, "error": str(e)}


@router.post("/recovery/add")
async def add_recovery_action(
    data: RecoveryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Add recovery action to an outcome"""
    try:
        recovery_id = uuid.uuid4()
        
        await db.execute(
            text("""
                INSERT INTO recovery_actions (id, outcome_id, amount, recovery_method, recovered_at, notes)
                VALUES (:id, :outcome_id, :amount, :method, NOW(), :notes)
            """),
            {
                "id": recovery_id,
                "outcome_id": data.outcome_id,
                "amount": data.amount,
                "method": data.recovery_method,
                "notes": data.notes
            }
        )
        
        # Update total recovered_value in outcome
        await db.execute(
            text("""
                UPDATE outcome
                SET recovered_value = COALESCE(recovered_value, 0) + :amount,
                    updated_at = NOW()
                WHERE id = :outcome_id
            """),
            {"amount": data.amount, "outcome_id": data.outcome_id}
        )
        await db.commit()
        
        return {
            "success": True,
            "recovery_id": str(recovery_id),
            "message": "Recovery action added successfully"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/summary")
async def get_outcome_summary(
    db: AsyncSession = Depends(get_db)
):
    """Get outcome summary across all cases"""
    try:
        result = await db.execute(
            text("""
                SELECT 
                    COUNT(*) as total_outcomes,
                    COALESCE(SUM(estimated_loss), 0) as total_loss,
                    COALESCE(SUM(recovered_value), 0) as total_recovered,
                    COUNT(CASE WHEN referred_to_aph = TRUE THEN 1 END) as referred_count
                FROM outcome
            """)
        )
        row = result.fetchone()
        
        total_loss = float(row[1]) if row[1] else 0
        total_recovered = float(row[2]) if row[2] else 0
        
        return {
            "total_outcomes": row[0] or 0,
            "total_estimated_loss": total_loss,
            "total_recovered": total_recovered,
            "recovery_rate": round((total_recovered / total_loss * 100), 1) if total_loss > 0 else 0,
            "referred_to_aph": row[3] or 0
        }
    except Exception as e:
        return {"error": str(e)}
