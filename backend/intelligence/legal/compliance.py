"""
Compliance Checker
"""

from typing import Dict, Any, List, Tuple


class ComplianceChecker:
    """Check compliance with regulations"""
    
    def __init__(self):
        self.requirements = {
            "data_retention": {"required": True, "description": "Data retention policy"},
            "audit_trail": {"required": True, "description": "Complete audit trail"},
            "encryption": {"required": True, "description": "Data encryption at rest"},
            "access_control": {"required": True, "description": "Access control"},
            "evidence_integrity": {"required": True, "description": "Evidence integrity verification"}
        }
    
    def check(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance for given context"""
        results = {}
        
        for req_name, req_info in self.requirements.items():
            is_met = context.get(req_name, False)
            results[req_name] = {
                "required": req_info["required"],
                "met": is_met,
                "description": req_info["description"]
            }
        
        overall = all(r["met"] for r in results.values())
        
        return {
            "compliant": overall,
            "checks": results,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_violations(self, context: Dict[str, Any]) -> List[str]:
        """Get list of compliance violations"""
        result = self.check(context)
        return [
            f"{req}: {info['description']}"
            for req, info in result["checks"].items()
            if not info["met"]
        ]
    
    def generate_certificate(self, context: Dict[str, Any]) -> str:
        """Generate compliance certificate"""
        result = self.check(context)
        
        if not result["compliant"]:
            return "Compliance check failed. Cannot generate certificate."
        
        return f"""
COMPLIANCE CERTIFICATE
======================
Status: COMPLIANT
Timestamp: {result['timestamp']}

All requirements satisfied:
{chr(10).join(f'  [OK] {req}: {info["description"]}' for req, info in result["checks"].items())}

This certificate confirms that the system meets all compliance requirements.
"""
