# backend/repositories/interfaces/procurement_search_repository.py

"""
Procurement Search Repository Interface.

Used by Investigation layer for dynamic search queries.
"""

from typing import Optional, Protocol, Sequence, TYPE_CHECKING

from backend.application.dto.investigation_criteria import InvestigationCriteria
from backend.application.dto.search_options import SearchOptions
from backend.application.dto.procurement_record import ProcurementRecord

if TYPE_CHECKING:
    from backend.graph.dto.rup_record_dto import RupRecordDTO


class IProcurementSearchRepository(Protocol):
    """Repository for procurement search and graph source retrieval."""

    async def search(
        self,
        criteria: InvestigationCriteria,
        options: Optional[SearchOptions] = None,
    ) -> Sequence[ProcurementRecord]:
        """Search procurement records by criteria."""
        ...

    async def get_by_id(
        self,
        source_id: int,
    ) -> Optional["RupRecordDTO"]:
        """Fetch one RUP source row for graph ingestion."""
        ...

    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Sequence["RupRecordDTO"]:
        """Fetch RUP source rows ordered deterministically by source ID."""
        ...