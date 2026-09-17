# backend/repositories/sqlalchemy/procurement_search_repository_impl.py

"""
Procurement Search Repository Implementation.

Uses ORM with dynamic filters for investigation queries.
"""

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.sql import Executable, Select
from sqlalchemy.engine import Result
from sqlalchemy import select

from backend.application.dto.investigation_criteria import InvestigationCriteria
from backend.application.dto.search_options import SearchOptions
from backend.application.dto.procurement_record import ProcurementRecord
from backend.infrastructure.models.procurement import RupPaketDetailed
from backend.repositories.interfaces.procurement_search_repository import IProcurementSearchRepository
from backend.graph.dto.rup_record_dto import RupRecordDTO


class ProcurementSearchRepositoryImpl(IProcurementSearchRepository):
    """Search repository using ORM with dynamic filters."""

    def __init__(self, session_factory: async_sessionmaker):
        self._session_factory = session_factory

    async def _execute(self, stmt: Executable) -> Result:
        async with self._session_factory() as session:
            return await session.execute(stmt)

    @staticmethod
    def _safe_str(value: Optional[str]) -> str:
        return value or ""

    @staticmethod
    def _safe_int(value: Optional[int]) -> int:
        return value or 0

    @staticmethod
    def _safe_float(value) -> float:
        return float(value or 0)

    def _validate_options(self, options: Optional[SearchOptions]) -> None:
        if options:
            if options.limit is not None and options.limit < 0:
                raise ValueError("limit must be >= 0")
            if options.offset is not None and options.offset < 0:
                raise ValueError("offset must be >= 0")

    def _build_statement(
        self,
        criteria: InvestigationCriteria,
        options: Optional[SearchOptions] = None,
    ) -> Select:
        stmt = select(RupPaketDetailed)

        if criteria.institutions:
            stmt = stmt.where(RupPaketDetailed.nama_instansi.in_(criteria.institutions))
        if criteria.vendors:
            stmt = stmt.where(RupPaketDetailed.nama_penyedia.in_(criteria.vendors))
        if criteria.packages:
            stmt = stmt.where(RupPaketDetailed.kode_paket.in_(criteria.packages))
        if criteria.years:
            stmt = stmt.where(RupPaketDetailed.tahun_anggaran.in_(criteria.years))

        stmt = stmt.order_by(
            RupPaketDetailed.tahun_anggaran,
            RupPaketDetailed.kode_paket,
            RupPaketDetailed.id,
        )

        if options:
            if options.limit is not None:
                stmt = stmt.limit(options.limit)
            if options.offset is not None:
                stmt = stmt.offset(options.offset)

        return stmt

    def _to_record(self, row: RupPaketDetailed) -> ProcurementRecord:
        return ProcurementRecord(
            vendor_name=self._safe_str(row.nama_penyedia),
            package_code=self._safe_str(row.kode_paket),
            package_name=self._safe_str(row.nama_paket),
            institution_name=self._safe_str(row.nama_instansi),
            sub_unit=self._safe_str(row.satuan_kerja),
            year=self._safe_int(row.tahun_anggaran),
            value=self._safe_float(row.total_nilai),
            method=self._safe_str(row.metode_pengadaan),
            transaction_source=self._safe_str(row.sumber_transaksi),
            funding_source=self._safe_str(row.sumber_dana),
            procurement_type=self._safe_str(row.jenis_pengadaan),
            status=self._safe_str(row.status_paket),
            ppk=None,
        )

    # ============================================================
    # SINGLE MAPPING AUTHORITY: RupPaketDetailed → RupRecordDTO
    # ============================================================

    def _to_rup_record_dto(self, row: RupPaketDetailed) -> RupRecordDTO:
        from decimal import Decimal
        return RupRecordDTO(
            id=row.id,
            package_code=row.kode_paket or "",
            name=row.nama_paket or "",
            vendor=row.nama_penyedia or "",
            year=row.tahun_anggaran or 0,
            rup_code=row.kode_rup,
            total_value=Decimal(str(row.total_nilai)) if row.total_nilai is not None else None,
            pdn_value=Decimal(str(row.nilai_pdn)) if row.nilai_pdn is not None else None,
            institution=row.nama_instansi,
            work_unit=row.satuan_kerja,
            fund_source=row.sumber_dana,
            procurement_method=row.metode_pengadaan,
            procurement_type=row.jenis_pengadaan,
            status=row.status_paket,
            transaction_source=row.sumber_transaksi,
        )

    # ============================================================
    # PUBLIC API
    # ============================================================

    async def search(
        self,
        criteria: InvestigationCriteria,
        options: Optional[SearchOptions] = None,
    ) -> Sequence[ProcurementRecord]:
        self._validate_options(options)
        stmt = self._build_statement(criteria, options)
        result = await self._execute(stmt)
        rows = result.scalars().all()
        return [self._to_record(row) for row in rows]

    async def get_by_id(
        self,
        source_id: int,
    ) -> Optional[RupRecordDTO]:
        """Fetch one RUP source row for graph ingestion."""
        stmt = select(RupPaketDetailed).where(RupPaketDetailed.id == source_id)
        result = await self._execute(stmt)
        row = result.scalar_one_or_none()
        if row is None:
            return None
        return self._to_rup_record_dto(row)

    async def get_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> Sequence[RupRecordDTO]:
        """Fetch RUP source rows ordered deterministically by source ID."""
        if limit is not None and limit < 0:
            raise ValueError("limit must be >= 0")
        if offset < 0:
            raise ValueError("offset must be >= 0")

        stmt = select(RupPaketDetailed).order_by(RupPaketDetailed.id)

        if limit is not None:
            stmt = stmt.limit(limit)
        if offset > 0:
            stmt = stmt.offset(offset)

        result = await self._execute(stmt)
        rows = result.scalars().all()
        return [self._to_rup_record_dto(row) for row in rows]