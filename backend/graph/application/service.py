"""
Graph Application - Regeneration Service

Orchestrates graph regeneration for a case.
"""

from typing import Optional, Dict, Any
from typing import Tuple
from uuid import UUID
import logging

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.infrastructure.interfaces.clock import Clock
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.domain.checksum import GraphChecksumService
from backend.graph.domain.validators import SyntaxValidator, SemanticValidator, BusinessValidator
from backend.graph.domain.policy import PolicyRegistry
from backend.graph.application.dto import GraphBuildRequest
from backend.graph.application.assembler import GraphAssembler
from backend.graph.application.statistics import BuilderStatistics
from backend.graph.application.projection_mapper import GraphProjectionMapper
from backend.repositories.interfaces.graph_write_repository import GraphWriteRepository
from backend.repositories.interfaces.graph_maintenance_repository import GraphMaintenanceRepository

logger = logging.getLogger(__name__)


class GraphRegenerationService:
    """
    Graph Regeneration Service - Application Orchestrator.
    
    Responsibilities:
    1. Build aggregate from DTOs (via Assembler)
    2. Validate aggregate (via Validators)
    3. Apply business policies (via PolicyRegistry)
    4. Compute checksum (via ChecksumService)
    5. Persist aggregate (via Repository)
    6. Project aggregate (via ProjectionMapper)
    
    Transaction Boundary: Owns UOW.
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
        self._assembler = assembler
        self._checksum_service = checksum_service
        self._syntax_validator = syntax_validator
        self._semantic_validator = semantic_validator
        self._business_validator = business_validator
        self._policy_registry = policy_registry
        self._write_repository = write_repository
        self._maintenance_repository = maintenance_repository
        self._clock = clock
    
    async def regenerate_graph(
        self,
        uow: IUnitOfWork,
        request: GraphBuildRequest,
        strategy: str = "replace",
    ) -> Tuple[GraphAggregate, BuilderStatistics]:
        """
        Regenerate graph for a case.
        
        Atomic: ALL or NOTHING.
        If any step fails, transaction rolls back.
        
        Args:
            uow: Unit of Work (transaction boundary)
            request: GraphBuildRequest DTO
            strategy: Regeneration strategy
            
        Returns:
            Tuple of (GraphAggregate, BuilderStatistics)
        """
        # ============================================================
        # PHASE 1: BUILD (NO TRANSACTION)
        # ============================================================
        logger.info(f"Building graph for case {request.case_id}")
        aggregate, statistics = self._assembler.assemble(request)
        
        # ============================================================
        # PHASE 2: VALIDATE (NO TRANSACTION)
        # ============================================================
        logger.info(f"Validating graph for case {request.case_id}")
        self._validate_aggregate(aggregate)
        
        # ============================================================
        # PHASE 3: POLICY (NO TRANSACTION)
        # ============================================================
        logger.info(f"Applying policies for case {request.case_id}")
        self._policy_registry.validate_all(aggregate)
        
        # ============================================================
        # PHASE 4: CHECKSUM (NO TRANSACTION)
        # ============================================================

        checksum = self._checksum_service.compute_from_aggregate(aggregate)
        aggregate = aggregate.with_checksum(checksum)
                
        # ============================================================
        # PHASE 5: PERSIST (IN TRANSACTION)
        # ============================================================
        logger.info(f"Persisting graph for case {request.case_id}")
        
        if strategy == "replace":
            await self._maintenance_repository.delete_case_graph(uow, request.case_id)
        
        await self._write_repository.save_aggregate(uow, aggregate)
        
        # ============================================================
        # PHASE 6: COMMIT (UOW HANDLES)
        # ============================================================
        # UOW will commit on context exit
        logger.info(f"Graph regenerated for case {request.case_id}")
        
        return aggregate, statistics
    
    def _validate_aggregate(self, aggregate: GraphAggregate) -> None:
        """Validate aggregate across all validators."""
        for node in aggregate.nodes:
            if node.entity_type == "vendor":
                self._syntax_validator.validate_vendor(node)
            elif node.entity_type == "package":
                self._syntax_validator.validate_package(node)
            elif node.entity_type == "officer":
                self._syntax_validator.validate_officer(node)
        
        for edge in aggregate.edges:
            self._semantic_validator.validate_edge_semantic(
                edge,
                list(aggregate.nodes)
            )
        
        self._business_validator.validate_no_self_reference(aggregate)
        self._business_validator.validate_no_duplicate_business_keys(aggregate)