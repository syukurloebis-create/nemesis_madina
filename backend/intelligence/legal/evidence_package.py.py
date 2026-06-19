from typing import Dict, List
from datetime import datetime


class EvidencePackage:
    """
    Menggabungkan evidence menjadi satu paket legal
    """

    def build(self, entity_id: str, evidences: List[Dict]) -> Dict:
        return {
            "entity_id": entity_id,
            "created_at": datetime.utcnow().isoformat(),
            "total_evidence": len(evidences),
            "evidences": evidences,
        }