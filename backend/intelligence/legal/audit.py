"""
Audit Trail Validator
"""

from typing import List, Dict, Any
from datetime import datetime


class AuditTrailValidator:
    """Validate audit trail integrity"""
    
    def __init__(self):
        self.audit_entries: List[Dict[str, Any]] = []
    
    def add_entry(self, action: str, actor: str, details: Dict[str, Any]):
        """Add audit entry"""
        self.audit_entries.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "actor": actor,
            "details": details
        })
    
    def validate_chain(self) -> Dict[str, Any]:
        """Validate audit chain integrity"""
        if len(self.audit_entries) < 2:
            return {"valid": True, "message": "Insufficient entries"}
        
        issues = []
        prev_timestamp = None
        
        for i, entry in enumerate(self.audit_entries):
            current_timestamp = datetime.fromisoformat(entry["timestamp"])
            
            if prev_timestamp and current_timestamp < prev_timestamp:
                issues.append(f"Non-chronological entry at index {i}")
            
            prev_timestamp = current_timestamp
        
        return {
            "valid": len(issues) == 0,
            "total_entries": len(self.audit_entries),
            "issues": issues
        }
    
    def get_report(self) -> str:
        """Generate audit report"""
        validation = self.validate_chain()
        
        report = []
        report.append("=" * 60)
        report.append("AUDIT TRAIL REPORT")
        report.append("=" * 60)
        report.append(f"Total Entries: {validation['total_entries']}")
        report.append(f"Chain Valid: {validation['valid']}")
        
        if validation['issues']:
            report.append("Issues Found:")
            for issue in validation['issues']:
                report.append(f"  - {issue}")
        
        report.append("Recent Entries:")
        for entry in self.audit_entries[-5:]:
            report.append(f"  {entry['timestamp']}: {entry['action']} by {entry['actor']}")
        
        return "\n".join(report)
