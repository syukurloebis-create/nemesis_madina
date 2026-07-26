# scripts/policy/engine.py
from enum import Enum
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

class PolicyAction(Enum):
    IGNORE = "ignore"
    WARN = "warn"
    WAIVER = "waiver"
    SOFT_FAIL = "soft_fail"
    HARD_FAIL = "hard_fail"
    EXCEPTION = "exception"

@dataclass
class Policy:
    """Governance policy"""
    id: str
    name: str
    description: str
    rule_ids: List[str]
    action: PolicyAction
    waiver_required: bool = False
    exception_required: bool = False
    review_required: bool = False
    owner: str = ""
    created_at: datetime = None

@dataclass
class Waiver:
    """Policy waiver"""
    id: str
    policy_id: str
    rule_id: str
    module: str
    reason: str
    approved_by: str
    expires_at: Optional[datetime] = None
    created_at: datetime = None

class PolicyEngine:
    """Governance policy engine"""
    
    def __init__(self, rule_engine: IRuleEngine):
        self.rule_engine = rule_engine
        self.policies: Dict[str, Policy] = {}
        self.waivers: Dict[str, Waiver] = {}
        self.exceptions: Dict[str, Policy] = {}
    
    def add_policy(self, policy: Policy):
        """Add a governance policy"""
        self.policies[policy.id] = policy
    
    def evaluate(self, inventory: IInventoryQuery) -> Dict[str, Any]:
        """Evaluate policies against inventory"""
        violations = self.rule_engine.evaluate(inventory)
        results = {}
        
        for policy in self.policies.values():
            policy_violations = [
                v for v in violations 
                if v['rule_id'] in policy.rule_ids
            ]
            
            # Check waivers
            waived_violations = []
            for v in policy_violations:
                if self._has_waiver(policy.id, v['rule_id'], v.get('module')):
                    waived_violations.append(v)
            
            # Determine action
            action = policy.action
            if waived_violations and policy.waiver_required:
                action = PolicyAction.WARN  # Waived but still warn
            
            results[policy.id] = {
                'policy': policy,
                'violations': policy_violations,
                'waived': waived_violations,
                'action': action,
                'status': self._get_status(action)
            }
        
        return results
    
    def _has_waiver(self, policy_id: str, rule_id: str, module: str) -> bool:
        """Check if violation has a waiver"""
        for waiver in self.waivers.values():
            if (waiver.policy_id == policy_id and 
                waiver.rule_id == rule_id and 
                waiver.module == module):
                if waiver.expires_at is None or waiver.expires_at > datetime.now():
                    return True
        return False
    
    def _get_status(self, action: PolicyAction) -> str:
        """Get status based on action"""
        status_map = {
            PolicyAction.IGNORE: "ignored",
            PolicyAction.WARN: "warning",
            PolicyAction.WAIVER: "waived",
            PolicyAction.SOFT_FAIL: "soft_fail",
            PolicyAction.HARD_FAIL: "hard_fail",
            PolicyAction.EXCEPTION: "exception"
        }
        return status_map.get(action, "unknown")
    
    def request_waiver(self, policy_id: str, rule_id: str, 
                       module: str, reason: str, 
                       approved_by: str, expires_at: Optional[datetime] = None):
        """Request a policy waiver"""
        waiver = Waiver(
            id=str(uuid.uuid4()),
            policy_id=policy_id,
            rule_id=rule_id,
            module=module,
            reason=reason,
            approved_by=approved_by,
            expires_at=expires_at,
            created_at=datetime.now()
        )
        self.waivers[waiver.id] = waiver
        return waiver