# backend/dashboard/orchestrators/pipeline_planner.py

from typing import List, Optional
from dataclasses import dataclass
from datetime import timedelta

from backend.dashboard.pipelines.registry import PipelineRegistry, PipelineName
from backend.dashboard.protocols.pipeline_context import PipelineContext
from backend.dashboard.protocols.feature_flags import FeatureFlagProvider
from backend.dashboard.executor.task_definition import TaskDefinition


@dataclass(slots=True, frozen=True)
class ExecutionPlan:
    """Immutable execution plan."""
    tasks: List[TaskDefinition]
    sections: List[PipelineName]
    
    @property
    def is_empty(self) -> bool:
        return len(self.tasks) == 0


class PipelinePlanner:
    """
    Pipeline planning layer.
    
    Responsibilities:
    1. Select pipelines based on sections
    2. Filter by feature flags
    3. Build TaskDefinitions with correct timeouts
    4. Return ExecutionPlan
    
    This is pure planning - NO execution.
    """
    
    def __init__(
        self,
        registry: PipelineRegistry,
        feature_flags: FeatureFlagProvider,
        default_timeout: timedelta = timedelta(seconds=5.0)
    ):
        self._registry = registry
        self._feature_flags = feature_flags
        self._default_timeout = default_timeout
    
    async def plan(
        self,
        context: PipelineContext,
        sections: Optional[List[PipelineName]] = None
    ) -> ExecutionPlan:
        """Plan execution for given sections."""
        # 1. Select pipelines
        selected = self._select_pipelines(sections)
        
        if not selected:
            return ExecutionPlan(tasks=[], sections=[])
        
        # 2. Build tasks
        tasks = self._build_tasks(context, selected)
        
        return ExecutionPlan(tasks=tasks, sections=selected)
    
    def _select_pipelines(self, sections: Optional[List[PipelineName]]) -> List[PipelineName]:
        """Select pipelines based on feature flags."""
        if sections is None:
            sections = list(self._registry.get_default())
        
        return [
            name for name in sections
            if self._feature_flags.is_enabled(f"dashboard_{name.value}_enabled", default=True)
        ]
    
    def _build_tasks(
        self,
        context: PipelineContext,
        pipeline_names: List[PipelineName]
    ) -> List[TaskDefinition]:
        """Build TaskDefinitions with correct timeouts."""
        tasks = []
        for name in pipeline_names:
            pipeline = self._registry.get(name)
            descriptor = self._registry.get_descriptor(name)
            timeout = descriptor.timeout if descriptor else self._default_timeout
            required = descriptor.required if descriptor else True
            
            tasks.append(TaskDefinition(
                name=name.value,
                coroutine=pipeline.execute(context),
                timeout=timeout,
                required=required
            ))
        return tasks