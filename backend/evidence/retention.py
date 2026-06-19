# backend/evidence/retention.py
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid


class RetentionAction(str, Enum):
    """Actions for retention management"""
    KEEP = "KEEP"
    ARCHIVE = "ARCHIVE"
    PURGE = "PURGE"
    REVIEW = "REVIEW"
    EXTEND = "EXTEND"


@dataclass
class RetentionPolicy:
    """Retention policy untuk evidence"""
    policy_id: str
    name: str
    description: str
    base_days: int
    extensions: List[Dict[str, Any]] = field(default_factory=list)
    
    def calculate_retention_date(self, created_at: datetime) -> datetime:
        """Calculate retention date based on policy"""
        retention_date = created_at + timedelta(days=self.base_days)
        
        # Apply extensions
        for extension in self.extensions:
            if extension.get("condition") == "CASE_ACTIVE":
                retention_date += timedelta(days=extension.get("days", 0))
            elif extension.get("condition") == "HIGH_RISK":
                retention_date += timedelta(days=extension.get("days", 0))
        
        return retention_date
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "base_days": self.base_days,
            "extensions": self.extensions
        }


class RetentionPolicyRegistry:
    """Registry for retention policies"""
    
    def __init__(self):
        self._policies: Dict[str, RetentionPolicy] = {}
        self._init_policies()
    
    def _init_policies(self):
        """Initialize default retention policies"""
        
        # Standard document policy
        self._policies["DOCUMENT_STANDARD"] = RetentionPolicy(
            policy_id="DOCUMENT_STANDARD",
            name="Standard Document Retention",
            description="Standard retention for general documents",
            base_days=365 * 5,  # 5 years
            extensions=[
                {"condition": "CASE_ACTIVE", "days": 365, "description": "Extended while case active"},
                {"condition": "HIGH_RISK", "days": 365 * 2, "description": "Extended for high risk cases"}
            ]
        )
        
        # Financial record policy
        self._policies["FINANCIAL_RECORD"] = RetentionPolicy(
            policy_id="FINANCIAL_RECORD",
            name="Financial Record Retention",
            description="Retention for financial records (10 years per regulation)",
            base_days=365 * 10,  # 10 years
            extensions=[
                {"condition": "CASE_ACTIVE", "days": 365},
                {"condition": "UNDER_INVESTIGATION", "days": 365 * 5}
            ]
        )
        
        # Investigation evidence policy
        self._policies["INVESTIGATION_EVIDENCE"] = RetentionPolicy(
            policy_id="INVESTIGATION_EVIDENCE",
            name="Investigation Evidence Retention",
            description="Retention for investigation evidence",
            base_days=365 * 10,  # 10 years
            extensions=[
                {"condition": "CASE_ACTIVE", "days": 365},
                {"condition": "LEGAL_HOLD", "days": 365 * 20, "description": "Extended for legal hold"}
            ]
        )
        
        # Interview recording policy
        self._policies["INTERVIEW_RECORDING"] = RetentionPolicy(
            policy_id="INTERVIEW_RECORDING",
            name="Interview Recording Retention",
            description="Retention for interview recordings",
            base_days=365 * 5,  # 5 years
            extensions=[
                {"condition": "CASE_ACTIVE", "days": 365},
                {"condition": "LEGAL_HOLD", "days": 365 * 10}
            ]
        )
        
        # System log policy
        self._policies["SYSTEM_LOG"] = RetentionPolicy(
            policy_id="SYSTEM_LOG",
            name="System Log Retention",
            description="Retention for system logs",
            base_days=365 * 2,  # 2 years
            extensions=[]
        )
        
        # External intelligence policy
        self._policies["EXTERNAL_INTELLIGENCE"] = RetentionPolicy(
            policy_id="EXTERNAL_INTELLIGENCE",
            name="External Intelligence Retention",
            description="Retention for external intelligence",
            base_days=365 * 3,  # 3 years
            extensions=[
                {"condition": "CASE_ACTIVE", "days": 365},
                {"condition": "HIGH_RISK", "days": 365 * 2}
            ]
        )
    
    def get_policy(self, policy_id: str) -> Optional[RetentionPolicy]:
        """Get policy by ID"""
        return self._policies.get(policy_id)
    
    def get_policy_for_evidence_type(self, evidence_type: str, classification: str) -> str:
        """Get appropriate policy ID for evidence type and classification"""
        
        mapping = {
            "DOCUMENT": "DOCUMENT_STANDARD",
            "FINANCIAL_RECORD": "FINANCIAL_RECORD",
            "PROCUREMENT_RECORD": "FINANCIAL_RECORD",
            "INTERVIEW": "INTERVIEW_RECORDING",
            "EXTERNAL_INTELLIGENCE": "EXTERNAL_INTELLIGENCE",
            "SYSTEM_LOG": "SYSTEM_LOG"
        }
        
        return mapping.get(evidence_type, "DOCUMENT_STANDARD")


