"""
Decision Engine
Mengelola keputusan berbasis intelligence
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)


class DecisionType(str, Enum):
    """Tipe keputusan"""
    RECOMMENDATION = "recommendation"
    APPROVAL = "approval"
    ESCALATION = "escalation"
    ACTION = "action"
    REJECTION = "rejection"


class DecisionStatus(str, Enum):
    """Status keputusan"""
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Decision:
    """Keputusan"""
    id: UUID = field(default_factory=uuid4)
    case_id: str = ""
    type: DecisionType = DecisionType.RECOMMENDATION
    title: str = ""
    description: str = ""
    rationale: str = ""
    priority: str = "medium"
    confidence: float = 0.0
    impact: float = 0.0
    estimated_recovery: float = 0.0
    options: List[Dict[str, Any]] = field(default_factory=list)
    selected_option: Optional[Dict[str, Any]] = None
    status: DecisionStatus = DecisionStatus.PENDING
    created_by: str = "system"
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "case_id": self.case_id,
            "type": self.type.value,
            "title": self.title,
            "description": self.description,
            "rationale": self.rationale,
            "priority": self.priority,
            "confidence": self.confidence,
            "impact": self.impact,
            "estimated_recovery": self.estimated_recovery,
            "options": self.options,
            "selected_option": self.selected_option,
            "status": self.status.value,
            "created_by": self.created_by,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "implemented_at": self.implemented_at.isoformat() if self.implemented_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

    def approve(self, approver: str) -> None:
        """Approve decision"""
        self.status = DecisionStatus.APPROVED
        self.approved_by = approver
        self.approved_at = datetime.now()
        self.updated_at = datetime.now()
        logger.info(f"Decision {self.id} approved by {approver}")

    def reject(self, approver: str, reason: str) -> None:
        """Reject decision"""
        self.status = DecisionStatus.REJECTED
        self.approved_by = approver
        self.approved_at = datetime.now()
        self.metadata["rejection_reason"] = reason
        self.updated_at = datetime.now()
        logger.info(f"Decision {self.id} rejected by {approver}: {reason}")

    def implement(self) -> None:
        """Mark decision as implemented"""
        self.status = DecisionStatus.IMPLEMENTED
        self.implemented_at = datetime.now()
        self.updated_at = datetime.now()
        logger.info(f"Decision {self.id} implemented")

    def complete(self) -> None:
        """Mark decision as completed"""
        self.status = DecisionStatus.COMPLETED
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        logger.info(f"Decision {self.id} completed")


class DecisionEngine:
    """
    Decision Engine
    Menghasilkan dan mengelola keputusan
    """

    def __init__(self):
        self.decisions: Dict[str, Decision] = {}

    def create_decision(
        self,
        case_id: str,
        recommendations: List[Dict[str, Any]],
        options: List[Dict[str, Any]]
    ) -> Decision:
        """
        Create decision from recommendations
        """
        if not recommendations:
            raise ValueError("No recommendations provided")

        # Get top recommendation
        top_recommendation = recommendations[0]

        decision = Decision(
            case_id=case_id,
            type=DecisionType.RECOMMENDATION,
            title=top_recommendation.get("title", "Decision Required"),
            description=top_recommendation.get("description", ""),
            rationale=top_recommendation.get("reasoning", ""),
            priority=top_recommendation.get("priority", "medium"),
            confidence=top_recommendation.get("confidence", 0.8),
            impact=top_recommendation.get("impact", 0),
            estimated_recovery=top_recommendation.get("estimated_recovery", 0),
            options=options,
            created_by="system"
        )

        self.decisions[str(decision.id)] = decision
        logger.info(f"Decision created: {decision.id} for case {case_id}")

        return decision

    def get_decision(self, decision_id: str) -> Optional[Decision]:
        """Get decision by ID"""
        return self.decisions.get(decision_id)

    def get_decisions_by_case(self, case_id: str) -> List[Decision]:
        """Get all decisions for a case"""
        return [d for d in self.decisions.values() if d.case_id == case_id]

    def get_decisions_by_status(self, status: DecisionStatus) -> List[Decision]:
        """Get decisions by status"""
        return [d for d in self.decisions.values() if d.status == status]

    def get_pending_decisions(self) -> List[Decision]:
        """Get all pending decisions"""
        return self.get_decisions_by_status(DecisionStatus.PENDING)

    def get_decisions_by_type(self, decision_type: DecisionType) -> List[Decision]:
        """Get decisions by type"""
        return [d for d in self.decisions.values() if d.type == decision_type]

    def approve_decision(self, decision_id: str, approver: str) -> bool:
        """Approve a decision"""
        decision = self.get_decision(decision_id)
        if not decision:
            return False
        if decision.status != DecisionStatus.PENDING:
            return False
        decision.approve(approver)
        return True

    def reject_decision(self, decision_id: str, approver: str, reason: str) -> bool:
        """Reject a decision"""
        decision = self.get_decision(decision_id)
        if not decision:
            return False
        if decision.status not in [DecisionStatus.PENDING, DecisionStatus.UNDER_REVIEW]:
            return False
        decision.reject(approver, reason)
        return True

    def implement_decision(self, decision_id: str) -> bool:
        """Implement a decision"""
        decision = self.get_decision(decision_id)
        if not decision:
            return False
        if decision.status != DecisionStatus.APPROVED:
            return False
        decision.implement()
        return True

    def complete_decision(self, decision_id: str) -> bool:
        """Complete a decision"""
        decision = self.get_decision(decision_id)
        if not decision:
            return False
        if decision.status != DecisionStatus.IMPLEMENTED:
            return False
        decision.complete()
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get decision statistics"""
        total = len(self.decisions)
        by_status = {}
        by_type = {}

        for decision in self.decisions.values():
            by_status[decision.status.value] = by_status.get(decision.status.value, 0) + 1
            by_type[decision.type.value] = by_type.get(decision.type.value, 0) + 1

        return {
            "total_decisions": total,
            "by_status": by_status,
            "by_type": by_type,
            "pending": len(self.get_pending_decisions()),
            "approved": len(self.get_decisions_by_status(DecisionStatus.APPROVED)),
            "implemented": len(self.get_decisions_by_status(DecisionStatus.IMPLEMENTED)),
            "completed": len(self.get_decisions_by_status(DecisionStatus.COMPLETED)),
            "rejected": len(self.get_decisions_by_status(DecisionStatus.REJECTED))
        }


# Singleton instance
decision_engine = DecisionEngine()