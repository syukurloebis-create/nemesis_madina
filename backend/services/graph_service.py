"""
Graph Service - Compatibility Wrapper

Phase B: Wrapper created
Phase C: Dual registration
Phase D: Import migration
Phase E: Legacy removal

This is a COMPATIBILITY LAYER only.
DO NOT add business logic.
DO NOT change behavior.
DO NOT modify return values.
DO NOT change exceptions.

Purpose: Enable phased migration from legacy graph/application/service
to platform backend/services/graph_service.
"""

from typing import Tuple, Optional
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.application.dto import GraphBuildRequest


class GraphRegenerationService:
    """
    Graph Regeneration Service - Compatibility Wrapper.
    
    Wraps the legacy GraphRegenerationService from backend.graph.application.service.
    All methods delegate directly to the legacy implementation.
    
    Migration Status:
    - Phase B: Wrapper created
    - Phase C: Dual registration active
    - Phase D: Imports migrated
    - Phase E: Remove wrapper and use direct implementation
    """
    
    def __init__(
        self,
        assembler,
        checksum_service,
        syntax_validator,
        semantic_validator,
        business_validator,
        policy_registry,
        write_repository,
        maintenance_repository,
        clock,
    ):
        from backend.graph.application.service import GraphRegenerationService as _GraphRegenerationService
        self._impl = _GraphRegenerationService(
            assembler=assembler,
            checksum_service=checksum_service,
            syntax_validator=syntax_validator,
            semantic_validator=semantic_validator,
            business_validator=business_validator,
            policy_registry=policy_registry,
            write_repository=write_repository,
            maintenance_repository=maintenance_repository,
            clock=clock,
        )
    
    async def regenerate_graph(self, uow, request, strategy="replace"):
        return await self._impl.regenerate_graph(uow, request, strategy)
    
    async def regenerate_by_case_id(self, uow, case_id, institution_id, strategy="replace"):
        return await self._impl.regenerate_by_case_id(uow, case_id, institution_id, strategy)
    
    # All public methods from legacy must be mirrored here
    # Add any additional methods that exist in the legacy implementation


# For backward compatibility, also expose the class at module level
__all__ = ["GraphRegenerationService"]