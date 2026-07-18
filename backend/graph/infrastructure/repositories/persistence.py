# backend/graph/infrastructure/repositories/persistence.py
from backend.infrastructure.unit_of_work import IUnitOfWork

class GraphPersistenceRepository:
    """
    Atomic Persistence Repository.
    
    Wraps all persistence operations in a single atomic boundary.
    """
    
    async def save_aggregate(
        self,
        uow: IUnitOfWork,
        aggregate: GraphAggregate,
        strategy: SaveStrategy = SaveStrategy.REPLACE,
    ) -> int:
        """Save with optimistic concurrency control."""
        # 1. Get current version
        current_metadata = await self._metadata_repo.get_latest(uow, aggregate.case_id)
        
        # 2. Check version
        if current_metadata:
            if aggregate.version < current_metadata.version:
                raise OptimisticLockError(
                    f"Version conflict: current={current_metadata.version}, "
                    f"attempted={aggregate.version}"
                )
            if aggregate.version > current_metadata.version + 1:
                raise OptimisticLockError(
                    f"Version gap: current={current_metadata.version}, "
                    f"attempted={aggregate.version}"
                )
        
        # 3. Increment version
        new_version = (current_metadata.version + 1) if current_metadata else 1
        
        # 4. Update aggregate version
        aggregate = GraphAggregate(
            case_id=aggregate.case_id,
            institution_id=aggregate.institution_id,
            nodes=aggregate.nodes,
            edges=aggregate.edges,
            version=new_version,
            checksum=aggregate.checksum,
        )
        
        # 5. Save
        await self._save_atomic(uow, aggregate, strategy)
        
        return new_version


    async def _save_entities(self, uow, aggregate, strategy):
        """Save entities."""
        entities = self._mapper.map_entities(aggregate)
        for entity in entities:
            uow.session.add(entity)
    
    async def _save_relationships(self, uow, aggregate, strategy):
        """Save relationships."""
        relationships = self._mapper.map_relationships(aggregate)
        for rel in relationships:
            uow.session.add(rel)
    
    async def _save_metadata(self, uow, case_id, version, checksum):
        """Save metadata."""
        metadata = GraphMetadata(
            case_id=str(case_id),
            version=version,
            checksum=checksum,
            created_at=datetime.now(timezone.utc),
        )
        uow.session.add(metadata)


class OptimisticLockError(Exception):
    """Raised when version conflict occurs."""
    pass


class GraphRegenerationService:
    async def regenerate_graph(self, uow, request):
        try:
            version = await self._repository.save_aggregate(uow, aggregate)
            logger.info(f"Saved with version {version}")
        except OptimisticLockError as e:
            logger.warning(f"Optimistic lock failed: {e}")
            # Retry or abort
