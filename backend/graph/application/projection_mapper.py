"""
Graph Projection Mapper - Compatibility Shim

This file exists to maintain ABI compatibility during migration.
The actual implementation is in backend.presenters.graph_presenter.

CONTRACT (from container_builder.py):
- __init__(statistics_service, clock)

No method calls have been found in the codebase.
Methods will be added if/when they are actually called.
"""


class GraphProjectionMapper:
    """
    Compatibility wrapper for GraphProjectionMapper.
    
    Constructor matches the expected contract:
    - statistics_service: Statistics service instance
    - clock: Clock instance
    """
    
    def __init__(self, statistics_service, clock):
        """
        Initialize with the same contract as expected by container_builder.
        """
        from backend.presenters.graph_presenter import GraphPresenter
        self._impl = GraphPresenter(
            statistics_service=statistics_service,
            clock=clock,
        )
    
    # No methods are currently called in the codebase.
    # If a method call is discovered (e.g., to_projection_data),
    # it will be added here.


__all__ = ["GraphProjectionMapper"]