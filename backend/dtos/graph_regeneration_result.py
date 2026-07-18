"""
Graph Regeneration Result - DTO

Result of graph regeneration operation.
"""

from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID


@dataclass(frozen=True)
class GraphRegenerationResult:
    """Result of graph regeneration operation."""
    
    case_id: UUID
    nodes_created: int
    edges_created: int
    success: bool
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    version: Optional[int] = None
    checksum: Optional[str] = None
    
    @classmethod
    def success_result(
        cls,
        case_id: UUID,
        nodes_created: int,
        edges_created: int,
        duration_ms: float,
        version: Optional[int] = None,
        checksum: Optional[str] = None,
    ) -> 'GraphRegenerationResult':
        return cls(
            case_id=case_id,
            nodes_created=nodes_created,
            edges_created=edges_created,
            success=True,
            duration_ms=duration_ms,
            version=version,
            checksum=checksum,
        )
    
    @classmethod
    def failure_result(
        cls,
        case_id: UUID,
        error: str,
        duration_ms: Optional[float] = None,
    ) -> 'GraphRegenerationResult':
        return cls(
            case_id=case_id,
            nodes_created=0,
            edges_created=0,
            success=False,
            error=error,
            duration_ms=duration_ms,
        )
    
    def to_dict(self) -> dict:
        return {
            "case_id": str(self.case_id),
            "nodes_created": self.nodes_created,
            "edges_created": self.edges_created,
            "success": self.success,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "version": self.version,
            "checksum": self.checksum,
        }