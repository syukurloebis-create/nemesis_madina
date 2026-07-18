# backend/dashboard/pipelines/constants.py

from enum import StrEnum


class PipelineName(StrEnum):
    """Pipeline names for registration and identification."""
    RISK = "risk"
    FRAUD = "fraud"
    GRAPH = "graph"
    EVIDENCE = "evidence"
    PROCUREMENT = "procurement"


DEFAULT_PIPELINES: tuple[PipelineName, ...] = (
    PipelineName.RISK,
    PipelineName.FRAUD,
    PipelineName.GRAPH,
    PipelineName.EVIDENCE,
    PipelineName.PROCUREMENT,
)