from sqlalchemy import text
from uuid import UUID

from backend.services.finding_lifecycle_service import (
    FindingLifecycleService
)
from backend.services.finding_assignment_sla_service import (
    FindingAssignmentSLAService
)



class FindingAssignmentService:

    def __init__(self, db):
        self.db = db
        self.lifecycle = FindingLifecycleService(db)


    async def get_active_assignment(
        self,
        finding_id
    ):

        result = await self.db.execute(
            text(
                """
                SELECT id, finding_id, analyst_id, analyst_name, role,
                       assigned_by, assigned_at, notes, status,
                       due_date, sla_deadline, is_active,
                       created_at, updated_at
                FROM finding_assignments
                WHERE finding_id = :finding_id AND is_active = true
                AND status='ACTIVE'
                LIMIT 1
                """
            ),
            {
                "finding_id": finding_id
            }
        )

        row = result.mappings().first()

        return dict(row) if row else None



    async def assign(
        self,
        finding_id,
        analyst_id,
        analyst_name,
        role,
        assigned_by,
        notes=None
    ):

        existing = await self.get_active_assignment(
            finding_id
        )

        if existing:
            raise Exception(
                "Finding already assigned"
            )


        result = await self.db.execute(
            text(
                """
                INSERT INTO finding_assignments
                (
                    id,
                    finding_id,
                    analyst_id,
                    analyst_name,
                    role,
                    assigned_by,
                    assigned_at,
                    notes,
                    status,
                    due_date,
                    sla_deadline,
                    is_active,
                    created_at,
                    updated_at
                )

                VALUES
                (
                    :finding_id,
                    :analyst_id,
                    :analyst_name,
                    :assigned_by,
                    :role,
                    :notes,
                    'ACTIVE'
                )

                RETURNING id
                """
            ),
            {
                "finding_id": finding_id,
                "analyst_id": analyst_id,
                "analyst_name": analyst_name,
                "assigned_by": assigned_by,
                "role": role,
                "notes": notes
            }
        )


        row = result.fetchone()

        assignment_id = row.id


        await self.lifecycle.record_event(
            finding_id=finding_id,
            event="ASSIGNMENT_SLA_CREATED",
            actor=assigned_by,
            notes=f"SLA due at {sla_due_at}"
        )


        return assignment_id


    async def mark_overdue(self):

        result = await self.db.execute(
            text("""
                SELECT finding_id
                FROM finding_assignments
                WHERE status='ACTIVE'
                AND sla_due_at < now()
            """)
        )

        rows = result.fetchall()


        for row in rows:

            await self.db.execute(
                text("""
                    UPDATE finding_assignments
                    SET status='OVERDUE'
                    WHERE finding_id=:finding_id
                    AND status='ACTIVE'
                """),
                {
                    "finding_id": row.finding_id
                }
            )


            await self.lifecycle.record_event(
                finding_id=row.finding_id,
                event="ASSIGNMENT_OVERDUE",
                actor="SLA_ENGINE",
                notes="Assignment exceeded SLA deadline"
            )


        await self.db.commit()


    async def reassign(
        self,
        finding_id,
        analyst_id,
        analyst_name,
        role,
        assigned_by,
        notes=None
    ):

        current = await self.get_active_assignment(
            finding_id
        )

        if not current:
            return await self.assign(
                finding_id,
                analyst_id,
                analyst_name,
                role,
                assigned_by,
                notes
            )


        await self.db.execute(
            text(
                """
                UPDATE finding_assignments
                SET
                    status='CLOSED',
                    closed_at=now()
                WHERE
                    finding_id=:finding_id
                AND
                    status='ACTIVE'
                """
            ),
            {
                "finding_id": finding_id
            }
        )


        await self.lifecycle.record_event(
            finding_id=finding_id,
            event="ASSIGNMENT_CLOSED",
            actor=assigned_by,
            notes=f"Closed assignment {current['analyst_name']}"
        )


        return await self.assign(
            finding_id,
            analyst_id,
            analyst_name,
            role,
            assigned_by,
            notes
        )



    async def unassign(
        self,
        finding_id,
        actor,
        notes=None
    ):

        current = await self.get_active_assignment(
            finding_id
        )


        if not current:
            raise Exception(
                "No active assignment"
            )


        await self.db.execute(
            text(
                """
                UPDATE finding_assignments
                SET
                    status='CLOSED',
                    closed_at=now()
                WHERE
                    finding_id=:finding_id
                AND
                    status='ACTIVE'
                """
            ),
            {
                "finding_id": finding_id
            }
        )


        await self.lifecycle.record_event(
            finding_id=finding_id,
            event="UNASSIGNED",
            actor=actor,
            notes=notes
        )


        return True