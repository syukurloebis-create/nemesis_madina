# backend/dashboard/executor/pipeline_policy.py

from typing import List, Optional
from datetime import timedelta

from backend.dashboard.executor.task_definition import TaskDefinition
from backend.dashboard.protocols.circuit_breaker import CircuitBreaker
from backend.dashboard.protocols.metrics import MetricsRecorder
from backend.dashboard.events.pipeline_events import EventBus, PipelineStartedEvent


class PipelinePolicy:
    """
    Pipeline execution policy layer.
    
    Applies resilience policies before execution:
    1. Circuit Breaker
    2. Timeout (already in TaskDefinition)
    3. Retry (future)
    4. Rate Limiter (future)
    5. Bulkhead (future)
    
    This follows patterns like Polly (.NET) or resilience4j (Java).
    """
    
    def __init__(
        self,
        circuit_breaker: Optional[CircuitBreaker] = None,
        metrics: Optional[MetricsRecorder] = None,
        event_bus: Optional[EventBus] = None,
        default_timeout: timedelta = timedelta(seconds=5.0)
    ):
        self._circuit_breaker = circuit_breaker
        self._metrics = metrics
        self._event_bus = event_bus
        self._default_timeout = default_timeout
    
    async def apply(
        self,
        tasks: List[TaskDefinition]
    ) -> List[TaskDefinition]:
        """
        Apply policies to tasks.
        
        Returns filtered tasks based on policies.
        """
        # 1. Circuit Breaker check
        if self._circuit_breaker and not self._circuit_breaker.is_available():
            return []  # No tasks can be executed
        
        # 2. Apply timeouts (already in tasks, ensure they have defaults)
        for task in tasks:
            if task.timeout is None:
                task = task.with_timeout(self._default_timeout)
        
        # 3. Record start events
        if self._event_bus:
            for task in tasks:
                await self._event_bus.publish(
                    PipelineStartedEvent(name=task.name)
                )
        
        # 4. Future: Retry, Rate Limiter, Bulkhead
        
        return tasks