"""Audit Logger - Tamper-proof audit trail with hash chain"""

import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

class AuditLogger:
    """Tamper-proof audit logger using blockchain-like hash chain"""
    
    _logs: List[Dict] = []
    _last_hash: str = "0" * 64
    
    @classmethod
    def log(cls, action: str, actor: str, resource: str, data: Dict[str, Any]) -> Dict:
        """Add audit log entry with hash chain"""
        
        entry = {
            "id": len(cls._logs) + 1,
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": actor,
            "resource": resource,
            "data": data,
            "previous_hash": cls._last_hash
        }
        
        # Compute hash of current entry
        entry_str = json.dumps(entry, sort_keys=True, default=str)
        entry["hash"] = hashlib.sha256(entry_str.encode()).hexdigest()
        
        cls._logs.append(entry)
        cls._last_hash = entry["hash"]
        
        return entry
    
    @classmethod
    def get_logs(cls, limit: int = 100, offset: int = 0, event_type: str = None) -> List[Dict]:
        """Get audit logs with pagination"""
        logs = cls._logs
        
        if event_type:
            logs = [l for l in logs if l["action"] == event_type]
        
        return logs[offset:offset + limit]
    
    @classmethod
    def verify_integrity(cls) -> Dict:
        """Verify entire audit log integrity"""
        current_hash = "0" * 64
        verified_count = 0
        failed_count = 0
        
        for log in cls._logs:
            expected_prev = log.get("previous_hash")
            if expected_prev != current_hash:
                failed_count += 1
                continue
            
            # Recompute hash
            log_copy = {k: v for k, v in log.items() if k != "hash"}
            log_copy["previous_hash"] = current_hash
            computed = hashlib.sha256(json.dumps(log_copy, sort_keys=True, default=str).encode()).hexdigest()
            
            if computed != log.get("hash"):
                failed_count += 1
                continue
            
            verified_count += 1
            current_hash = log.get("hash")
        
        return {
            "total_logs": len(cls._logs),
            "verified_count": verified_count,
            "failed_count": failed_count,
            "integrity_intact": failed_count == 0,
            "last_hash": cls._last_hash
        }
    
    @classmethod
    def get_stats(cls) -> Dict:
        """Get audit log statistics"""
        actions = {}
        for log in cls._logs:
            action = log["action"]
            actions[action] = actions.get(action, 0) + 1
        
        return {
            "total_entries": len(cls._logs),
            "actions": actions,
            "first_entry": cls._logs[0]["timestamp"] if cls._logs else None,
            "last_entry": cls._logs[-1]["timestamp"] if cls._logs else None,
            "integrity_verified": cls.verify_integrity()["integrity_intact"]
        }
