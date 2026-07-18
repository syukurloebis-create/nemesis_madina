"""
Graph Infrastructure - Metadata Repository
"""

from uuid import UUID
from datetime import datetime, timezone
from typing import Optional, Tuple  
from sqlalchemy import select

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.models import GraphMetadata  


class GraphMetadataRepository:
    """
    Graph Metadata Repository.
    
    Manages graph version and checksum.
    """
    
    async def get_version(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> Optional[int]:
        """Get current version for case."""
        stmt = select(GraphMetadata).where(
            GraphMetadata.case_id == str(case_id)
        ).order_by(GraphMetadata.version.desc()).limit(1)
        
        result = await uow.session.execute(stmt)
        metadata = result.scalar_one_or_none()
        
        return metadata.version if metadata else None
    
    async def get_checksum(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> Optional[str]:
        """Get current checksum for case."""
        stmt = select(GraphMetadata).where(
            GraphMetadata.case_id == str(case_id)
        ).order_by(GraphMetadata.version.desc()).limit(1)
        
        result = await uow.session.execute(stmt)
        metadata = result.scalar_one_or_none()
        
        return metadata.checksum if metadata else None
    
    async def save_metadata(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        version: int,
        checksum: str,
    ) -> None:
        """Save graph metadata."""
        metadata = GraphMetadata(
            case_id=str(case_id),
            version=version,
            checksum=checksum,
            created_at=datetime.now(timezone.utc),
        )
        uow.session.add(metadata)
        await uow.flush()
    

    async def get_latest(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> Optional[GraphMetadata]:
        """
        Get latest metadata in one query.
        
        Returns:
            GraphMetadata with both version and checksum
        """
        stmt = select(GraphMetadata).where(
            GraphMetadata.case_id == str(case_id)
        ).order_by(GraphMetadata.version.desc()).limit(1)
        
        result = await uow.session.execute(stmt)
        return result.scalar_one_or_none()


    async def get_version_and_checksum(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> Tuple[Optional[int], Optional[str]]:
        """Get both version and checksum in one query."""
        latest = await self.get_latest(uow, case_id)
        if latest:
            return latest.version, latest.checksum
        return None, None