"""
Human Approval Flow
Workflow untuk approval keputusan
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ApprovalLevel(str, Enum):
    """Level approval"""
    TEAM_LEAD = "team_lead"
    MANAGER = "manager"
    DIRECTOR = "director"
    EXECUTIVE = "executive"


class ApprovalStatus(str, Enum):
    """Status approval"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"


@dataclass
class Approval:
    """Approval record"""
    id: str
    decision_id: str
    level: ApprovalLevel
    approver_id: str
    approver_name: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    comment: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "level": self.level.value,
            "approver_id": self.approver_id,
            "approver_name": self.approver_name,
            "status": self.status.value,
            "comment": self.comment,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_at": self.created_at.isoformat()
        }


class ApprovalWorkflow:
    """
    Human Approval Flow
    Mengelola workflow approval
    """

    def __init__(self):
        self.approvals: Dict[str, List[Approval]] = {}
        self.approval_levels = [
            ApprovalLevel.TEAM_LEAD,
            ApprovalLevel.MANAGER,
            ApprovalLevel.DIRECTOR,
            ApprovalLevel.EXECUTIVE
        ]

    def create_approval_chain(
        self,
        decision_id: str,
        approvers: Dict[ApprovalLevel, str]
    ) -> List[Approval]:
        """
        Create approval chain for a decision
        """
        approvals = []

        for level in self.approval_levels:
            if level in approvers:
                approval = Approval(
                    id=f"appr_{decision_id}_{level.value}",
                    decision_id=decision_id,
                    level=level,
                    approver_id=approvers[level],
                    approver_name=f"{level.value.capitalize()} Approver"
                )
                approvals.append(approval)
            else:
                # Auto-approve if no approver specified
                approval = Approval(
                    id=f"appr_{decision_id}_{level.value}",
                    decision_id=decision_id,
                    level=level,
                    approver_id="system",
                    approver_name="System",
                    status=ApprovalStatus.APPROVED,
                    approved_at=datetime.now()
                )
                approvals.append(approval)

        self.approvals[decision_id] = approvals
        logger.info(f"Approval chain created for decision {decision_id}")

        return approvals

    def get_approvals(self, decision_id: str) -> List[Approval]:
        """Get all approvals for a decision"""
        return self.approvals.get(decision_id, [])

    def get_pending_approvals(self, decision_id: str) -> List[Approval]:
        """Get pending approvals for a decision"""
        return [a for a in self.approvals.get(decision_id, [])
                if a.status == ApprovalStatus.PENDING]

    def approve(self, decision_id: str, level: ApprovalLevel, approver_id: str) -> bool:
        """Approve at a specific level"""
        approvals = self.approvals.get(decision_id, [])
        for approval in approvals:
            if approval.level == level and approval.status == ApprovalStatus.PENDING:
                approval.status = ApprovalStatus.APPROVED
                approval.approved_at = datetime.now()
                logger.info(f"Decision {decision_id} approved at {level.value} level")
                return True

        # Check if all approvals are done
        if self.is_fully_approved(decision_id):
            logger.info(f"Decision {decision_id} fully approved")
            return True

        return False

    def reject(self, decision_id: str, level: ApprovalLevel, approver_id: str, reason: str) -> bool:
        """Reject at a specific level"""
        approvals = self.approvals.get(decision_id, [])
        for approval in approvals:
            if approval.level == level and approval.status == ApprovalStatus.PENDING:
                approval.status = ApprovalStatus.REJECTED
                approval.comment = reason
                approval.approved_at = datetime.now()
                logger.info(f"Decision {decision_id} rejected at {level.value} level: {reason}")
                return True
        return False

    def escalate(self, decision_id: str, level: ApprovalLevel) -> bool:
        """Escalate to next approval level"""
        approvals = self.approvals.get(decision_id, [])
        for i, approval in enumerate(approvals):
            if approval.level == level and approval.status == ApprovalStatus.PENDING:
                approval.status = ApprovalStatus.ESCALATED
                # Check if there's a next level
                if i + 1 < len(approvals):
                    next_approval = approvals[i + 1]
                    if next_approval.status == ApprovalStatus.PENDING:
                        logger.info(f"Decision {decision_id} escalated from {level.value} to {next_approval.level.value}")
                        return True
        return False

    def is_fully_approved(self, decision_id: str) -> bool:
        """Check if decision is fully approved"""
        approvals = self.approvals.get(decision_id, [])
        if not approvals:
            return False
        return all(a.status == ApprovalStatus.APPROVED for a in approvals)

    def get_approval_status(self, decision_id: str) -> Dict[str, Any]:
        """Get approval status summary"""
        approvals = self.approvals.get(decision_id, [])
        if not approvals:
            return {"status": "no_approvals", "progress": "0%"}
        approved = sum(1 for a in approvals if a.status == ApprovalStatus.APPROVED)
        total = len(approvals)
        return {
            "status": "approved" if self.is_fully_approved(decision_id) else "pending",
            "progress": f"{approved}/{total}",
            "percentage": (approved / total * 100) if total > 0 else 0,
            "approvals": [a.to_dict() for a in approvals]
        }


# Singleton instance
approval_workflow = ApprovalWorkflow()