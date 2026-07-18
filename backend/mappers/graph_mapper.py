"""
Graph Mapper — HANYA mapping, TIDAK ada perhitungan.
"""

from backend.dtos.collector_dtos import GraphCollectorDTO
from backend.domain.summary_objects import GraphSummary
from backend.domain.enums import EngineType


class GraphMapper:
    """Graph Mapper — HANYA mapping."""

    @staticmethod
    def to_summary(dto: GraphCollectorDTO) -> GraphSummary:
        """Convert DTO to GraphSummary."""
        return GraphSummary(
            entities=dto.entities,
            relationships=dto.relationships,
            engine=EngineType.GRAPH,
            engine_status=dto.engine_status
        )