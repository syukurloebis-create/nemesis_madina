# backend/lifecycle/approval.py
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ESCALATED = "ESCALATED"


class ApprovalRequest:
    """Request for approval"""
    
    def __init__(
        self,
        approval_id: str,
        case_id: uuid.UUID,
        approval_type: str,
        requested_by: uuid.UUID,
        requested_at: datetime,
        due_date: Optional[datetime] = None
    ):
        self.approval_id = approval_id
        self.case_id = case_id
        self.approval_type = approval_type
        self.requested_by = requested_by
        self.requested_at = requested_at
        self.due_date = due_date or (requested_at + timedelta(days=7))
        self.status = ApprovalStatus.PENDING
        self.approvals: List[Dict[str, Any]] = []
        self.rejection_reason: Optional[str] = None
    
    def add_approval(self, approver_id: uuid.UUID, approver_role: str, notes: Optional[str] = None):
        """Add approval from an approver"""
        self.approvals.append({
            "approver_id": str(approver_id),
            "approver_role": approver_role,
            "approved_at": datetime.utcnow().isoformat(),
            "notes": notes
        })
    
    def is_fully_approved(self, required_approvers: List[str], min_approvals: int) -> bool:
        """Check if fully approved"""
        unique_approvers = {a["approver_id"] for a in self.approvals}
        return len(unique_approvers) >= min_approvals
    
    def is_expired(self) -> bool:
        """Check if approval request has expired"""
        return datetime.utcnow() > self.due_date
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "case_id": str(self.case_id),
            "approval_type": self.approval_type,
            "requested_by": str(self.requested_by),
            "requested_at": self.requested_at.isoformat(),
            "due_date": self.due_date.isoformat(),
            "status": self.status.value,
            "approvals": self.approvals,
            "rejection_reason": self.rejection_reason
        }


class ApprovalWorkflow:
    """Workflow for managing approvals"""
    
    def __init__(self, lifecycle):
        self.lifecycle = lifecycle
        self._active_approvals: Dict[str, ApprovalRequest] = {}
        self._approval_history: List[ApprovalRequest] = []
    
    def create_approval(
        self,
        case_id: uuid.UUID,
        approval_type: str,
        requested_by: uuid.UUID,
        due_date: Optional[datetime] = None
    ) -> ApprovalRequest:
        """Create a new approval request"""
        
        approval_id = f"{approval_type}_{case_id}_{datetime.utcnow().timestamp()}"
        
        request = ApprovalRequest(
            approval_id=approval_id,
            case_id=case_id,
            approval_type=approval_type,
            requested_by=requested_by,
            requested_at=datetime.utcnow(),
            due_date=due_date
        )
        
        self._active_approvals[approval_id] = request
        return request
    
    def get_approval(self, approval_id: str) -> Optional[ApprovalRequest]:
        """Get approval request by ID"""
        return self._active_approvals.get(approval_id)
    
    def submit_approval(
        self,
        approval_id: str,
        approver_id: uuid.UUID,
        approver_role: str,
        approved: bool,
        notes: Optional[str] = None
    ) -> bool:
        """Submit an approval decision"""
        
        request = self._active_approvals.get(approval_id)
        if not request:
            return False
        
        if request.status != ApprovalStatus.PENDING:
            return False
        
        if approved:
            request.add_approval(approver_id, approver_role, notes)
            
            # Get approval definition
            approval_def = self.lifecycle.get_approval(request.approval_type)
            if approval_def:
                if request.is_fully_approved(approval_def.required_approvers, approval_def.min_approvals):
                    request.status = ApprovalStatus.APPROVED
        else:
            request.status = ApprovalStatus.REJECTED
            request.rejection_reason = notes
        
        # Check for expiration
        if request.is_expired():
            request.status = ApprovalStatus.EXPIRED
            
            # Check if escalation needed
            approval_def = self.lifecycle.get_approval(request.approval_type)
            if approval_def and approval_def.escalation_days:
                if (datetime.utcnow() - request.requested_at).days > approval_def.escalation_days:
                    request.status = ApprovalStatus.ESCALATED
        
        # Move to history if completed
        if request.status in [ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED, ApprovalStatus.ESCALATED]:
            self._active_approvals.pop(approval_id)
            self._approval_history.append(request)
        
        return True
    
    def get_pending_approvals_for_role(self, role: str) -> List[ApprovalRequest]:
        """Get pending approvals for a specific role"""
        pending = []
        for request in self._active_approvals.values():
            approval_def = self.lifecycle.get_approval(request.approval_type)
            if approval_def and role in approval_def.required_approvers:
                pending.append(request)
        return pending
    
    def get_pending_approvals_for_case(self, case_id: uuid.UUID) -> List[ApprovalRequest]:
        """Get pending approvals for a specific case"""
        return [
            request for request in self._active_approvals.values()
            if request.case_id == case_id
        ]
    
    def get_approval_history(self, case_id: uuid.UUID) -> List[Dict[str, Any]]:
        """Get approval history for a case"""
        return [
            request.to_dict() for request in self._approval_history
            if request.case_id == case_id
        ]
    
    def check_escalations(self) -> List[Dict[str, Any]]:
        """Check for approvals that need escalation"""
        escalated = []
        for request in self._active_approvals.values():
            if request.is_expired():
                request.status = ApprovalStatus.EXPIRED
                escalated.append(request.to_dict())
        return escalated