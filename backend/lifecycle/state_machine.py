from typing import Optional, Dict, Any, List
from datetime import datetime
import uuid

from .models import CaseStatus, can_transition, get_required_conditions, get_status_display_name


class TransitionResult:
    """Result of state transition"""
    
    def __init__(self, success: bool, message: str, new_status: Optional[CaseStatus] = None):
        self.success = success
        self.message = message
        self.new_status = new_status
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "message": self.message,
            "new_status": self.new_status.value if self.new_status else None
        }


class CaseStateMachine:
    """State machine untuk case investigation lifecycle"""
    
    def __init__(self, case_id: uuid.UUID, current_status: CaseStatus = CaseStatus.REPORTED):
        self.case_id = case_id
        self._current_status = current_status
        self._history: List[Dict[str, Any]] = []
        self._conditions_checker = None
    
    def set_conditions_checker(self, checker):
        """Set condition checker function"""
        self._conditions_checker = checker
    
    async def transition_to(
        self, 
        new_status: CaseStatus, 
        actor_id: uuid.UUID, 
        actor_name: str,
        reason: Optional[str] = None
    ) -> TransitionResult:
        """Transition to new status"""
        
        # Check if transition is valid
        if not can_transition(self._current_status, new_status):
            return TransitionResult(
                False,
                f"Invalid transition from {get_status_display_name(self._current_status)} to {get_status_display_name(new_status)}"
            )
        
        # Check required conditions
        required_conditions = get_required_conditions(self._current_status, new_status)
        if required_conditions and self._conditions_checker:
            conditions_met = await self._conditions_checker(str(self.case_id), required_conditions)
            if not conditions_met:
                return TransitionResult(
                    False,
                    f"Required conditions not met: {', '.join(required_conditions)}"
                )
        
        # Record history
        self._history.append({
            "case_id": str(self.case_id),
            "from_status": self._current_status.value,
            "to_status": new_status.value,
            "actor_id": str(actor_id),
            "actor_name": actor_name,
            "timestamp": datetime.utcnow().isoformat(),
            "reason": reason
        })
        
        old_status = self._current_status
        self._current_status = new_status
        
        return TransitionResult(
            True,
            f"Case transitioned from {get_status_display_name(old_status)} to {get_status_display_name(new_status)}",
            new_status
        )
    
    def get_current_status(self) -> CaseStatus:
        return self._current_status
    
    def get_current_status_display(self) -> str:
        return get_status_display_name(self._current_status)
    
    def get_history(self) -> List[Dict[str, Any]]:
        return self._history
    
    def get_available_transitions(self) -> List[Dict[str, Any]]:
        """Get available transitions with display names"""
        transitions = TRANSITIONS.get(self._current_status, [])
        return [
            {
                "value": t.value,
                "label": get_status_display_name(t),
                "required_conditions": get_required_conditions(self._current_status, t)
            }
            for t in transitions
        ]
    
    def can_transition_to(self, status: CaseStatus) -> bool:
        return can_transition(self._current_status, status)
    
    def get_lifecycle_progress(self) -> float:
        """Get progress percentage based on current status"""
        status_order = [
            CaseStatus.REPORTED,
            CaseStatus.SCREENING,
            CaseStatus.ASSESSMENT,
            CaseStatus.INVESTIGATION,
            CaseStatus.FINDING,
            CaseStatus.RECOMMENDATION,
            CaseStatus.FOLLOW_UP,
            CaseStatus.CLOSED
        ]
        
        if self._current_status in status_order:
            idx = status_order.index(self._current_status)
            return (idx / (len(status_order) - 1)) * 100
        return 0
