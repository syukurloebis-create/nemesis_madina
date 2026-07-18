# backend/graph/domain/services/checksum.py

class GraphChecksumService:
    """
    Single source of truth for checksum computation.
    
    Used by:
    - Domain (for aggregate validation)
    - Infrastructure (for persistence checksum)
    - Audit (for integrity verification)
    - Export/Replication (for consistency checks)
    """
    
    SCHEMA_VERSION = 1
    
    def compute_from_aggregate(self, aggregate: GraphAggregate) -> str:
        """Compute checksum from aggregate (Domain use)."""
        canonical = self._to_canonical(aggregate)
        canonical["_schema_version"] = self.SCHEMA_VERSION
        return self._compute_hash(canonical)
    
    def compute_from_orm(self, entities, relationships) -> str:
        """Compute checksum from ORM models (Infrastructure use)."""
        canonical = self._to_canonical_from_orm(entities, relationships)
        canonical["_schema_version"] = self.SCHEMA_VERSION
        return self._compute_hash(canonical)