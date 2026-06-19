# backend/intelligence/legal/audit_trail_validator.py

from .evidence_hashing import EvidenceHashing


class AuditTrailValidator:

    @staticmethod
    def verify(record):

        expected = EvidenceHashing.hash_evidence(
            record["payload"]
        )

        return expected == record["hash"]