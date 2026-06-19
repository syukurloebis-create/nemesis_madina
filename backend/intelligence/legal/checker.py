from typing import Dict, Any
from datetime import datetime


class ComplianceChecker:
    def __init__(self):
        self.requirements = {
            "data_retention": {"required": True, "desc": "Data retention policy"},
            "audit_trail": {"required": True, "desc": "Complete audit trail"},
            "encryption": {"required": True, "desc": "Data encryption"}
        }
    
    def check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        for req, info in self.requirements.items():
            results[req] = {"required": info["required"], "met": context.get(req, False)}
        return {
            "compliant": all(r["met"] for r in results.values()),
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
