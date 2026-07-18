"""
Graph Persistence Result - Immutable DTO

DTO for persistence operation results.
Repository returns this instead of ORM models.
"""

from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from backend.graph.domain.aggregate import GraphAggregate

@dataclass(frozen=True)
class GraphPersistenceResult:
    """
    Graph Persistence Result - Immutable DTO.
    
    Represents the result of a persistence operation.
    
    Attributes:
        case_id: Case UUID
        nodes_saved: Number of nodes persisted
        edges_saved: Number of edges persisted
        version: Aggregate version
        checksum: Aggregate checksum
        duration_ms: Duration in milliseconds
        success: True if successful, False otherwise
        error: Error message (if failed)
    """
    
    case_id: UUID
    nodes_saved: int
    edges_saved: int
    version: int
    checksum: str
    duration_ms: float
    success: bool = True
    error: Optional[str] = None
    
    @classmethod
    def from_aggregate(
        cls,
        aggregate: GraphAggregate,
        duration_ms: float,
    ) -> 'GraphPersistenceResult':
        """Create result from aggregate."""
        return cls(
            case_id=aggregate.case_id,
            nodes_saved=aggregate.node_count,
            edges_saved=aggregate.edge_count,
            version=aggregate.version,
            checksum=aggregate.checksum,
            duration_ms=duration_ms,
            success=True,
        )
    
    @classmethod
    def failure(
        cls,
        case_id: UUID,
        error: str,
        duration_ms: float,
    ) -> 'GraphPersistenceResult':
        """Create failure result."""
        return cls(
            case_id=case_id,
            nodes_saved=0,
            edges_saved=0,
            version=0,
            checksum="",
            duration_ms=duration_ms,
            success=False,
            error=error,
        )
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "case_id": str(self.case_id),
            "nodes_saved": self.nodes_saved,
            "edges_saved": self.edges_saved,
            "version": self.version,
            "checksum": self.checksum,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "error": self.error,
        }