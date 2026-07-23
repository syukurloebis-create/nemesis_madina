"""
Graph Builder Interface — Contract for all graph builders.

Pure domain interface — NO persistence, NO infrastructure.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from backend.graph.dto.graph_candidate import GraphCandidate


class IGraphBuilder(ABC):
    """
    Interface for pure graph builders.
    
    Builders transform source data into GraphCandidate.
    NO persistence, NO UUID, NO SQL.
    """
    
    @abstractmethod
    async def build(self, source_data: Dict[str, Any]) -> GraphCandidate:
        """
        Build graph from source data.
        
        Args:
            source_data: Raw source data (e.g., from rup_paket_detailed)
            
        Returns:
            Pure GraphCandidate — NO persistence details.
        """
        pass
    
    @abstractmethod
    def builder_id(self) -> str:
        """
        Return unique builder identifier.
        
        Used for registry and source data routing.
        """
        pass