"""
Graph Presenter - Compatibility Wrapper

Phase B: Wrapper created
Phase C: Dual registration
Phase D: Import migration
Phase E: Legacy removal

This is a COMPATIBILITY LAYER only.
DO NOT add business logic.
DO NOT change behavior.
DO NOT modify return values.
DO NOT change exceptions.

Purpose: Enable phased migration from legacy graph/application/projection_mapper
to platform backend/presenters/graph_presenter.
"""

from typing import Dict, Any
from uuid import UUID

from backend.graph.domain.aggregate import GraphAggregate


class GraphPresenter:
    """
    Graph Presenter - Compatibility Wrapper.
    
    Wraps the legacy GraphProjectionMapper from backend.graph.application.projection_mapper.
    All methods delegate directly to the legacy implementation.
    
    Migration Status:
    - Phase B: Wrapper created
    - Phase C: Dual registration active
    - Phase D: Imports migrated
    - Phase E: Remove wrapper and use direct implementation
    """
    
    def __init__(self):
        """Initialize with legacy implementation."""
        from backend.graph.application.projection_mapper import GraphProjectionMapper as _GraphProjectionMapper
        self._impl = _GraphProjectionMapper()
    
    def to_projection_data(self, aggregate: GraphAggregate) -> Dict[str, Any]:
        """
        Convert aggregate to projection data.
        
        Delegates directly to legacy implementation.
        No behavior changes.
        
        Args:
            aggregate: GraphAggregate (Domain)
            
        Returns:
            Projection data dictionary
        """
        return self._impl.to_projection_data(aggregate)
    
    def to_api_response(self, aggregate: GraphAggregate) -> Dict[str, Any]:
        """
        Convert aggregate to API response.
        
        Delegates directly to legacy implementation.
        No behavior changes.
        """
        return self._impl.to_api_response(aggregate)
    
    # All public methods from legacy must be mirrored here
    # Add any additional methods that exist in the legacy implementation


# For backward compatibility
__all__ = ["GraphPresenter"]