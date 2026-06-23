# backend/services/workflow_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional, List
from domain.value_objects import CaseState, WorkflowStatus, CaseStatus
from cases.event_store import EventStore
from services.replay_service import ReplayService
import logging

logger = logging.getLogger(__name__)


class WorkflowService:
    """
    Workflow service yang membaca status dari CANONICAL CaseState.
    BUKAN sumber kebenaran sendiri - hanya view/read model.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.event_store = EventStore(session)
        self.replay_service = ReplayService(session)
    
    async def get_workflow(self, case_id: str) -> Dict[str, Any]:
        """
        Get workflow from canonical case state.
        Status diambil dari aggregate, bukan dari projection terpisah.
        """
        # Get current state dari replay (canonical)
        state = await self.replay_service.get_state_at_version(case_id, None)
        
        if not state:
            return {
                "case_id": case_id,
                "workflow": [],
                "current_state": "unknown",
                "total_steps": 0,
                "message": "No events found for this case"
            }
        
        # Convert to canonical CaseState
        case_state = self._dict_to_case_state(case_id, state)
        
        # Generate workflow from canonical state
        workflow = self._generate_workflow_from_state(case_state)
        
        return {
            "case_id": case_id,
            "workflow": workflow,
            "current_state": WorkflowStatus.from_case_status(case_state.status),
            "current_status_display": WorkflowStatus.get_display_name(case_state.status),
            "total_steps": len(workflow),
            "is_active": case_state.status.is_active(),
            "canonical_status": case_state.status.value
        }
    
    def _dict_to_case_state(self, case_id: str, state_dict: Dict[str, Any]) -> CaseState:
        """Convert dictionary from replay to canonical CaseState"""
        return CaseState(
            case_id=case_id,
            title=state_dict.get("title", ""),
            description=state_dict.get("description", ""),
            status=CaseStatus.from_string(state_dict.get("status", "draft")),
            priority=state_dict.get("priority", "medium"),
            assigned_to=state_dict.get("assigned_to"),
            evidence_count=state_dict.get("evidence_count", 0),
            finding_count=state_dict.get("finding_count", 0),
            version=state_dict.get("version", 0)
        )
    
    def _generate_workflow_from_state(self, state: CaseState) -> List[Dict[str, Any]]:
        """Generate workflow steps from canonical state"""
        steps = []
        
        # Step 1: Case Created
        steps.append({
            "step": "case_created",
            "status": WorkflowStatus.from_case_status(CaseStatus.OPEN),
            "timestamp": state.created_at,
            "user": None,
            "completed": True
        })
        
        # Step 2: Assignment
        steps.append({
            "step": "case_assigned",
            "status": WorkflowStatus.from_case_status(CaseStatus.ASSIGNED),
            "timestamp": state.updated_at if state.assigned_to else None,
            "user": None,
            "assignee": state.assigned_to,
            "completed": state.assigned_to is not None
        })
        
        # Step 3: Investigation
        steps.append({
            "step": "investigation",
            "status": WorkflowStatus.from_case_status(CaseStatus.INVESTIGATING),
            "timestamp": state.updated_at if state.evidence_count > 0 else None,
            "evidence_count": state.evidence_count,
            "completed": state.evidence_count > 0 or state.status in [CaseStatus.VERIFYING, CaseStatus.RESOLVED, CaseStatus.CLOSED]
        })
        
        # Step 4: Verification
        steps.append({
            "step": "verification",
            "status": WorkflowStatus.from_case_status(CaseStatus.VERIFYING),
            "timestamp": None,
            "completed": state.status in [CaseStatus.RESOLVED, CaseStatus.CLOSED]
        })
        
        # Step 5: Resolution/Closure
        is_closed = state.status in [CaseStatus.CLOSED, CaseStatus.ARCHIVED]
        steps.append({
            "step": "closure",
            "status": WorkflowStatus.from_case_status(state.status),
            "timestamp": state.closed_at,
            "closed_by": getattr(state, 'closed_by', None),
            "completed": is_closed
        })
        
        return steps
    
    async def get_workflow_summary(self, case_id: str) -> Dict[str, Any]:
        """Get workflow summary with status distribution"""
        workflow = await self.get_workflow(case_id)
        
        completed_steps = sum(1 for step in workflow.get("workflow", []) if step.get("completed", False))
        total_steps = workflow.get("total_steps", 0)
        
        return {
            "case_id": case_id,
            "current_state": workflow.get("current_state"),
            "progress_percentage": (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "is_completed": workflow.get("is_active") is False,
            "canonical_status": workflow.get("canonical_status")
        }