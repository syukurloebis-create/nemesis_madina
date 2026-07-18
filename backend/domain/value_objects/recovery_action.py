"""
NEMESIS Madina - Recovery Action Value Object
"""

from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import Optional, Tuple


class ActionPriority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4
    
    def __str__(self) -> str:
        return self.name


class ActionType(Enum):
    INVESTIGATE_VENDORS = "INVESTIGATE_VENDORS"
    REVIEW_PACKAGES = "REVIEW_PACKAGES"
    REVIEW_EVIDENCE = "REVIEW_EVIDENCE"
    RECOVER_FINDING = "RECOVER_FINDING"
    ESCALATE = "ESCALATE"


@dataclass(frozen=True)
class RecoveryAction:
    """
    Immutable recovery action.
    ✅ Domain Value Object, no description
    ✅ sort_index enables sorting by priority then confidence
    """
    
    action_type: ActionType
    priority: ActionPriority
    confidence: float
    target: Optional[str] = None  # finding_id, vendor_id, etc.
    
    sort_index: Tuple[int, float] = field(init=False)
    
    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "sort_index",
            (-self.priority.value, -self.confidence)
        )
    
    def __lt__(self, other: "RecoveryAction") -> bool:
        return self.sort_index < other.sort_index
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RecoveryAction):
            return False
        return self.sort_index == other.sort_index