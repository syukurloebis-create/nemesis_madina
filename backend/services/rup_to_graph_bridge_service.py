"""Production bridge: RUP source records → canonical graph application.

R16.4.6.D.8.C.3
"""

from typing import Optional, Tuple
from uuid import UUID

from backend.infrastructure.unit_of_work import IUnitOfWork
from backend.graph.application.dto import GraphBuildRequest
from backend.graph.application.service import GraphRegenerationService
from backend.graph.domain.aggregate import GraphAggregate
from backend.graph.application.statistics import BuilderStatistics
from backend.repositories.interfaces.procurement_search_repository import (
    IProcurementSearchRepository,
)
from backend.graph.transformers.rup_to_graph_transformer import RupToGraphTransformer


class RupToGraphBridgeService:
    """Production bridge: RUP source records → canonical graph application.

    This bridge does NOT own the UOW or the graph service.
    It only orchestrates the flow from RUP repository to canonical graph service.
    """

    def __init__(
        self,
        rup_repository: IProcurementSearchRepository,
        graph_service: GraphRegenerationService,
    ):
        self._rup_repository = rup_repository
        self._graph_service = graph_service

    async def build_graph_from_rup(
        self,
        uow: IUnitOfWork,
        case_id: UUID,
        institution_id: UUID,
        limit: Optional[int] = None,
    ) -> Tuple[GraphAggregate, BuilderStatistics]:
        """Build graph from RUP source records for a case.

        Args:
            uow: Unit of Work (owned by caller)
            case_id: Case UUID
            institution_id: Institution UUID
            limit: Optional limit for RUP records (for testing)

        Returns:
            Tuple of (GraphAggregate, BuilderStatistics)

        Raises:
            ValueError: If limit < 0
        """
        if limit is not None and limit < 0:
            raise ValueError("limit must be >= 0")

        # 1. Fetch RUP records
        records = await self._rup_repository.get_all(limit=limit)

        # 2. Transform to nodes and edges
        rows = [self._to_dict(r) for r in records]
        nodes, edges = RupToGraphTransformer.transform(rows)

        # 3. Build GraphBuildRequest with pre-built nodes and edges
        request = GraphBuildRequest(
            case_id=case_id,
            institution_id=institution_id,
            nodes=nodes,
            edges=edges,
        )

        # 4. Delegate to canonical graph service
        return await self._graph_service.regenerate_graph(
            uow=uow,
            request=request,
            strategy="replace",
        )

    def _to_dict(self, record):
        return {
            "id": record.id,
            "kode_paket": record.package_code,
            "nama_paket": record.name,
            "nama_penyedia": record.vendor,
            "tahun_anggaran": record.year,
            "total_nilai": record.total_value,
            "nilai_pdn": record.pdn_value,
            "nama_instansi": record.institution,
            "satuan_kerja": record.work_unit,
            "sumber_dana": record.fund_source,
            "metode_pengadaan": record.procurement_method,
            "jenis_pengadaan": record.procurement_type,
            "status_paket": record.status,
            "sumber_transaksi": record.transaction_source,
        }
