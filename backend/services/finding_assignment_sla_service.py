from sqlalchemy import text

from backend.services.finding_lifecycle_service import (
    FindingLifecycleService,
)


class FindingAssignmentSLAService:

    def __init__(self, db):
        self.db = db


    async def mark_overdue(self):

        result = await self.db.execute(
            text(
                """
                UPDATE finding_assignments
                SET
                    status='OVERDUE'
                WHERE
                    status='ACTIVE'
                    AND sla_due_at IS NOT NULL
                    AND sla_due_at < now()
                RETURNING id, finding_id
                """
            )
        )

        updated = result.fetchall()


        lifecycle = FindingLifecycleService(self.db)


        for row in updated:

            await lifecycle.record_event(
                finding_id=str(row.finding_id),
                event="ASSIGNMENT_SLA_BREACHED",
                actor="SLA_ENGINE",
                notes="Assignment exceeded SLA deadline",
                metadata={
                    "sla": {
                        "due_at": str(row.sla_due_at),
                        "priority": row.priority,
                        "assignment_id": str(row.id),
                    },
                    "engine": "assignment_sla_monitor",
                }
            )


        await self.db.commit()


        return len(updated)


    async def get_overdue(self):

        result = await self.db.execute(
            text(
                """
                SELECT
                    id,
                    finding_id,
                    analyst_name,
                    sla_due_at,
                    priority
                FROM finding_assignments
                WHERE status='OVERDUE'
                ORDER BY sla_due_at ASC
                """
            )
        )

        return [
            dict(row)
            for row in result.mappings()
        ]