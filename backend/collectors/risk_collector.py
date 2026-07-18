"""
Risk Collector — Menerima IRiskRepository langsung (DI).
"""

import logging
from uuid import UUID

from backend.collectors.interfaces.collector import ICollector
from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.core.context import ExecutionContext
from backend.dtos.collector_dtos import RiskCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason
from backend.collectors.assemblers.risk_assembler import RiskAssembler
from backend.repositories.interfaces.risk_repository import IRiskRepository
from backend.infrastructure.exceptions import RepositoryError
from backend.infrastructure.unit_of_work import UnitOfWorkFactory

logger = logging.getLogger(__name__)


class RiskCollector(ICollector[RiskCollectorDTO]):
    """
    Risk Collector — Menerima IRiskRepository via DI.
    """
    
    def __init__(
        self,
        repository: IRiskRepository,
        uow_factory: UnitOfWorkFactory,
    ):
        self._repository = repository
        self._uow_factory = uow_factory
    
    async def collect(
        self,
        uow: IUnitOfWork,
        context: ExecutionContext
    ) -> RiskCollectorDTO:
        """Collect risk data."""
        case_id = context.case_id
        
        try:
            row = await self._repository.get_summary(uow, case_id)
            
            if row is None:
                logger.debug("RiskCollector: No data for case %s", case_id)
                return RiskAssembler.assemble_empty()
            
            dto = RiskAssembler.assemble(row, engine_status=EngineStatus.OK)
            
            logger.info(
                "RiskCollector: score=%.2f, level=%s for case %s",
                dto.score,
                dto.level,
                case_id
            )
            
            return dto
            
        except RepositoryError as e:
            logger.warning(f"RiskCollector repository failure: {e}")
            return RiskCollectorDTO.error_fallback(
                error=str(e),
                reason=FallbackReason.QUERY_ERROR
            )
            return RiskCollectorDTO.error_fallback(
                error=str(e),
                reason=FallbackReason.QUERY_ERROR
            )
            raise