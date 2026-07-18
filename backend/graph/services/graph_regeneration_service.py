"""
Graph Regeneration Service - Application Service.

Orchestrates graph regeneration for a case.
All operations are atomic within a single UnitOfWork.
"""

from typing import Dict, Any
from uuid import UUID
import logging

from backend.infrastructure.unit_of_work import UnitOfWorkFactory
from backend.repositories.interfaces.graph_command_repository import GraphCommandRepository
from backend.graph.services.graph_builder import GraphBuilder
from backend.graph.validators.graph_invariant_validator import GraphInvariantValidator

logger = logging.getLogger(__name__)


class GraphRegenerationResult:
    """Result of graph regeneration operation."""
    
    def __init__(
        self,
        case_id: UUID,
        entities_created: int,
        relationships_created: int,
        success: bool,
        error: str = None,
    ):
        self.case_id = case_id
        self.entities_created = entities_created
        self.relationships_created = relationships_created
        self.success = success
        self.error = error


class GraphRegenerationService:
    """
    Graph Regeneration Service.
    
    Orchestrates:
    1. Delete existing graph data
    2. Build entities from source
    3. Validate entities
    4. Save entities
    5. Build relationships from source
    6. Validate relationships
    7. Save relationships
    
    All operations are atomic within a single UnitOfWork.
    If any step fails, the entire transaction rolls back.
    """
    
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        command_repo: GraphCommandRepository,
        builder: GraphBuilder,
        validator: GraphInvariantValidator,
    ):
        self._uow_factory = uow_factory
        self._command_repo = command_repo
        self._builder = builder
        self._validator = validator
    
    async def regenerate_graph(
        self,
        case_id: UUID,
        institution_id: UUID,
        source_data: Dict[str, Any],
    ) -> GraphRegenerationResult:
        """
        Regenerate graph data for a case.
        
        Atomic: ALL or NOTHING.
        If any step fails, the entire transaction rolls back.
        
        Args:
            case_id: Case UUID
            institution_id: Institution UUID
            source_data: Source data (RUP, packages, vendors)
            
        Returns:
            GraphRegenerationResult with statistics
            
        Raises:
            ValueError: If source_data is invalid
            RepositoryError: If database operation fails
        """
        try:
            async with self._uow_factory.create() as uow:
                # 1. Delete existing graph data
                await self._command_repo.delete_case_graph(uow, case_id)
                
                # 2. Build entities from source
                entities = self._builder.build_entities_from_source(
                    case_id=case_id,
                    institution_id=institution_id,
                    source_data=source_data,
                )
                
                # 3. Validate entities
                self._validator.validate_entities(entities)
                
                # 4. Save entities (batch)
                saved_entities = await self._command_repo.save_entities(uow, entities)
                
                # 5. Build relationships from source
                relationships = self._builder.build_relationships_from_source(
                    case_id=case_id,
                    institution_id=institution_id,
                    source_data=source_data,
                    entities=saved_entities,
                )
                
                # 6. Validate relationships
                self._validator.validate_relationships(relationships, saved_entities)
                self._validator.validate_no_duplicate_edges(relationships)
                
                # 7. Save relationships (batch)
                saved_relationships = await self._command_repo.save_relationships(
                    uow, relationships
                )
                
                # 8. Commit - managed by UOW
                await uow.commit()
                
                logger.info(
                    f"Regenerated graph for case {case_id}: "
                    f"{len(saved_entities)} entities, {len(saved_relationships)} relationships"
                )
                
                return GraphRegenerationResult(
                    case_id=case_id,
                    entities_created=len(saved_entities),
                    relationships_created=len(saved_relationships),
                    success=True,
                )
                
        except Exception as e:
            logger.error(f"Failed to regenerate graph for case {case_id}: {e}")
            return GraphRegenerationResult(
                case_id=case_id,
                entities_created=0,
                relationships_created=0,
                success=False,
                error=str(e),
            )