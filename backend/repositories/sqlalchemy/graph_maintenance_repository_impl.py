"""
Graph Maintenance Repository Implementation - SQLAlchemy ORM.

Handles deletion, cleanup, vacuum, and other maintenance operations.
"""

from uuid import UUID
import logging

from sqlalchemy import delete, text

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.models import GraphEntity, GraphRelationship
from backend.repositories.interfaces.graph_maintenance_repository import GraphMaintenanceRepository
from backend.infrastructure.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class GraphMaintenanceRepositoryImpl(GraphMaintenanceRepository):
    """
    Graph Maintenance Repository Implementation.
    
    Responsibilities:
    - Delete all graph data for a case
    - Clean up orphaned data
    - Vacuum/optimize tables
    """
    
    def __init__(self):
        """Initialize repository without dependencies."""
        pass
    
    async def delete_case_graph(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
    ) -> None:
        """
        Delete all graph data for a case (entities + relationships).
        
        Atomic: Both entities and relationships are deleted in one transaction.
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
                repository="GraphMaintenanceRepository",
                case_id=str(case_id),
                original_error=e,
            ) from e
    
    async def cleanup_orphaned(self, uow: IUnitOfWork) -> int:
        """
        Clean up orphaned graph data.
        
        Orphaned data = relationships pointing to non-existent entities.
        """
        try:
            # Find orphaned relationships
            stmt = text("""
                DELETE FROM graph_relationships
                WHERE source_id NOT IN (SELECT id FROM graph_entities)
                OR target_id NOT IN (SELECT id FROM graph_entities)
                RETURNING id
            """)
            result = await uow.session.execute(stmt)
            deleted = result.rowcount
            await uow.flush()
            
            logger.info(f"Cleaned up {deleted} orphaned relationships")
            return deleted
        except Exception as e:
            logger.error(f"Failed to cleanup orphaned data: {e}")
            raise RepositoryError(
                operation="cleanup_orphaned",
                repository="GraphMaintenanceRepository",
                original_error=e,
            ) from e
    
    async def vacuum(self) -> None:
        """Vacuum graph tables (optimize storage)."""
        try:
            # This requires a separate connection with autocommit
            # For now, just log that it should be done
            logger.info("Vacuum requested for graph tables")
            # TODO: Implement vacuum with separate connection
            # await session.execute(text("VACUUM ANALYZE graph_entities, graph_relationships"))
        except Exception as e:
            logger.error(f"Failed to vacuum graph tables: {e}")
            raise RepositoryError(
                operation="vacuum",
                repository="GraphMaintenanceRepository",
                original_error=e,
            ) from e