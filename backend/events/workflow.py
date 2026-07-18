"""
Workflow Engine
Automated workflow management
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
import logging

logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Workflow status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class WorkflowStepStatus(str, Enum):
    """Step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    """Workflow step"""
    id: str
    name: str
    action: str
    status: WorkflowStepStatus = WorkflowStepStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "action": self.action,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "dependencies": self.dependencies
        }


@dataclass
class Workflow:
    """Workflow definition"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    steps: List[WorkflowStep] = field(default_factory=list)
    status: WorkflowStatus = WorkflowStatus.PENDING
    current_step: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status.value,
            "current_step": self.current_step,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "context": self.context,
            "created_at": self.created_at.isoformat()
        }


class WorkflowEngine:
    """
    Workflow Engine
    Execute and manage automated workflows
    """

    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.actions: Dict[str, Callable] = {}
        self.history: List[Workflow] = []

    def register_action(self, name: str, handler: Callable) -> None:
        """Register a workflow action"""
        self.actions[name] = handler
        logger.info(f"Action registered: {name}")

    def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[Dict[str, Any]]
    ) -> Workflow:
        """Create a new workflow"""
        workflow_steps = [
            WorkflowStep(
                id=f"step_{i+1}",
                name=step.get("name", f"Step {i+1}"),
                action=step.get("action", ""),
                dependencies=step.get("dependencies", [])
            )
            for i, step in enumerate(steps)
        ]

        workflow = Workflow(
            name=name,
            description=description,
            steps=workflow_steps
        )

        self.workflows[str(workflow.id)] = workflow
        logger.info(f"Workflow created: {name} ({workflow.id})")
        return workflow

    async def execute(self, workflow_id: str) -> bool:
        """Execute a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            logger.error(f"Workflow not found: {workflow_id}")
            return False

        if workflow.status in [WorkflowStatus.RUNNING, WorkflowStatus.COMPLETED]:
            return False

        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.now()

        try:
            # Process steps in order
            for i, step in enumerate(workflow.steps):
                workflow.current_step = i

                # Check dependencies
                if not self._check_dependencies(workflow, step):
                    step.status = WorkflowStepStatus.SKIPPED
                    continue

                step.status = WorkflowStepStatus.RUNNING
                step.started_at = datetime.now()

                try:
                    # Execute action
                    if step.action in self.actions:
                        result = await self.actions[step.action](step, workflow.context)
                        step.result = result
                        step.status = WorkflowStepStatus.COMPLETED
                    else:
                        step.status = WorkflowStepStatus.SKIPPED
                        logger.warning(f"Action not found: {step.action}")

                except Exception as e:
                    step.status = WorkflowStepStatus.FAILED
                    step.error = str(e)
                    workflow.status = WorkflowStatus.FAILED
                    logger.error(f"Step failed: {step.name} - {e}")
                    return False

                step.completed_at = datetime.now()

            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            self.history.append(workflow)
            logger.info(f"Workflow completed: {workflow.name} ({workflow_id})")
            return True

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            logger.error(f"Workflow failed: {workflow.name} - {e}")
            return False

    def _check_dependencies(self, workflow: Workflow, step: WorkflowStep) -> bool:
        """Check if step dependencies are met"""
        if not step.dependencies:
            return True

        dep_ids = set(step.dependencies)
        completed_ids = set()

        for s in workflow.steps:
            if s.status == WorkflowStepStatus.COMPLETED:
                completed_ids.add(s.id)

        return dep_ids.issubset(completed_ids)

    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        return self.workflows.get(workflow_id)

    def get_workflows_by_status(self, status: WorkflowStatus) -> List[Workflow]:
        """Get workflows by status"""
        return [w for w in self.workflows.values() if w.status == status]

    def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        if workflow.status not in [WorkflowStatus.PENDING, WorkflowStatus.RUNNING]:
            return False
        workflow.status = WorkflowStatus.CANCELLED
        logger.info(f"Workflow cancelled: {workflow.name} ({workflow_id})")
        return True

    def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        if workflow.status != WorkflowStatus.RUNNING:
            return False
        workflow.status = WorkflowStatus.PAUSED
        logger.info(f"Workflow paused: {workflow.name} ({workflow_id})")
        return True

    def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            return False
        if workflow.status != WorkflowStatus.PAUSED:
            return False
        workflow.status = WorkflowStatus.RUNNING
        logger.info(f"Workflow resumed: {workflow.name} ({workflow_id})")
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        total = len(self.workflows)
        by_status = {}

        for workflow in self.workflows.values():
            by_status[workflow.status.value] = by_status.get(workflow.status.value, 0) + 1

        return {
            "total_workflows": total,
            "by_status": by_status,
            "completed": len(self.history)
        }


# Singleton instance
workflow_engine = WorkflowEngine()