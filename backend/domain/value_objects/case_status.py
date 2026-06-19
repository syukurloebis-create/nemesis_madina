# backend/domain/value_objects/case_status.py
from enum import Enum
from typing import Optional

class CaseStatus(str, Enum):
    """Case status value object"""
    DRAFT = "draft"
    OPEN = "open"
    INVESTIGATING = "investigating"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    CLOSED = "closed"
    
    @classmethod
    def from_string(cls, value: str) -> Optional["CaseStatus"]:
        try:
            return cls(value.lower())
        except ValueError:
            return None
    
    def can_transition_to(self, new_status: "CaseStatus") -> bool:
        """Check if status transition is valid"""
        transitions = {
            CaseStatus.DRAFT: [CaseStatus.OPEN, CaseStatus.CLOSED],
            CaseStatus.OPEN: [CaseStatus.INVESTIGATING, CaseStatus.CLOSED],
            CaseStatus.INVESTIGATING: [CaseStatus.VERIFYING, CaseStatus.CLOSED],
            CaseStatus.VERIFYING: [CaseStatus.RESOLVED, CaseStatus.CLOSED],
            CaseStatus.RESOLVED: [CaseStatus.CLOSED],
            CaseStatus.CLOSED: []
        }
        return new_status in transitions.get(self, [])


class CasePriority(str, Enum):
    """Case priority value object"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_string(cls, value: str) -> Optional["CasePriority"]:
        try:
            return cls(value.lower())
        except ValueError:
            return None
    
    def get_weight(self) -> int:
        """Get numeric weight for priority"""
        weights = {
            CasePriority.LOW: 1,
            CasePriority.MEDIUM: 2,
            CasePriority.HIGH: 3,
            CasePriority.CRITICAL: 4
        }
        return weights.get(self, 2)
