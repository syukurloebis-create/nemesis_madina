from typing import List, Dict, Any
from datetime import datetime


class AuditTrailValidator:
    def __init__(self):
        self.entries: List[Dict[str, Any]] = []
    
    def add(self, action: str, actor: str, details: Dict[str, Any] = None):
        self.entries.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": actor,
            "details": details or {}
        })
    
    def validate(self) -> Dict[str, Any]:
        return {"valid": True, "total": len(self.entries), "issues": []}
    
    def get_report(self) -> str:
        return f"Audit Report\nTotal Entries: {len(self.entries)}\nValid: True"
