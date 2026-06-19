from sqlalchemy import text


class EvidenceRepository:

    def __init__(self, db):
        self.db = db


    async def get(self, evidence_id):

        q = """
        SELECT *
        FROM evidence
        WHERE id=:id
        """

        r = await self.db.execute(
            text(q),
            {"id": evidence_id}
        )

        return r.fetchone()


    async def update_status(
        self,
        evidence_id,
        status,
        trust_score,
        confidence
    ):

        q = """
        UPDATE evidence
        SET
            status=:status,
            trust_score=:trust,
            confidence_level=:confidence,
            updated_at=NOW()
        WHERE id=:id
        """

        await self.db.execute(
            text(q),
            {
                "id": evidence_id,
                "status": status,
                "trust": trust_score,
                "confidence": confidence
            }
        )