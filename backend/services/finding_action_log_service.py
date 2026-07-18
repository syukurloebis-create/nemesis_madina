import json
from sqlalchemy import text

from backend.services.finding_lifecycle_service import FindingLifecycleService


class FindingActionLogService:
    """
    Immutable operational audit log
    for finding analyst activities.
    """

    def __init__(self, db):
        self.db = db


    async def create_action(
        self,
        finding_id: str,
        action_type: str,
        description: str | None = None,
        actor_id: str | None = None,
        actor_name: str | None = None,
        assignment_id: str | None = None,
        metadata: dict | None = None,
    ):

        result = await self.db.execute(
            text(
                """
                INSERT INTO finding_action_logs
                (
                    finding_id,
                    assignment_id,
                    action_type,
                    description,
                    actor_id,
                    actor_name,
                    metadata
                )
                VALUES
                (
                    :finding_id,
                    :assignment_id,
                    :action_type,
                    :description,
                    :actor_id,
                    :actor_name,
                    CAST(:metadata AS json)
                )
                RETURNING id
                """
            ),
            {
                "finding_id": finding_id,
                "assignment_id": assignment_id,
                "action_type": action_type,
                "description": description,
                "actor_id": actor_id,
                "actor_name": actor_name,
                "metadata": json.dumps(metadata) if metadata else None,
            },
        )

        row = result.fetchone()


        lifecycle = FindingLifecycleService(self.db)

        await lifecycle.record_event(
            finding_id=finding_id,
            event="ACTION_RECORDED",
            actor=actor_name or "system",
            notes=action_type,
            metadata={
                "action_type": action_type,
                "description": description,
                "assignment_id": assignment_id,
                **(metadata or {})
            }
        )

        return str(row[0])


    async def get_actions(
        self,
        finding_id: str,
    ):

        result = await self.db.execute(
            text(
                """
                SELECT
                    id,
                    action_type,
                    description,
                    actor_id,
                    actor_name,
                    metadata,
                    created_at
                FROM finding_action_logs
                WHERE finding_id=:finding_id
                ORDER BY created_at ASC
                """
            ),
            {
                "finding_id": finding_id
            },
        )

        return [
            dict(row)
            for row in result.mappings()
        ]