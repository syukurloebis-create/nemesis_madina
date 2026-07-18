from sqlalchemy import text

from backend.services.finding_lifecycle_service import (
    FindingLifecycleService
)


class FindingReviewService:


    def __init__(self, db):
        self.db = db



    async def create_decision(
        self,
        finding_id: str,
        decision: str,
        rationale: str,
        confidence_score: float | None,
        decided_by: str,
        assignment_id: str | None = None,
    ):

        status_map = {

            "CONFIRMED":
                "APPROVED",

            "DISMISSED":
                "REJECTED",

            "ESCALATED":
                "ESCALATED",

            "MORE_EVIDENCE_REQUIRED":
                "UNDER_REVIEW",
        }


        new_status = status_map.get(
            decision
        )


        if not new_status:
            raise ValueError(
                "Invalid decision"
            )


        await self.db.execute(
            text(
                """
                INSERT INTO finding_review_decisions
                (
                    finding_id,
                    assignment_id,
                    decision,
                    rationale,
                    confidence_score,
                    decided_by
                )
                VALUES
                (
                    :finding_id,
                    :assignment_id,
                    :decision,
                    :rationale,
                    :confidence_score,
                    :decided_by
                )
                """
            ),
            {
                "finding_id": finding_id,
                "assignment_id": assignment_id,
                "decision": decision,
                "rationale": rationale,
                "confidence_score": confidence_score,
                "decided_by": decided_by,
            },
        )


        lifecycle = FindingLifecycleService(
            self.db
        )



        await self.db.execute(
            text(
                """
                UPDATE findings
                SET status=:status,
                    reviewed_by=:reviewed_by,
                    reviewed_at=now()
                WHERE id=:finding_id
                """
            ),
            {
                "status": new_status,
                "reviewed_by": decided_by,
                "finding_id": finding_id,
            },
        )


        await self.db.commit()

        dashboard_cache_manager.invalidate_finding(
            finding_id
        )

        return {
            "status":"success"
        }



    async def get_history(
        self,
        finding_id: str
    ):

        result = await self.db.execute(
            text(
                """
                SELECT
                    decision,
                    rationale,
                    confidence_score,
                    decided_by,
                    decided_at
                FROM finding_review_decisions
                WHERE finding_id=:finding_id
                ORDER BY decided_at ASC
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