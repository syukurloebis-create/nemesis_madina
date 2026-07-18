"""
Graph Command Repository Implementation - SQLAlchemy ORM.

Single source of truth for graph persistence operations.
Repository ONLY handles persistence - no business logic.
"""

from typing import List, Optional
from uuid import UUID
import logging

from sqlalchemy import select, delete, and_

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.models import GraphEntity, GraphRelationship
from backend.repositories.interfaces.graph_command_repository import GraphCommandRepository
from backend.infrastructure.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class GraphCommandRepositoryImpl(GraphCommandRepository):
    """
    Graph Command Repository Implementation - SQLAlchemy ORM.
    
    Responsibilities:
    - Persist GraphEntity and GraphRelationship
    - Batch operations for performance
    - Enforce data invariants at persistence level
    
    Does NOT:
    - Orchestrate business logic
    - Build graphs from source data
    - Decide what to persist
    
    All operations are atomic within the UnitOfWork transaction.
    Repository MUST NOT call commit() - only UOW handles commit.
    """
    
    def __init__(self):
        """Initialize repository without dependencies."""
        pass
    
    async def save_entity(
        self,
        uow: IUnitOfWork,
        entity: GraphEntity,
    ) -> GraphEntity:
        """
        Save or update a single graph entity.
        
        Args:
            uow: Unit of Work (provides transaction context)
            entity: GraphEntity to save
            
        Returns:
            Saved GraphEntity with updated fields
            
        Raises:
            ValueError: If entity violates invariants
            RepositoryError: If database operation fails
        """
        # Basic invariant enforcement
        if entity.case_id is None:
            raise ValueError("GraphEntity MUST have case_id")
        if entity.institution_id is None:
            raise ValueError("GraphEntity MUST have institution_id")
        if not entity.entity_type:
            raise ValueError("GraphEntity MUST have entity_type")
        if not entity.name:
            raise ValueError("GraphEntity MUST have name")
        
        try:
            # Check if entity already exists (by id)
            if entity.id:
                stmt = select(GraphEntity).where(GraphEntity.id == entity.id)
                result = await uow.session.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    # Update existing entity
                    existing.entity_type = entity.entity_type
                    existing.name = entity.name
                    existing.external_id = entity.external_id
                    existing.tax_id = entity.tax_id
                    existing.address = entity.address
                    existing.attributes = entity.attributes
                    existing.extra_data = entity.extra_data
                    existing.risk_score = entity.risk_score
                    existing.confidence = entity.confidence
                    existing.last_seen = entity.last_seen
                    existing.updated_at = entity.updated_at
                    existing.created_by = entity.created_by
                    await uow.flush()
                    await uow.refresh(existing)
                    logger.debug(f"Updated GraphEntity: {existing.id} for case {existing.case_id}")
                    return existing
                else:
                    # New entity with provided id - add it
                    uow.session.add(entity)
                    await uow.flush()
                    await uow.refresh(entity)
                    logger.debug(f"Saved GraphEntity: {entity.id} for case {entity.case_id}")
                    return entity
            else:
                # New entity - let DB generate id
                uow.session.add(entity)
                await uow.flush()
                await uow.refresh(entity)
                logger.debug(f"Saved GraphEntity: {entity.id} for case {entity.case_id}")
                return entity
                
        except ValueError as e:
            # Re-raise ValueError (invariant violation)
            raise e
        except Exception as e:
            logger.error(f"Failed to save GraphEntity: {e}")
            raise RepositoryError(
                operation="save_entity",
                repository="GraphCommandRepository",
                case_id=str(entity.case_id) if entity.case_id else None,
                original_error=e,
            ) from e
    
    async def save_entities(
        self,
        uow: IUnitOfWork,
        entities: List[GraphEntity],
    ) -> List[GraphEntity]:
        """
        Save or update multiple graph entities (batch).
        
        Args:
            uow: Unit of Work (provides transaction context)
            entities: List of GraphEntity to save
            
        Returns:
            List of saved GraphEntity with updated fields
            
        Raises:
            ValueError: If any entity violates invariants
            RepositoryError: If database operation fails
        """
        if not entities:
            return []
        
        # Validate all entities first
        for entity in entities:
            if entity.case_id is None:
                raise ValueError("GraphEntity MUST have case_id")
            if entity.institution_id is None:
                raise ValueError("GraphEntity MUST have institution_id")
            if not entity.entity_type:
                raise ValueError("GraphEntity MUST have entity_type")
            if not entity.name:
                raise ValueError("GraphEntity MUST have name")
        
        try:
            # For batch operations, we need to handle upsert logic
            # Simple approach: add all and let session handle
            for entity in entities:
                if entity.id:
                    # Check if exists
                    stmt = select(GraphEntity).where(GraphEntity.id == entity.id)
                    result = await uow.session.execute(stmt)
                    existing = result.scalar_one_or_none()
                    if existing:
                        # Update existing
                        existing.entity_type = entity.entity_type
                        existing.name = entity.name
                        existing.external_id = entity.external_id
                        existing.tax_id = entity.tax_id
                        existing.address = entity.address
                        existing.attributes = entity.attributes
                        existing.extra_data = entity.extra_data
                        existing.risk_score = entity.risk_score
                        existing.confidence = entity.confidence
                        existing.last_seen = entity.last_seen
                        existing.updated_at = entity.updated_at
                        existing.created_by = entity.created_by
                        continue
                uow.session.add(entity)
            
            await uow.flush()
            
            # Refresh all entities
            saved_entities = []
            for entity in entities:
                await uow.refresh(entity)
                saved_entities.append(entity)
            
            logger.debug(f"Saved {len(saved_entities)} GraphEntities for case {saved_entities[0].case_id if saved_entities else 'unknown'}")
            return saved_entities
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to save GraphEntities: {e}")
            raise RepositoryError(
                operation="save_entities",
                repository="GraphCommandRepository",
                original_error=e,
            ) from e
    
    async def save_relationship(
        self,
        uow: IUnitOfWork,
        relationship: GraphRelationship,
    ) -> GraphRelationship:
        """
        Save or update a single graph relationship.
        
        Args:
            uow: Unit of Work (provides transaction context)
            relationship: GraphRelationship to save
            
        Returns:
            Saved GraphRelationship with updated fields
            
        Raises:
            ValueError: If relationship violates invariants
            RepositoryError: If database operation fails
        """
        # Basic invariant enforcement
        if relationship.case_id is None:
            raise ValueError("GraphRelationship MUST have case_id")
        if relationship.institution_id is None:
            raise ValueError("GraphRelationship MUST have institution_id")
        if not relationship.source_id:
            raise ValueError("GraphRelationship MUST have source_id")
        if not relationship.target_id:
            raise ValueError("GraphRelationship MUST have target_id")
        if not relationship.relationship_type:
            raise ValueError("GraphRelationship MUST have relationship_type")
        if relationship.source_id == relationship.target_id:
            raise ValueError("Self-loop is prohibited")
        
        try:
            # Check if relationship already exists (by id)
            if relationship.id:
                stmt = select(GraphRelationship).where(GraphRelationship.id == relationship.id)
                result = await uow.session.execute(stmt)
                existing = result.scalar_one_or_none()
                if existing:
                    # Update existing relationship
                    existing.source_id = relationship.source_id
                    existing.target_id = relationship.target_id
                    existing.relationship_type = relationship.relationship_type
                    existing.weight = relationship.weight
                    existing.amount = relationship.amount
                    existing.date = relationship.date
                    existing.description = relationship.description
                    existing.extra_data = relationship.extra_data
                    existing.updated_at = relationship.updated_at
                    existing.created_by = relationship.created_by
                    await uow.flush()
                    await uow.refresh(existing)
                    logger.debug(f"Updated GraphRelationship: {existing.id} for case {existing.case_id}")
                    return existing
                else:
                    # New relationship with provided id
                    uow.session.add(relationship)
                    await uow.flush()
                    await uow.refresh(relationship)
                    logger.debug(f"Saved GraphRelationship: {relationship.id} for case {relationship.case_id}")
                    return relationship
            else:
                # New relationship - let DB generate id
                uow.session.add(relationship)
                await uow.flush()
                await uow.refresh(relationship)
                logger.debug(f"Saved GraphRelationship: {relationship.id} for case {relationship.case_id}")
                return relationship
                
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to save GraphRelationship: {e}")
            raise RepositoryError(
                operation="save_relationship",
                repository="GraphCommandRepository",
                case_id=str(relationship.case_id) if relationship.case_id else None,
                original_error=e,
            ) from e
    
    async def save_relationships(
        self,
        uow: IUnitOfWork,
        relationships: List[GraphRelationship],
    ) -> List[GraphRelationship]:
        """
        Save or update multiple graph relationships (batch).
        
        Args:
            uow: Unit of Work (provides transaction context)
            relationships: List of GraphRelationship to save
            
        Returns:
            List of saved GraphRelationship with updated fields
            
        Raises:
            ValueError: If any relationship violates invariants
            RepositoryError: If database operation fails
        """
        if not relationships:
            return []
        
        # Validate all relationships first
        for rel in relationships:
            if rel.case_id is None:
                raise ValueError("GraphRelationship MUST have case_id")
            if rel.institution_id is None:
                raise ValueError("GraphRelationship MUST have institution_id")
            if not rel.source_id:
                raise ValueError("GraphRelationship MUST have source_id")
            if not rel.target_id:
                raise ValueError("GraphRelationship MUST have target_id")
            if not rel.relationship_type:
                raise ValueError("GraphRelationship MUST have relationship_type")
            if rel.source_id == rel.target_id:
                raise ValueError("Self-loop is prohibited")
        
        try:
            # Check for duplicate edges
            seen = set()
            for rel in relationships:
                key = (rel.source_id, rel.target_id, rel.relationship_type)
                if key in seen:
                    raise ValueError(f"Duplicate edge: {rel.source_id} -> {rel.target_id} ({rel.relationship_type})")
                seen.add(key)
            
            # Add all relationships
            for rel in relationships:
                if rel.id:
                    # Check if exists
                    stmt = select(GraphRelationship).where(GraphRelationship.id == rel.id)
                    result = await uow.session.execute(stmt)
                    existing = result.scalar_one_or_none()
                    if existing:
                        # Update existing
                        existing.source_id = rel.source_id
                        existing.target_id = rel.target_id
                        existing.relationship_type = rel.relationship_type
                        existing.weight = rel.weight
                        existing.amount = rel.amount
                        existing.date = rel.date
                        existing.description = rel.description
                        existing.extra_data = rel.extra_data
                        existing.updated_at = rel.updated_at
                        existing.created_by = rel.created_by
                        continue
                uow.session.add(rel)
            
            await uow.flush()
            
            # Refresh all relationships
            saved_rels = []
            for rel in relationships:
                await uow.refresh(rel)
                saved_rels.append(rel)
            
            logger.debug(f"Saved {len(saved_rels)} GraphRelationships for case {saved_rels[0].case_id if saved_rels else 'unknown'}")
            return saved_rels
            
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Failed to save GraphRelationships: {e}")
            raise RepositoryError(
                operation="save_relationships",
                repository="GraphCommandRepository",
                original_error=e,
            ) from e
    
    async def delete_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """
        Delete all graph data for a case (entities + relationships).
        
        Atomic: Both entities and relationships are deleted in one transaction.
        
        Args:
            uow: Unit of Work (provides transaction context)
            case_id: Case UUID
            
        Raises:
            RepositoryError: If database operation fails
        """
        try:
            case_id_str = str(case_id)
            
            # Delete relationships first (due to foreign key constraints)
            stmt_rel = delete(GraphRelationship).where(GraphRelationship.case_id == case_id_str)
            rel_result = await uow.session.execute(stmt_rel)
            
            # Delete entities
            stmt_ent = delete(GraphEntity).where(GraphEntity.case_id == case_id_str)
            ent_result = await uow.session.execute(stmt_ent)
            
            await uow.flush()
            
            logger.info(
                f"Deleted graph for case {case_id}: "
                f"{rel_result.rowcount} relationships, {ent_result.rowcount} entities"
            )
        except Exception as e:
            logger.error(f"Failed to delete case graph for {case_id}: {e}")
            raise RepositoryError(
                operation="delete_case_graph",
                repository="GraphCommandRepository",
                case_id=str(case_id),
                original_error=e,
            ) from e
    
    async def exists(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> bool:
        """
        Check if graph data exists for a case.
        
        Args:
            uow: Unit of Work (provides transaction context)
            case_id: Case UUID
            
        Returns:
            True if graph data exists, False otherwise
        """
        try:
            case_id_str = str(case_id)
            stmt = select(GraphEntity).where(GraphEntity.case_id == case_id_str).limit(1)
            result = await uow.session.execute(stmt)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Failed to check existence for case {case_id}: {e}")
            raise RepositoryError(
                operation="exists",
                repository="GraphCommandRepository",
                case_id=str(case_id),
                original_error=e,
            ) from e