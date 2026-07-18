"""
Graph Infrastructure - Write Repository Implementation

Implements GraphWriteRepository interface.
"""

from typing import Optional
from uuid import UUID
import logging

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.infrastructure.interfaces.repositories import GraphWriteRepository
from backend.graph.infrastructure.mappers.to_orm import GraphToOrmMapper
from backend.graph.models import GraphEntity, GraphRelationship

logger = logging.getLogger(__name__)


# backend/graph/infrastructure/repositories/write.py

class GraphWriteRepositoryImpl(GraphWriteRepository):
    """
    Graph Write Repository Implementation.
    
    Now handles business key deduplication.
    """
    
    def __init__(
        self,
        mapper: GraphToOrmMapper,
        metadata_repo: GraphMetadataRepository,
    ):
        self._mapper = mapper
        self._metadata_repo = metadata_repo
    
    async def save_aggregate(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
        strategy: str = "replace",
    ) -> None:
        """
        Save aggregate to database.
        
        Handles:
        - Business key deduplication
        - Version management
        - Checksum persistence
        """
        # 1. Check if graph exists
        existing = await self._get_existing_entities(uow, aggregate.case_id)
        existing_by_business_key = {
            entity.extra_data.get("business_key"): entity
            for entity in existing
        }
        
        # 2. Map domain to ORM
        entities, relationships = self._mapper.map(aggregate)
        
        # 3. Reuse existing IDs for matching business keys
        for entity in entities:
            business_key = entity.extra_data.get("business_key")
            if business_key and business_key in existing_by_business_key:
                entity.id = existing_by_business_key[business_key].id
        
        # 4. Save entities
        if entities:
            for entity in entities:
                # Check if entity exists
                if entity.id and entity.id in {e.id for e in existing}:
                    # Update existing
                    existing_entity = next(e for e in existing if e.id == entity.id)
                    existing_entity.name = entity.name
                    existing_entity.extra_data = entity.extra_data
                else:
                    # Insert new
                    uow.session.add(entity)
        
        if relationships:
            uow.session.add_all(relationships)
        
        # 5. Save metadata
        await self._metadata_repo.save_metadata(
            uow,
            aggregate.case_id,
            aggregate.version,
            aggregate.checksum or "",
        )
        
        await uow.flush()
        
        logger.info(
            f"Saved graph for case {aggregate.case_id}: "
            f"{len(entities)} entities, {len(relationships)} relationships, "
            f"version {aggregate.version}"
        )
    
    async def _get_existing_entities(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> List[GraphEntity]:
        """Get existing entities for case."""
        stmt = select(GraphEntity).where(GraphEntity.case_id == str(case_id))
        result = await uow.session.execute(stmt)
        return result.scalars().all()

# backend/graph/infrastructure/repositories/write.py

class GraphWriteRepositoryImpl:
    
    async def save_aggregate(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
        strategy: str = "replace",
    ) -> None:
        """
        Save aggregate with strategy.
        
        Strategies:
        - replace: Delete all, insert new
        - merge: Update existing, insert new
        - append: Only insert new
        """
        if strategy == "replace":
            await self._replace_strategy(uow, aggregate)
        elif strategy == "merge":
            await self._merge_strategy(uow, aggregate)
        elif strategy == "append":
            await self._append_strategy(uow, aggregate)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    async def _replace_strategy(self, uow, aggregate):
        """Delete all, insert new."""
        # Delete existing
        await self._delete_case_graph(uow, aggregate.case_id)
        # Insert new
        entities, relationships = self._mapper.map(aggregate)
        uow.session.add_all(entities)
        uow.session.add_all(relationships)
    
    async def _merge_strategy(self, uow, aggregate):
        """Update existing, insert new."""
        # Get existing entities
        existing = await self._get_existing_entities(uow, aggregate.case_id)
        existing_by_key = {e.extra_data.get("business_key"): e for e in existing}
        
        # Map and merge
        entities, relationships = self._mapper.map(aggregate)
        
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
        await self._delete_case_relationships(uow, aggregate.case_id)
        uow.session.add_all(relationships)
    
    async def _append_strategy(self, uow, aggregate):
        """Only insert new."""
        # Get existing entities
        existing = await self._get_existing_entities(uow, aggregate.case_id)
        existing_by_key = {e.extra_data.get("business_key"): e for e in existing}
        
        # Map and filter
        entities, relationships = self._mapper.map(aggregate)
        
        # Only insert entities that don't exist
        for entity in entities:
            business_key = entity.extra_data.get("business_key")
            if not (business_key and business_key in existing_by_key):
                uow.session.add(entity)
        
        # For relationships, only insert if both entities exist
        # Simplified: just add all (could have duplicates)
        uow.session.add_all(relationships)