from typing import Awaitable, TypeVar, Generic, Optional
from datetime import timedelta
from dataclasses import dataclass

T = TypeVar("T")

@dataclass(slots=True, frozen=True)
class TaskDefinition(Generic[T]):
    name: str
    coroutine: Awaitable[T]
    timeout: timedelta = timedelta(seconds=5)
    required: bool = True

    @classmethod
    def create(
        cls,
        name: str,
        coroutine: Awaitable[T],
        timeout: float | timedelta = timedelta(seconds=5),
        required: bool = True,
    ) -> "TaskDefinition[T]":
        """Compatibility factory method. Added Sprint 3.4D."""
        if isinstance(timeout, (int, float)):
            timeout = timedelta(seconds=float(timeout))
        return cls(
            name=name,
            coroutine=coroutine,
            timeout=timeout,
            required=required,
        )