# backend/lifecycle/service.py
from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .models import CaseStatus, InvestigationStage, get_lifecycle
from .state_machine import CaseStateMachine, TransitionResult
from .rules import TransitionRules, RuleEngine
from .approval import ApprovalWorkflow


class LifecycleService:
    """Service untuk mengelola investigation lifecycle"""
    
    def __init__(self, db_session):
        self.db_session = db_session
        self.lifecycle = get_lifecycle()
        self.rules = TransitionRules(db_session)
        self.rule_engine = RuleEngine(self.rules)
        self.approval_workflow = ApprovalWorkflow(self.lifecycle)
        self._state_machines: Dict[uuid.UUID, CaseStateMachine] = {}
    
    def get_state_machine(self, case_id: uuid.UUID) -> CaseStateMachine:
        """Get or create state machine for a case"""
        if case_id not in self._state_machines:
            sm = CaseStateMachine(case_id)
            
            # Register condition checkers
            sm.register_condition_checker("case_complete", self.rules.check_case_complete)
            sm.register_condition_checker("screening_complete", self.rules.check_screening_complete)
            sm.register_condition_checker("evidence_minimum", self.rules.check_evidence_minimum)
            sm.register_condition_checker("risk_assessed", self.rules.check_risk_assessed)
            sm.register_condition_checker("priority_assigned", self.rules.check_priority_assigned)
            sm.register_condition_checker("evidence_sufficient", self.rules.check_evidence_sufficient)
            sm.register_condition_checker("analysis_complete", self.rules.check_analysis_complete)
            sm.register_condition_checker("finding_approved", self.rules.check_finding_approved)
            sm.register_condition_checker("recommendation_issued", self.rules.check_recommendation_issued)
            sm.register_condition_checker("followup_complete", self.rules.check_followup_complete)
            sm.register_condition_checker("recovery_recorded", self.rules.check_recovery_recorded)
            
            self._state_machines[case_id] = sm
        return self._state_machines[case_id]
    
    async def transition_case(
        self,
        case_id: uuid.UUID,
        new_status: CaseStatus,
        actor_id: uuid.UUID,
        actor_role: str,
        reason: Optional[str] = None
    ) -> TransitionResult:
        """Transition case to new status"""
        
        sm = self.get_state_machine(case_id)
        
        # TODO: Load current status from database
        # sm.set_current_status(current_status)
        
        result = await sm.transition_to(new_status, actor_id, actor_role, reason)
        
        # TODO: Save state machine state to database
        # TODO: Emit events for status change
        
        return result
    
    async def submit_approval(
        self,
        approval_id: str,
        approver_id: uuid.UUID,
        approver_role: str,
        approved: bool,
        notes: Optional[str] = None
    ) -> bool:
        """Submit approval decision"""
        
        result = self.approval_workflow.submit_approval(
            approval_id, approver_id, approver_role, approved, notes
        )
        
        if result and approved:
            # Get the approval request
            # TODO: Execute the approved transition
            pass
        
        return result
    
    def get_case_lifecycle_status(self, case_id: uuid.UUID) -> Dict[str, Any]:
        """Get complete lifecycle status for a case"""
        
        sm = self.get_state_machine(case_id)
        pending_approvals = self.approval_workflow.get_pending_approvals_for_case(case_id)
        approval_history = self.approval_workflow.get_approval_history(case_id)
        
        return {
            "case_id": str(case_id),
            "current_status": sm.get_current_status().value if sm.get_current_status() else None,
            "state_history": sm.get_state_history(),
            "pending_approvals": [a.to_dict() for a in pending_approvals],
            "approval_history": approval_history,
            "available_transitions": [
                s.value for s in self.lifecycle.get_next_statuses(sm.get_current_status())
            ] if sm.get_current_status() else []
        }
    
    def get_lifecycle_graph(self) -> Dict[str, Any]:
        """Get lifecycle graph for visualization"""
        return self.lifecycle.get_lifecycle_graph()
    
    def get_all_statuses(self) -> List[str]:
        """Get all possible case statuses"""
        return [s.value for s in CaseStatus]
    
    def get_all_stages(self) -> List[Dict[str, Any]]:
        """Get all investigation stages"""
        stages = self.lifecycle.get_all_stages()
        return [
            {
                "name": s.name.value,
                "display_name": s.display_name,
                "description": s.description,
                "required_roles": s.required_roles,
                "estimated_duration_days": s.estimated_duration_days,
                "is_mandatory": s.is_mandatory
            }
            for s in stages
        ]
    
    async def get_case_health(self, case_id: uuid.UUID) -> Dict[str, Any]:
        """Get case health metrics"""
        
        sm = self.get_state_machine(case_id)
        current_status = sm.get_current_status()
        
        # Calculate days in current status
        history = sm.get_state_history()
        days_in_status = 0
        if history and history[-1]["to_status"] == current_status.value if current_status else None:
            last_transition = datetime.fromisoformat(history[-1]["timestamp"])
            days_in_status = (datetime.utcnow() - last_transition).days
        
        # Get estimated duration for this status
        estimated_duration = 30  # Default
        for stage in self.lifecycle.get_all_stages():
            if stage.name.value == current_status.value if current_status else None:
                estimated_duration = stage.estimated_duration_days
                break
        
        # Calculate health score
        if days_in_status > estimated_duration:
            health_score = max(0, 100 - ((days_in_status - estimated_duration) / estimated_duration * 50))
        else:
            health_score = 100 - ((estimated_duration - days_in_status) / estimated_duration * 20)
        
        health_score = max(0, min(100, health_score))
        
        return {
            "case_id": str(case_id),
            "current_status": current_status.value if current_status else None,
            "days_in_status": days_in_status,
            "estimated_duration_days": estimated_duration,
            "health_score": round(health_score, 1),
            "health_status": "HEALTHY" if health_score >= 70 else "WARNING" if health_score >= 50 else "CRITICAL",
            "pending_approvals": len(self.approval_workflow.get_pending_approvals_for_case(case_id))
        }