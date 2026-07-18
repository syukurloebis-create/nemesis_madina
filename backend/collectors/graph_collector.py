"""
Graph Collector — Menerima IGraphRepository langsung (DI).
"""

import logging
from uuid import UUID

from backend.collectors.interfaces.collector import ICollector
from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.core.context import ExecutionContext
from backend.dtos.collector_dtos import GraphCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason
from backend.collectors.assemblers.graph_assembler import GraphAssembler
from backend.repositories.interfaces.graph_repository import IGraphRepository
from backend.infrastructure.exceptions import RepositoryError
from backend.infrastructure.unit_of_work import UnitOfWorkFactory 

logger = logging.getLogger(__name__)


class GraphCollector(ICollector[GraphCollectorDTO]):
    """
    Graph Collector — Menerima IGraphRepository via DI.
    
    ✅ Collector menerima repository langsung (bukan factory)
    ✅ Repository dipanggil langsung: self._repository.get_summary()
    """
    
    def __init__(
        self,
        repository: IGraphRepository,
        uow_factory: UnitOfWorkFactory,  # ← TAMBAHKAN
    ):
        self._repository = repository
        self._uow_factory = uow_factory
    
    async def collect(
        self,
        uow: IUnitOfWork,
        context: ExecutionContext
    ) -> GraphCollectorDTO:
        logger.error("🚨🚨🚨 GraphCollector.collect() WAS CALLED! 🚨🚨🚨")
        logger.error("🚨 case_id: %s", context.case_id)
        """Collect graph data."""
        case_id = context.case_id

        logger.info(
            "🔍 GraphCollector.collect() called for case_id=%s",
            case_id
        )
        
        try:
            # ✅ Panggil repository langsung
            row = await self._repository.get_summary(uow, case_id)
            logger.warning(
                "🔍 GraphCollector: row.entities=%s, row.relationships=%s",
                row.entities,
                row.relationships
            )
            
            if row.entities == 0 and row.relationships == 0:
                logger.debug("GraphCollector: No data for case %s", case_id)
                return GraphAssembler.assemble_empty()
            
            dto = GraphAssembler.assemble(row, engine_status=EngineStatus.OK)
            
            logger.info(
                "GraphCollector: %d entities, %d relationships for case %s",
                dto.entities,
                dto.relationships,
                case_id
            )
            logger.warning(
                "🔍 GraphCollector: returning dto with entities=%s, relationships=%s",
                dto.entities,
                dto.relationships
            )
            return dto
            
        except RepositoryError as e:
            # 🔍 DEBUG: Log exception dan propagate
            logger.exception(
                "GraphCollector repository failure",
                extra={
                    "case_id": str(case_id),
                    "collector": "graph",
                    "error": str(e),
                    "error_type": type(e).__name__
                }
            )
            # ✅ Propagate error, jangan return fallback
            raise