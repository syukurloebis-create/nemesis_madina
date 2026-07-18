# backend/dashboard/executor/task_definition.py

from dataclasses import dataclass
from typing import Awaitable, TypeVar, Generic, Optional
from datetime import timedelta

T = TypeVar("T")


@dataclass(slots=True, frozen=True)
class TaskDefinition(Generic[T]):
    """
    Task definition for parallel execution.
    
    Uses timedelta for type-safe timeouts.
    """
    
    name: str
    coroutine: Awaitable[T]
    timeout: timedelta = timedelta(seconds=5.0)
    required: bool = True
    
    def with_timeout(self, timeout: timedelta) -> "TaskDefinition[T]":
        """Create new task definition with different timeout."""
        return TaskDefinition(
            name=self.name,
            coroutine=self.coroutine,
            timeout=timeout,
            required=self.required
        )