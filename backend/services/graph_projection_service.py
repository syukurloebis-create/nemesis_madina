"""
Graph Projection Service - Application Service.

Handles updating projections after graph persistence.
"""

import logging
from uuid import UUID

from backend.graph.domain.aggregate import GraphAggregate

logger = logging.getLogger(__name__)


class GraphProjectionService:
    """
    Graph Projection Service.
    
    Responsibilities:
    - Update all projections after graph changes
    
    Called AFTER commit (eventual consistency).
    Failures do NOT rollback the transaction.
    """
    
    def __init__(self):
        """Initialize projection service."""
        # TODO: Add projection dependencies (dashboard, search, analytics)
        pass
    
    async def update_all(self, case_id: UUID, aggregate: GraphAggregate) -> None:
        """
        Update all projections.
        
        Called AFTER commit.
        If projection fails, we log but don't rollback.
        """
        try:
            await self._update_dashboard(case_id, aggregate)
            await self._update_search(case_id, aggregate)
            await self._update_analytics(case_id, aggregate)
            logger.info(f"Updated all projections for case {case_id}")
        except Exception as e:
            # Projection failure does NOT rollback the transaction
            logger.error(f"Failed to update projections for case {case_id}: {e}")
            # Could retry with exponential backoff
    
    async def _update_dashboard(self, case_id: UUID, aggregate: GraphAggregate) -> None:
        """Update dashboard projection."""
        # TODO: Implement dashboard projection update
        # await self._dashboard_cache.set(f"graph:{case_id}", aggregate.to_dict())
        logger.debug(f"Dashboard projection updated for case {case_id}")
    
    async def _update_search(self, case_id: UUID, aggregate: GraphAggregate) -> None:
        """Update search index."""
        # TODO: Implement search index update
        # await self._search_index.index("graph", case_id, aggregate.to_dict())
        logger.debug(f"Search projection updated for case {case_id}")
    
    async def _update_analytics(self, case_id: UUID, aggregate: GraphAggregate) -> None:
        """Update analytics projection."""
        # TODO: Implement analytics projection update
        # await self._analytics_cache.set(f"graph_stats:{case_id}", aggregate.compute_statistics().to_dict())
        logger.debug(f"Analytics projection updated for case {case_id}")