"""
Legal Report Generator
"""

from typing import Dict, Any, List
from datetime import datetime


class LegalReportGenerator:
    """Generate legal reports"""
    
    def __init__(self):
        self.reports: List[Dict[str, Any]] = []
    
    def generate_evidence_report(self, evidence_data: List[Dict[str, Any]]) -> str:
        """Generate evidence report for legal purposes"""
        report = []
        report.append("=" * 70)
        report.append("LEGAL EVIDENCE REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Total Evidence Items: {len(evidence_data)}")
        report.append("")
        
        for i, evidence in enumerate(evidence_data[:20], 1):  # Limit for readability
            report.append(f"Evidence #{i}")
            report.append(f"  ID: {evidence.get('id', 'N/A')}")
            report.append(f"  Hash: {evidence.get('hash', 'N/A')[:16]}...")
            report.append(f"  Created: {evidence.get('created_at', 'N/A')}")
            report.append(f"  Source: {evidence.get('source', 'N/A')}")
            
            if evidence.get('custody_chain'):
                report.append(f"  Custody Events: {len(evidence['custody_chain'])}")
            
            report.append("")
        
        report.append("=" * 70)
        report.append("This report is generated for legal review purposes.")
        
        return "\n".join(report)
    
    def generate_audit_report(self, audit_data: List[Dict[str, Any]]) -> str:
        """Generate audit report"""
        report = []
        report.append("=" * 70)
        report.append("AUDIT REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Total Audit Entries: {len(audit_data)}")
        report.append("")
        
        # Group by action
        actions = {}
        for entry in audit_data:
            action = entry.get('action', 'unknown')
            actions[action] = actions.get(action, 0) + 1
        
        report.append("Activity Summary:")
        for action, count in actions.items():
            report.append(f"  {action}: {count}")
        
        report.append("")
        report.append("Recent Activities:")
        for entry in audit_data[-10:]:
            report.append(f"  {entry.get('timestamp', 'N/A')}: {entry.get('action', 'N/A')} by {entry.get('actor', 'N/A')}")
        
        return "\n".join(report)
    
    def generate_compliance_report(self, compliance_result: Dict[str, Any]) -> str:
        """Generate compliance report"""
        report = []
        report.append("=" * 70)
        report.append("COMPLIANCE REPORT")
        report.append("=" * 70)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Compliant: {compliance_result.get('compliant', False)}")
        report.append("")
        
        report.append("Requirement Checks:")
        for req, info in compliance_result.get('checks', {}).items():
            status = "[OK]" if info.get('met') else "[ERR]"
            report.append(f"  {status} {req}: {info.get('description', 'N/A')}")
        
        return "\n".join(report)