class RetentionEngine:
    """Engine for managing evidence retention"""
    
    def __init__(self):
        self.policy_registry = RetentionPolicyRegistry()
    
    def get_retention_date(
        self,
        evidence_type: str,
        classification: str,
        created_at: datetime,
        case_status: str = "ACTIVE",
        risk_level: str = "MEDIUM",
        legal_hold: bool = False
    ) -> datetime:
        """Calculate retention date for evidence"""
        
        policy_id = self.policy_registry.get_policy_for_evidence_type(evidence_type, classification)
        policy = self.policy_registry.get_policy(policy_id)
        
        if not policy:
            policy = self.policy_registry.get_policy("DOCUMENT_STANDARD")
        
        retention_date = policy.calculate_retention_date(created_at)
        
        # Apply case-based adjustments
        if case_status == "ACTIVE":
            retention_date += timedelta(days=365)
        
        if risk_level == "HIGH" or risk_level == "CRITICAL":
            retention_date += timedelta(days=365 * 2)
        
        if legal_hold:
            retention_date += timedelta(days=365 * 20)
        
        return retention_date
    
    def determine_action(
        self,
        retention_date: datetime,
        current_date: datetime = None
    ) -> Dict[str, Any]:
        """Determine what action should be taken based on retention date"""
        
        if current_date is None:
            current_date = datetime.utcnow()
        
        days_until_retention = (retention_date - current_date).days
        
        if days_until_retention < 0:
            action = RetentionAction.PURGE
            urgency = "CRITICAL"
            message = "Retention period has expired - immediate action required"
        elif days_until_retention < 30:
            action = RetentionAction.REVIEW
            urgency = "HIGH"
            message = f"Retention period expires in {days_until_retention} days - review required"
        elif days_until_retention < 90:
            action = RetentionAction.REVIEW
            urgency = "MEDIUM"
            message = f"Retention period expires in {days_until_retention} days - schedule review"
        elif days_until_retention < 180:
            action = RetentionAction.KEEP
            urgency = "LOW"
            message = f"Retention period expires in {days_until_retention} days - monitoring"
        else:
            action = RetentionAction.KEEP
            urgency = "INFO"
            message = f"Evidence within retention period ({days_until_retention} days remaining)"
        
        return {
            "action": action.value,
            "urgency": urgency,
            "message": message,
            "days_until_retention": days_until_retention,
            "retention_date": retention_date.isoformat()
        }
    
    def get_retention_report(
        self,
        evidence_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate retention report for a list of evidence"""
        
        report = {
            "total_evidence": len(evidence_list),
            "expired": [],
            "expiring_soon": [],
            "within_retention": [],
            "by_action": {
                "PURGE": 0,
                "REVIEW": 0,
                "KEEP": 0
            }
        }
        
        for evidence in evidence_list:
            retention_date = self.get_retention_date(
                evidence_type=evidence.get("evidence_type", "DOCUMENT"),
                classification=evidence.get("classification", "CONFIDENTIAL"),
                created_at=evidence.get("created_at", datetime.utcnow()),
                case_status=evidence.get("case_status", "ACTIVE"),
                risk_level=evidence.get("risk_level", "MEDIUM"),
                legal_hold=evidence.get("legal_hold", False)
            )
            
            action_result = self.determine_action(retention_date)
            
            evidence_report = {
                "evidence_id": str(evidence.get("evidence_id")),
                "name": evidence.get("filename", "Unknown"),
                "evidence_type": evidence.get("evidence_type"),
                "created_at": evidence.get("created_at").isoformat() if evidence.get("created_at") else None,
                "retention_date": retention_date.isoformat(),
                "action": action_result["action"],
                "urgency": action_result["urgency"],
                "message": action_result["message"]
            }
            
            if action_result["action"] == RetentionAction.PURGE.value:
                report["expired"].append(evidence_report)
                report["by_action"]["PURGE"] += 1
            elif action_result["action"] == RetentionAction.REVIEW.value:
                report["expiring_soon"].append(evidence_report)
                report["by_action"]["REVIEW"] += 1
            else:
                report["within_retention"].append(evidence_report)
                report["by_action"]["KEEP"] += 1
        
        return report


# Singleton instance
_retention_engine = None

def get_retention_engine() -> RetentionEngine:
    """Get singleton retention engine"""
    global _retention_engine
    if _retention_engine is None:
        _retention_engine = RetentionEngine()
    return _retention_engine