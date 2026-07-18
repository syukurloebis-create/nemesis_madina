# backend/dashboard/pipelines/base.py

from typing import Protocol, TypeVar, runtime_checkable
from backend.dashboard.protocols.pipeline_context import PipelineContext

T = TypeVar("T", covariant=True)
R = TypeVar("R", covariant=True)


@runtime_checkable
class Pipeline(Protocol[T, R]):
    """
    Pipeline Protocol - execute only.
    
    Registry holds name and metadata separately.
    Pipeline is pure execution object.
    """
    async def execute(self, context: PipelineContext) -> R:
        """Execute pipeline and return result."""
        ...

