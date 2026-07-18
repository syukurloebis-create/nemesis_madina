"""
Graph Infrastructure - Metadata Factory
"""

import uuid
from uuid import UUID
from datetime import datetime, timezone
from typing import Optional

from backend.graph.models import GraphMetadata  


class MetadataFactory:
    """
    Metadata Factory.
    
    Creates GraphMetadata instances.
    Centralizes metadata construction.
    """
    
    def create(
        self,
        case_id: UUID,
        version: int,
        checksum: str,
        reason: Optional[str] = None,
        regenerated_by: Optional[str] = None,
        graph_type: str = "default",
        algorithm_version: str = "1.0.0",
    ) -> GraphMetadata:
        """Create metadata entry."""
        return GraphMetadata(
            id=str(uuid.uuid4()),
            case_id=str(case_id),
            version=version,
            checksum=checksum,
            reason=reason,
            regenerated_by=regenerated_by or "system",
            graph_type=graph_type,
            algorithm_version=algorithm_version,
            created_at=datetime.now(timezone.utc),
        )


class GraphPersistenceRepository:
    def __init__(self, metadata_factory: MetadataFactory):
        self._metadata_factory = metadata_factory
    
    async def save_aggregate(self, uow, aggregate, checksum, strategy):
        metadata = self._metadata_factory.create(
            case_id=aggregate.case_id,
            version=new_version,
            checksum=checksum,
            regenerated_by="system",
        )
        uow.session.add(metadata)