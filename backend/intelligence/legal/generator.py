from typing import List, Dict, Any
from datetime import datetime


class LegalReportGenerator:
    def generate_evidence_report(self, evidence_list: List[Dict[str, Any]]) -> str:
        return f"LEGAL EVIDENCE REPORT\nGenerated: {datetime.now().isoformat()}\nTotal Items: {len(evidence_list)}"
    
    def generate_audit_report(self, audit_data: List[Dict[str, Any]]) -> str:
        return f"AUDIT REPORT\nGenerated: {datetime.now().isoformat()}\nTotal Entries: {len(audit_data)}"
