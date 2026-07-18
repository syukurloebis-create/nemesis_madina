"""
Procurement Collector — Menerima IProcurementRepository langsung (DI).
"""

import logging
from uuid import UUID

from backend.collectors.interfaces.collector import ICollector
from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.core.context import ExecutionContext
from backend.dtos.collector_dtos import ProcurementCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason
from backend.collectors.assemblers.procurement_assembler import ProcurementAssembler
from backend.repositories.interfaces.procurement_repository import IProcurementRepository
from backend.infrastructure.exceptions import RepositoryError
from backend.infrastructure.unit_of_work import UnitOfWorkFactory

logger = logging.getLogger(__name__)


class ProcurementCollector(ICollector[ProcurementCollectorDTO]):
    """
    Procurement Collector — Menerima IProcurementRepository via DI.
    
    NOTE: Data procurement adalah GLOBAL (tidak memiliki case_id).
    """
    
    def __init__(
        self,
        repository: IProcurementRepository,
        uow_factory: UnitOfWorkFactory,
    ):
        self._repository = repository
        self._uow_factory = uow_factory
    
    async def collect(
        self,
        uow: IUnitOfWork,
        context: ExecutionContext
    ) -> ProcurementCollectorDTO:
        """Collect procurement data (global)."""
        case_id = context.case_id
        
        try:
            row = await self._repository.get_summary(uow)
            
            if row.packages == 0:
                logger.debug("ProcurementCollector: No data")
                return ProcurementAssembler.assemble_empty()
            
            dto = ProcurementAssembler.assemble(row, engine_status=EngineStatus.OK)
            
            logger.info(
                "ProcurementCollector: %d packages, %d vendors globally",
                dto.packages,
                dto.vendors
            )
            
            return dto
            
        except RepositoryError as e:
            logger.warning(
                "ProcurementCollector repository failure",
                extra={
                    "case_id": str(case_id),
                    "collector": "procurement",
                    "error": str(e)
                }
            )
            return ProcurementCollectorDTO.error_fallback(
                error=str(e),
                reason=FallbackReason.QUERY_ERROR
            )
            raise