from sqlalchemy import text

from backend.services.finding_timeline_normalizer import (
    FindingTimelineNormalizer
)


class FindingTimelineService:

    def __init__(self, db):
        self.db = db


    async def get_timeline(
        self,
        finding_id: str
    ):

        result = await self.db.execute(
            text(
                """
                SELECT *
                FROM
                (

                    /*
                    CORE EVENTS
                    */
                    SELECT
                        'EVENT' AS type,
                        event AS event_type,
                        actor,
                        notes,
                        metadata,
                        created_at AS timestamp

                    FROM finding_events

                    WHERE finding_id=:finding_id

                    AND event NOT IN
                    (
                        'ACTION_RECORDED',
                        'REVIEW_DECISION_CREATED'
                    )


                    UNION ALL


                    /*
                    ACTION LOG
                    */
                    SELECT
                        'ACTION' AS type,
                        action_type AS event_type,
                        actor_name AS actor,
                        description AS notes,
                        metadata,
                        created_at AS timestamp

                    FROM finding_action_logs

                    WHERE finding_id=:finding_id



                    UNION ALL


                    /*
                    REVIEW DECISION
                    */
                    SELECT
                        'REVIEW_DECISION' AS type,
                        decision AS event_type,
                        decided_by AS actor,
                        rationale AS notes,
                        NULL AS metadata,
                        decided_at AS timestamp

                    FROM finding_review_decisions

                    WHERE finding_id=:finding_id


                ) AS timeline

                ORDER BY timestamp ASC
                """
            ),
            {
                "finding_id": finding_id
            }
        )


        timeline=[]


        return [
            FindingTimelineNormalizer.normalize(
                dict(row)
            )
            for row in result.mappings()
        ]