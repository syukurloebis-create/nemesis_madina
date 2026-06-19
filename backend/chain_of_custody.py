# backend/intelligence/legal/chain_of_custody.py

from datetime import datetime
from typing import Dict, List


class ChainOfCustody:

    def __init__(self):
        self.records: List[Dict] = []

    def record(
        self,
        evidence_id: str,
        actor: str,
        action: str
    ) -> Dict:

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "evidence_id": evidence_id,
            "actor": actor,
            "action": action
        }

        self.records.append(entry)

        return entry

    def get_history(
        self,
        evidence_id: str
    ) -> List[Dict]:

        return [
            r
            for r in self.records
            if r["evidence_id"] == evidence_id
        ]