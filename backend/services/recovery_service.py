"""
Recovery Service - Generate recovery actions
"""

from typing import Dict, Any, List


class RecoveryService:
    """Service untuk generate recovery actions."""
    
    @staticmethod
    async def get_recovery_actions(case_id: str, intelligence_data: Dict) -> List[Dict]:
        """Generate recovery actions based on intelligence data."""
        actions = []
        
        # Recovery actions berdasarkan fraud level
        fraud = intelligence_data.get("fraud", {})
        if fraud.get("overall_risk") == "CRITICAL":
            actions.append({
                "action": "Immediate enforcement action required",
                "priority": "CRITICAL",
                "status": "PENDING",
                "notes": "Fraud risk is critical, immediate intervention needed"
            })
        
        # Recovery actions berdasarkan evidence
        evidence = intelligence_data.get("evidence", {})
        if evidence.get("verified", 0) < evidence.get("total", 0) * 0.5:
            actions.append({
                "action": "Verify pending evidence",
                "priority": "HIGH",
                "status": "PENDING",
                "notes": f"Only {evidence.get('verified', 0)} of {evidence.get('total', 0)} evidence verified"
            })
        
        # Recovery actions berdasarkan graph
        graph = intelligence_data.get("graph", {})
        if graph.get("entities", 0) > 100:
            actions.append({
                "action": "Investigate graph network",
                "priority": "MEDIUM",
                "status": "PENDING",
                "notes": f"Large graph network with {graph.get('entities', 0)} entities"
            })
        
        return actions