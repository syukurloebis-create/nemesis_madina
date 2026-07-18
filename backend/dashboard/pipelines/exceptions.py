# backend/dashboard/pipelines/exceptions.py

from backend.dashboard.pipelines.constants import PipelineName


class UnknownPipelineException(Exception):
    """
    Raised when pipeline is not found in registry.
    
    Carries structured data for logging, telemetry, and metrics.
    """
    
    def __init__(
        self,
        requested: PipelineName,
        available: list[PipelineName]
    ):
        self.requested = requested
        self.available = available
        super().__init__(
            f"Pipeline '{requested.value}' not found. "
            f"Available: {[p.value for p in available]}"
        )