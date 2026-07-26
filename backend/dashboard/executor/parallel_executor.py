# backend/dashboard/executor/parallel_executor.py

import asyncio
import logging
from typing import Dict, List, TypeVar, Generic, Optional
from dataclasses import dataclass
from datetime import datetime

from backend.dashboard.executor.task_definition import TaskDefinition
from backend.dashboard.events.pipeline_events import (
    EventBus,
    PipelineFinishedEvent,
    PipelineFailedEvent,
    PipelineTimeoutEvent
)

T = TypeVar("T")
logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ExecutionResult(Generic[T]):
    """Result from parallel execution - preserves Exception."""
    name: str
    result: Optional[T]
    success: bool
    exception: Optional[Exception] = None
    duration_ms: float = 0.0
    
    @property
    def error(self) -> Optional[str]:
        """Format exception as string for presentation."""
        return str(self.exception) if self.exception else None
    
    @property
    def has_error(self) -> bool:
        return self.exception is not None


class ParallelExecutor:
    """
    Pure parallel execution engine.
    
    Responsibilities:
    1. Execute tasks concurrently
    2. Individual timeouts per task (from TaskDefinition)
    3. Emit events for observability
    
    DOES NOT know about:
    - Circuit Breaker (handled by PipelinePolicy)
    - Retry (handled by PipelinePolicy)
    - Feature Flags (handled by PipelinePlanner)
    - Metrics (handled by EventBus subscribers)
    
    This is the simplest possible execution engine.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        self._event_bus = event_bus
    
    async def execute(
        self,
        tasks: List[TaskDefinition[T]],
        *,
        raise_on_required_error: bool = False,
    ) -> Dict[str, ExecutionResult[T]]:
        """Execute tasks in parallel. Pure execution only."""
        del raise_on_required_error
        results: Dict[str, ExecutionResult[T]] = {}
        
        async def run_task(task: TaskDefinition[T]) -> ExecutionResult[T]:
            start_time = datetime.now()
            try:
                result = await asyncio.wait_for(task.coroutine, timeout=task.timeout.total_seconds())
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Emit event
                if self._event_bus:
                    await self._event_bus.publish(
                        PipelineFinishedEvent(
                            name=task.name,
                            duration_ms=duration_ms,
                            success=True,
                            result=result
                        )
                    )
                
                return ExecutionResult(
                    name=task.name,
                    result=result,
                    success=True,
                    duration_ms=duration_ms
                )
            except asyncio.TimeoutError:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Emit event
                if self._event_bus:
                    await self._event_bus.publish(
                        PipelineTimeoutEvent(
                            name=task.name,
                            timeout_seconds=task.timeout.total_seconds()
                        )
                    )
                
                return ExecutionResult(
                    name=task.name,
                    result=None,
                    success=False,
                    exception=TimeoutError(f"Timeout after {task.timeout}"),
                    duration_ms=duration_ms
                )
            except Exception as e:
                duration_ms = (datetime.now() - start_time).total_seconds() * 1000
                
                # Emit event
                if self._event_bus:
                    await self._event_bus.publish(
                        PipelineFailedEvent(
                            name=task.name,
                            error=e
                        )
                    )
                
                return ExecutionResult(
                    name=task.name,
                    result=None,
                    success=False,
                    exception=e,
                    duration_ms=duration_ms
                )
        
        # Execute all tasks concurrently
        task_results = await asyncio.gather(
            *(run_task(task) for task in tasks),
            return_exceptions=True
        )
        
        # Collect results
        for result in task_results:
            if isinstance(result, ExecutionResult):
                results[result.name] = result
            elif isinstance(result, Exception):
                logger.error(f"Unexpected exception in task: {result}")
        
        return results