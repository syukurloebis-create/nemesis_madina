from typing import Dict, List
from datetime import datetime


class LegalReportEngine:
    """
    Generate laporan legal defensibility
    """

    def generate(self, entity_id: str, chain: List[Dict]) -> Dict:

        return {
            "entity_id": entity_id,
            "generated_at": datetime.utcnow().isoformat(),
            "summary": {
                "total_records": len(chain),
                "chain_integrity": "UNKNOWN",
            },
            "timeline": [
                {
                    "timestamp": r["timestamp"],
                    "hash": r["hash"]
                }
                for r in chain
            ]
        }