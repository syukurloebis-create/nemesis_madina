from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.infrastructure.database import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/finding-assignments", tags=["finding-assignments"])


# =========================
# GET ACTIVE ASSIGNMENT
# =========================
@router.get("/{finding_id}")
async def get_active_assignment(
    finding_id: str,
    db: AsyncSession = Depends(get_db)
):
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

    row = result.mappings().fetchone()

    if not row:
        return {"message": "No active assignment"}

    return dict(row)


# =========================
# SLA CHECK ENGINE
# =========================
@router.post("/sla/check")
async def check_sla(
    db: AsyncSession = Depends(get_db)
):

    service = FindingAssignmentSLAService(db)

    count = await service.mark_overdue()

    return {
        "message":"SLA check completed",
        "overdue_count":count
    }

    rows = result.mappings().all()

    now = datetime.utcnow()
    updated = 0

    for r in rows:
        if r["sla_due_at"] and r["sla_due_at"] < now:

            await db.execute(
                text("""
                    UPDATE finding_assignments
                    SET status='OVERDUE',
                        closed_at=now()
                    WHERE id=:id
                """),
                {"id": r["id"]}
            )

            await db.execute(
                text("""
                    INSERT INTO finding_events
                    (finding_id, event, actor, notes)
                    VALUES
                    (:finding_id, 'ASSIGNMENT_OVERDUE', 'system', 'SLA breached')
                """),
                {"finding_id": r["finding_id"]}
            )

            updated += 1

    await db.commit()

    return {
        "checked": len(rows),
        "overdue_marked": updated
    }