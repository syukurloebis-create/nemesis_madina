"""
Graph Assembler — Row → DTO.

Architecture Decision:
- Assembler converts Row Objects to DTOs
- NOT in Collector (Collector only orchestrates)
- Pure transformation, no business logic
"""

from typing import Tuple, Optional  # ← TAMBAHKAN Optional
from backend.repositories.rows.graph_rows import GraphSummaryRow
from backend.dtos.collector_dtos import GraphCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason


class GraphAssembler:
    """Graph Assembler — Row → DTO."""

    @classmethod
    def assemble(
        cls,
        row: GraphSummaryRow,
        engine_status: EngineStatus = EngineStatus.OK,
        fallback_reason: Optional[FallbackReason] = None,
        error: Optional[str] = None
    ) -> GraphCollectorDTO:
        return GraphCollectorDTO(
            entities=row.entities,
            relationships=row.relationships,
            engine_status=engine_status,
            fallback_reason=fallback_reason,
            error=error
        )

    @classmethod
    def assemble_empty(cls) -> GraphCollectorDTO:
        return GraphCollectorDTO(
            entities=0,
            relationships=0,
            engine_status=EngineStatus.OK
        )