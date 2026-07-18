from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.infrastructure.database import get_db
from backend.services.finding_assignment_sla_service import (
    FindingAssignmentSLAService
)

router = APIRouter(prefix="/finding-assignments", tags=["finding-assignments"])


@router.get("/{finding_id}")
async def get_assignment(finding_id: str, db: AsyncSession = Depends(get_db)):

    result = await db.execute(
        text("""
            SELECT *
            FROM finding_assignments
            WHERE finding_id=:finding_id
            AND status='ACTIVE'
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"finding_id": finding_id}
    )

    row = result.mappings().first()

    return row if row else {"message": "no active assignment"}


@router.post("/sla/check")
async def check_sla(db: AsyncSession = Depends(get_db)):

    service = FindingAssignmentSLAService(db)

    await service.mark_overdue()

    return {
        "message": "SLA check completed"
    }