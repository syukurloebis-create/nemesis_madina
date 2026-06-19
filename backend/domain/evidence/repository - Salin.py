import hashlib
import aiofiles
import glob

from backend.domain.shared.confidence import (
    calculate_confidence
)

from backend.domain.evidence.repository import (
    EvidenceRepository
)


class EvidenceService:

    def __init__(self, db):
        self.repo = EvidenceRepository(db)
        self.db = db


    async def verify(self, evidence_id):

        evidence = await self.repo.get(
            evidence_id
        )

        if not evidence:
            raise Exception("Evidence not found")

        if evidence.status == "VERIFIED":

            return {
                "verified": True,
                "already_verified": True
            }

        files = glob.glob(
            f"/app/backend/storage/uploads/{evidence_id}_*"
        )

        if not files:
            raise Exception(
                "Storage file missing"
            )

        async with aiofiles.open(
            files[0],
            "rb"
        ) as f:

            content = await f.read()

        h = hashlib.sha256(
            content
        ).hexdigest()

        verified = (
            h == evidence.file_hash
        )

        trust = min(
            float(evidence.trust_score)+20,
            100
        )

        confidence = (
            calculate_confidence(
                trust
            )
        )

        await self.repo.update_status(
            evidence_id,
            "VERIFIED",
            trust,
            confidence
        )

        await self.db.commit()

        return {
            "verified": verified,
            "trust_score": trust,
            "confidence": confidence
        }