"""
Fraud Collector — Menerima repository langsung (DI).

✅ Structured logging dengan extra
✅ logger.warning untuk fallback (bukan logger.exception)
"""

import logging
from uuid import UUID

from backend.collectors.interfaces.collector import ICollector
from backend.infrastructure.unit_of_work import IUnitOfWork, UnitOfWorkFactory  # ← TAMBAHKAN
from backend.core.context import ExecutionContext
from backend.dtos.collector_dtos import FraudCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason
from backend.collectors.assemblers.fraud_assembler import FraudAssembler
from backend.repositories.interfaces.fraud_repository import IFraudRepository
from backend.infrastructure.exceptions import RepositoryError

logger = logging.getLogger(__name__)


class FraudCollector(ICollector[FraudCollectorDTO]):
    """Fraud Collector — Menerima IFraudRepository via DI."""
    
    def __init__(
        self,
        repository: IFraudRepository,
        uow_factory: UnitOfWorkFactory,  # ← SEKARANG TERDEFINISI
    ):
        self._repository = repository
        self._uow_factory = uow_factory
    
    async def collect(
        self,
        uow: IUnitOfWork,
        context: ExecutionContext
    ) -> FraudCollectorDTO:
        """Collect fraud data."""
        case_id = context.case_id
        
        try:
            summary_row = await self._repository.get_summary(uow, case_id)
            pattern_rows = await self._repository.get_patterns(uow, case_id)
            
            if summary_row.total_patterns == 0:
                logger.debug("FraudCollector: No data for case %s", case_id)
                return FraudAssembler.assemble_empty()
            
            dto = FraudAssembler.assemble(
                summary_row=summary_row,
                pattern_rows=tuple(pattern_rows),
                engine_status=EngineStatus.OK
            )
            
            logger.info(
                "FraudCollector: %d patterns for case %s (critical=%d)",
                dto.total_patterns,
                case_id,
                dto.critical
            )
            
            return dto
            
        except RepositoryError as e:
            logger.warning(
                "FraudCollector repository failure",
                extra={
                    "case_id": str(case_id),
                    "collector": "fraud",
                    "operation": getattr(e, "operation", "unknown"),
                    "error": str(e)
                }
            )
            return FraudCollectorDTO.error_fallback(
                error=str(e),
                reason=FallbackReason.QUERY_ERROR
            )