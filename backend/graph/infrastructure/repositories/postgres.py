"""
Graph Infrastructure - PostgreSQL Repository Implementation
"""

import uuid
from typing import Optional, List, Tuple, Dict
from uuid import UUID
import logging

from sqlalchemy import select, delete

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.domain.aggregate import GraphAggregate

from backend.graph.infrastructure.interfaces.repository import (
    GraphRepository,
    SaveStrategy,
    DeleteStrategy,
    OptimisticLockError,
)
from backend.graph.infrastructure.interfaces.identity import IdentityGenerator
from backend.graph.infrastructure.mappers.to_orm import GraphToOrmMapper
from backend.graph.infrastructure.mappers.to_domain import OrmToGraphMapper
from backend.graph.infrastructure.repositories.metadata import GraphMetadataRepository
from backend.graph.infrastructure.services.checksum import CanonicalChecksumService
from backend.graph.infrastructure.factories.metadata import MetadataFactory
from backend.graph.models import GraphEntity, GraphRelationship, GraphMetadata

logger = logging.getLogger(__name__)


class PostgresGraphRepository(GraphRepository):  # ← Correct inheritance
    """PostgreSQL Graph Repository Implementation."""
    
    def __init__(
        self,
        to_orm_mapper: GraphToOrmMapper,
        identity_generator: IdentityGenerator,
        to_domain_mapper: OrmToGraphMapper,
        metadata_repo: GraphMetadataRepository,
        checksum_service: CanonicalChecksumService,
        metadata_factory: MetadataFactory,
    ):
        self._identity_generator = identity_generator
        self._to_orm_mapper = to_orm_mapper
        self._to_domain_mapper = to_domain_mapper
        self._metadata_repo = metadata_repo
        self._checksum_service = checksum_service
        self._metadata_factory = metadata_factory
    
    # ============================================================
    # GraphReadPort
    # ============================================================
    
    async def get_by_case(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> Optional[GraphAggregate]:
        """Get aggregate by case ID."""
        case_id_str = str(case_id)
        
        # 1. Get entities
        stmt_entities = select(GraphEntity).where(GraphEntity.case_id == case_id_str)
        result = await uow.session.execute(stmt_entities)
        entities = result.scalars().all()
        
        if not entities:
            return None
        
        # 2. Get relationships
        stmt_relationships = select(GraphRelationship).where(
            GraphRelationship.case_id == case_id_str
        )
        result = await uow.session.execute(stmt_relationships)
        relationships = result.scalars().all()
        
        # 3. Get metadata
        metadata = await self._metadata_repo.get_latest(uow, case_id)
        
        # 4. Map to domain
        aggregate = self._to_domain_mapper.map(
            entities=entities,
            relationships=relationships,
            version=metadata.version if metadata else 1,
            checksum=metadata.checksum if metadata else "",
        )
        
        logger.debug(f"Loaded graph for case {case_id}: {len(entities)} entities")
        return aggregate
    
    async def exists(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> bool:
        """Check if graph exists for case."""
        stmt = select(GraphEntity).where(GraphEntity.case_id == str(case_id)).limit(1)
        result = await uow.session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    # ============================================================
    # GraphWritePort
    # ============================================================
    
    async def save_aggregate(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
        strategy: SaveStrategy = SaveStrategy.REPLACE,
    ) -> int:
        """
        Save aggregate with optimistic concurrency control.  

        Returns:
            New version number
        """
        # 1. Get current version
        current_metadata = await self._metadata_repo.get_latest(uow, aggregate.case_id)

        # 2. Optimistic lock check
        if current_metadata:
            if aggregate.version < current_metadata.version:
                raise OptimisticLockError(
                    f"Version conflict: current={current_metadata.version}, "
                    f"attempted={aggregate.version}"
                )

        # 3. Determine new version
        new_version = (current_metadata.version + 1) if current_metadata else 1

        # 4. Compute checksum
        checksum = self._checksum_service.compute_from_aggregate(aggregate)

        # 5. Generate persistence IDs - ✅ PASS current_metadata
        entity_ids = await self._generate_entity_ids(uow, aggregate, current_metadata)  
        relationship_ids = await self._generate_relationship_ids(uow, aggregate, current_metadata)  

        # 6. Map to ORM
        entities = self._to_orm_mapper.map_entities(aggregate, entity_ids)
        relationships = self._to_orm_mapper.map_relationships(
            aggregate, entity_ids, relationship_ids
        )

        # 7. Execute strategy
        await self._execute_strategy(uow, aggregate.case_id, entities, relationships, strategy)

        # 8. Save metadata
        metadata = self._metadata_factory.create(
            case_id=aggregate.case_id,
            version=new_version,
            checksum=checksum,
            regenerated_by="system",
        )
        uow.session.add(metadata)

        await uow.flush()

        logger.info(
            f"Saved graph for case {aggregate.case_id}: "
            f"{len(entities)} entities, {len(relationships)} relationships, "
            f"version {new_version}"
        )

        return new_version
    
    async def _generate_entity_ids(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
        current_metadata: Optional[GraphMetadata],
    ) -> Dict[str, str]:
        """Generate or reuse entity persistence IDs."""
        entity_ids = {}
        
        # 1. Get existing entities
        existing = await self._get_existing_entities(uow, aggregate.case_id)
        existing_by_key = {
            e.extra_data.get("business_key"): e.id
            for e in existing
        }
        
        # 2. Generate IDs for new entities
        for node in aggregate.nodes:
            if node.business_key in existing_by_key:
                entity_ids[node.business_key] = existing_by_key[node.business_key]
            else:
                entity_ids[node.business_key] = str(uuid.uuid4())
        
        return entity_ids
    
    async def _generate_relationship_ids(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
        current_metadata: Optional[GraphMetadata],
    ) -> Dict[tuple, str]:
        """Generate or reuse relationship persistence IDs."""
        relationship_ids = {}
        
        # 1. Get existing relationships
        existing = await self._get_existing_relationships(uow, aggregate.case_id)
        existing_by_key = {
            (r.extra_data.get("source_business_key"),
             r.extra_data.get("target_business_key"),
             r.relationship_type): r.id
            for r in existing
            if r.extra_data.get("source_business_key")
        }
        
        # 2. Generate IDs for new relationships
        for edge in aggregate.edges:
            key = (edge.source_key, edge.target_key, edge.relationship_type)
            if key in existing_by_key:
                relationship_ids[key] = existing_by_key[key]
            else:
                relationship_ids[key] = str(uuid.uuid4())
        
        return relationship_ids
    
    async def _get_existing_entities(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> List[GraphEntity]:
        """Get existing entities for case."""
        stmt = select(GraphEntity).where(GraphEntity.case_id == str(case_id))
        result = await uow.session.execute(stmt)
        return result.scalars().all()
    
    async def _get_existing_relationships(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> List[GraphRelationship]:
        """Get existing relationships for case."""
        stmt = select(GraphRelationship).where(
            GraphRelationship.case_id == str(case_id)
        )
        result = await uow.session.execute(stmt)
        return result.scalars().all()
    
    async def _execute_strategy(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
        strategy: SaveStrategy,
    ) -> None:
        """Execute save strategy."""
        if strategy == SaveStrategy.REPLACE:
            # Delete all, insert new
            await self._delete_case_graph(uow, case_id)
            uow.session.add_all(entities)
            uow.session.add_all(relationships)
        elif strategy == SaveStrategy.MERGE:
            # Merge strategy: update existing, insert new
            await self._merge_strategy(uow, case_id, entities, relationships)
        elif strategy == SaveStrategy.APPEND:
            # Only insert new
            await self._append_strategy(uow, case_id, entities, relationships)
        elif strategy == SaveStrategy.UPSERT:
            await self._upsert_strategy(uow, case_id, entities, relationships)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    async def _merge_strategy(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
    ) -> None:
        """Merge: update existing, insert new."""
        # Get existing entities
        existing = await self._get_existing_entities(uow, case_id)
        existing_by_key = {e.extra_data.get("business_key"): e for e in existing}
        
        # Merge entities
        for entity in entities:
            business_key = entity.extra_data.get("business_key")
            if business_key and business_key in existing_by_key:
                # Update existing
                existing_entity = existing_by_key[business_key]
                existing_entity.name = entity.name
                existing_entity.extra_data = entity.extra_data
            else:
                # Insert new
                uow.session.add(entity)
        
        # Relationships - delete all, insert new (simplified)
        await self._delete_case_relationships(uow, case_id)
        uow.session.add_all(relationships)
    
    async def _append_strategy(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
    ) -> None:
        """Only insert new entities and relationships."""
        # Get existing entities
        existing = await self._get_existing_entities(uow, case_id)
        existing_by_key = {e.extra_data.get("business_key"): e for e in existing}
        
        # Only insert entities that don't exist
        for entity in entities:
            business_key = entity.extra_data.get("business_key")
            if not (business_key and business_key in existing_by_key):
                uow.session.add(entity)
        
        # For relationships, only insert if both entities exist
        # Simplified: add all, but unique constraint will prevent duplicates
        uow.session.add_all(relationships)
    
    async def _upsert_strategy(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
    ) -> None:
        """Upsert: insert or update."""
        # Use merge strategy
        await self._merge_strategy(uow, case_id, entities, relationships)
    
    # ============================================================
    # GraphMaintenancePort
    # ============================================================
    
    async def delete_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        strategy: DeleteStrategy = DeleteStrategy.CASCADE,
    ) -> None:
        """Delete all graph data for a case."""
        if strategy == DeleteStrategy.CASCADE:
            await self._delete_case_graph(uow, case_id)
        elif strategy == DeleteStrategy.SOFT_DELETE:
            await self._soft_delete_case_graph(uow, case_id)
        elif strategy == DeleteStrategy.ARCHIVE:
            await self._archive_case_graph(uow, case_id)
        else:
            raise ValueError(f"Unknown delete strategy: {strategy}")
    
    async def _delete_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """Physical delete."""
        case_id_str = str(case_id)
        
        # Delete relationships first (due to foreign key constraints)
        stmt_rel = delete(GraphRelationship).where(
            GraphRelationship.case_id == case_id_str
        )
        rel_result = await uow.session.execute(stmt_rel)
        
        # Delete entities
        stmt_ent = delete(GraphEntity).where(GraphEntity.case_id == case_id_str)
        ent_result = await uow.session.execute(stmt_ent)
        
        # Delete metadata
        stmt_meta = delete(GraphMetadata).where(GraphMetadata.case_id == case_id_str)
        meta_result = await uow.session.execute(stmt_meta)
        
        await uow.flush()
        
        logger.info(
            f"Deleted graph for case {case_id}: "
            f"{rel_result.rowcount} relationships, "
            f"{ent_result.rowcount} entities, "
            f"{meta_result.rowcount} metadata entries"
        )
    
    async def _soft_delete_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """Soft delete (mark as deleted)."""
        case_id_str = str(case_id)
        
        # Add deleted_at column to entities and relationships
        # For now, we just log
        logger.info(f"Soft delete for case {case_id} not yet implemented")
    
    async def _archive_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """Archive graph data."""
        logger.info(f"Archive for case {case_id} not yet implemented")
    
    async def _delete_case_relationships(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """Delete all relationships for a case."""
        stmt = delete(GraphRelationship).where(
            GraphRelationship.case_id == str(case_id)
        )
        await uow.session.execute(stmt)