# backend/domain/value_objects.py
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


class CaseStatus(str, Enum):
    """
    Canonical case status - SINGLE SOURCE OF TRUTH.
    Semua status lain (workflow, projection) harus merujuk ke sini.
    """
    DRAFT = "draft"
    OPEN = "open"
    ASSIGNED = "assigned"
    INVESTIGATING = "investigating"
    VERIFYING = "verifying"
    RESOLVED = "resolved"
    CLOSED = "closed"
    ARCHIVED = "archived"
    
    @classmethod
    def from_string(cls, value: str) -> "CaseStatus":
        """Convert string to enum with safe fallback"""
        try:
            return cls(value.lower())
        except ValueError:
            return cls.DRAFT
    
    def is_active(self) -> bool:
        """Check if case is still active (not closed/archived)"""
        return self not in [CaseStatus.CLOSED, CaseStatus.ARCHIVED]
    
    def can_transition_to(self, new_status: "CaseStatus") -> bool:
        """Check if status transition is valid"""
        valid_transitions = {
            CaseStatus.DRAFT: [CaseStatus.OPEN, CaseStatus.ARCHIVED],
            CaseStatus.OPEN: [CaseStatus.ASSIGNED, CaseStatus.CLOSED, CaseStatus.ARCHIVED],
            CaseStatus.ASSIGNED: [CaseStatus.INVESTIGATING, CaseStatus.OPEN, CaseStatus.CLOSED],
            CaseStatus.INVESTIGATING: [CaseStatus.VERIFYING, CaseStatus.ASSIGNED, CaseStatus.CLOSED],
            CaseStatus.VERIFYING: [CaseStatus.RESOLVED, CaseStatus.INVESTIGATING, CaseStatus.CLOSED],
            CaseStatus.RESOLVED: [CaseStatus.CLOSED, CaseStatus.VERIFYING],
            CaseStatus.CLOSED: [CaseStatus.ARCHIVED],
            CaseStatus.ARCHIVED: []
        }
        return new_status in valid_transitions.get(self, [])


class CasePriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_string(cls, value: str) -> "CasePriority":
        try:
            return cls(value.lower())
        except ValueError:
            return cls.MEDIUM


@dataclass
class CaseState:
    """
    Canonical case state - SINGLE SOURCE OF TRUTH.
    Workflow, timeline, dan projection HARUS membaca dari sini.
    """
    case_id: str
    title: str
    description: str
    status: CaseStatus
    priority: CasePriority
    assigned_to: Optional[str] = None
    evidence_count: int = 0
    finding_count: int = 0
    evidence_ids: list = None
    finding_ids: list = None
    version: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    closed_by: Optional[str] = None
    
    def __post_init__(self):
        if self.evidence_ids is None:
            self.evidence_ids = []
        if self.finding_ids is None:
            self.finding_ids = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "case_id": self.case_id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority.value,
            "assigned_to": self.assigned_to,
            "evidence_count": self.evidence_count,
            "finding_count": self.finding_count,
            "evidence_ids": self.evidence_ids,
            "finding_ids": self.finding_ids,
            "version": self.version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "closed_by": self.closed_by
        }
    
    @classmethod
    def from_aggregate(cls, aggregate) -> "CaseState":
        """Create state from CaseAggregate"""
        return cls(
            case_id=aggregate.id,
            title=aggregate.title,
            description=aggregate.description,
            status=aggregate.status if isinstance(aggregate.status, CaseStatus) else CaseStatus.from_string(str(aggregate.status)),
            priority=aggregate.priority if isinstance(aggregate.priority, CasePriority) else CasePriority.from_string(str(aggregate.priority)),
            assigned_to=aggregate.assigned_to,
            evidence_count=getattr(aggregate, 'evidence_count', 0),
            finding_count=getattr(aggregate, 'finding_count', 0),
            evidence_ids=getattr(aggregate, 'evidence_ids', []),
            finding_ids=getattr(aggregate, 'finding_ids', []),
            version=aggregate.version,
            created_at=aggregate.created_at,
            updated_at=aggregate.updated_at,
            closed_at=getattr(aggregate, 'closed_at', None),
            closed_by=getattr(aggregate, 'closed_by', None)
        )
    
    def get_workflow_steps(self) -> list:
        """Generate workflow steps from state"""
        steps = []
        
        # Step 1: Creation
        steps.append({
            "step": "case_created",
            "status": "open",
            "timestamp": self.created_at,
            "user": None  # Would need user info from events
        })
        
        # Step 2: Assignment
        if self.assigned_to:
            steps.append({
                "step": "case_assigned",
                "status": "assigned",
                "timestamp": self.updated_at,
                "user": None,
                "assignee": self.assigned_to
            })
        
        # Step 3: Investigation (if evidence added)
        if self.evidence_count > 0:
            steps.append({
                "step": "investigation",
                "status": "investigating",
                "timestamp": self.updated_at,
                "evidence_count": self.evidence_count
            })
        
        # Step 4: Closure
        if self.status == CaseStatus.CLOSED:
            steps.append({
                "step": "case_closed",
                "status": "closed",
                "timestamp": self.closed_at,
                "closed_by": self.closed_by
            })
        
        return steps


class WorkflowStatus:
    """
    Workflow status derived from canonical case state.
    BUKAN source of truth, hanya view dari CaseStatus.
    """
    
    @staticmethod
    def from_case_status(status: CaseStatus) -> str:
        """Map case status to workflow display status"""
        mapping = {
            CaseStatus.DRAFT: "draft",
            CaseStatus.OPEN: "open",
            CaseStatus.ASSIGNED: "assigned",
            CaseStatus.INVESTIGATING: "investigating",
            CaseStatus.VERIFYING: "verifying",
            CaseStatus.RESOLVED: "resolved",
            CaseStatus.CLOSED: "closed",
            CaseStatus.ARCHIVED: "archived"
        }
        return mapping.get(status, "unknown")
    
    @staticmethod
    def get_display_name(status: CaseStatus) -> str:
        """Get human-readable display name"""
        names = {
            CaseStatus.DRAFT: "Draft",
            CaseStatus.OPEN: "Open",
            CaseStatus.ASSIGNED: "Assigned",
            CaseStatus.INVESTIGATING: "Investigating",
            CaseStatus.VERIFYING: "Verifying",
            CaseStatus.RESOLVED: "Resolved",
            CaseStatus.CLOSED: "Closed",
            CaseStatus.ARCHIVED: "Archived"
        }
        return names.get(status, "Unknown")