from typing import Dict, List
from backend.evidence.registry import EvidenceRegistry


class ChainOfCustody:
    """
    Menjaga rantai bukti tidak bisa dimanipulasi
    """

    def __init__(self, registry: EvidenceRegistry):
        self.registry = registry

    def trace(self, entity_id: str) -> List[Dict]:
        """
        Ambil seluruh history evidence
        """
        return self.registry.get_by_entity(entity_id)

    def verify_chain(self, entity_id: str) -> bool:
        """
        Pastikan seluruh chain valid
        """

        chain = self.trace(entity_id)

        for record in chain:
            expected = record.get("hash")

            temp = record.copy()
            actual = temp.pop("hash", None)

            # re-hash
            from backend.evidence.hashing import EvidenceHashing
            recalculated = EvidenceHashing.hash(temp)

            if recalculated != expected:
                return False

        return True