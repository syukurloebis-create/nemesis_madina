# backend/graph/application/statistics.py

from dataclasses import dataclass, field
from typing import Tuple, Dict, Any


class BuilderStatistics:
    @classmethod
    def empty(cls) -> 'BuilderStatistics':
        ...
    
    def to_dict(self) -> Dict[str, Any]:
        ...

class BuilderStatisticsBuilder:
    def __init__(self):
        ...
    
    def add_warning(self, warning: str) -> None:
        ...
    
    def build(self) -> BuilderStatistics:
        ...

@dataclass(frozen=True)
class BuilderStatistics:
    """Immutable Builder Statistics - Application DTO."""
    
    total_nodes: int
    total_edges: int
    duplicates_removed: int
    invalid_edges_skipped: int
    normalized_nodes: int
    collapsed_nodes: int
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    
    @classmethod
    def empty(cls) -> 'BuilderStatistics':
        return cls(
            total_nodes=0,
            total_edges=0,
            duplicates_removed=0,
            invalid_edges_skipped=0,
            normalized_nodes=0,
            collapsed_nodes=0,
        )
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_nodes": self.total_nodes,
            "total_edges": self.total_edges,
            "duplicates_removed": self.duplicates_removed,
            "invalid_edges_skipped": self.invalid_edges_skipped,
            "normalized_nodes": self.normalized_nodes,
            "collapsed_nodes": self.collapsed_nodes,
            "warnings": list(self.warnings),
        }


class BuilderStatisticsBuilder:
    """Mutable builder for collecting statistics."""
    
    def __init__(self):
        self.total_nodes = 0
        self.total_edges = 0
        self.duplicates_removed = 0
        self.invalid_edges_skipped = 0
        self.normalized_nodes = 0
        self.collapsed_nodes = 0
        self._warnings: List[str] = []
    
    def add_warning(self, warning: str) -> None:
        self._warnings.append(warning)
    
    def build(self) -> BuilderStatistics:
        return BuilderStatistics(
            total_nodes=self.total_nodes,
            total_edges=self.total_edges,
            duplicates_removed=self.duplicates_removed,
            invalid_edges_skipped=self.invalid_edges_skipped,
            normalized_nodes=self.normalized_nodes,
            collapsed_nodes=self.collapsed_nodes,
            warnings=tuple(self._warnings),
        )