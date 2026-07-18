"""
Evidence Collector — Menerima IEvidenceRepository langsung (DI).
"""

import logging
from uuid import UUID

from backend.collectors.interfaces.collector import ICollector
from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.core.context import ExecutionContext
from backend.dtos.collector_dtos import EvidenceCollectorDTO
from backend.domain.enums import EngineStatus, FallbackReason
from backend.collectors.assemblers.evidence_assembler import EvidenceAssembler
from backend.repositories.interfaces.evidence_repository import IEvidenceRepository
from backend.infrastructure.exceptions import RepositoryError
from backend.infrastructure.unit_of_work import UnitOfWorkFactory

logger = logging.getLogger(__name__)


class EvidenceCollector(ICollector[EvidenceCollectorDTO]):
    """
    Evidence Collector — Menerima IEvidenceRepository via DI.
    """
    
    def __init__(
        self,
        repository: IEvidenceRepository,
        uow_factory: UnitOfWorkFactory,
    ):
        self._repository = repository
        self._uow_factory = uow_factory
    
    async def collect(
        self,
        uow: IUnitOfWork,
        context: ExecutionContext
    ) -> EvidenceCollectorDTO:
        """Collect evidence data."""
        case_id = context.case_id
        
        try:
            row = await self._repository.get_summary(uow, case_id)
            
            if row.total == 0:
                logger.debug("EvidenceCollector: No data for case %s", case_id)
                return EvidenceAssembler.assemble_empty()
            
            dto = EvidenceAssembler.assemble(row, engine_status=EngineStatus.OK)
            
            logger.info(
                "EvidenceCollector: %d evidence records for case %s (verified=%d)",
                dto.total,
                case_id,
                dto.verified
            )
            
            return dto
            
        except RepositoryError as e:
            logger.warning(
                "EvidenceCollector repository failure",
                extra={
                    "case_id": str(case_id),
                    "collector": "evidence",
                    "error": str(e)
                }
            )
            return EvidenceCollectorDTO.error_fallback(
                error=str(e),
                reason=FallbackReason.QUERY_ERROR
            )
            raise