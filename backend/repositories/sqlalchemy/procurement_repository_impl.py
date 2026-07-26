# backend/repositories/sqlalchemy/procurement_repository_impl.py

from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.application.dto.investigation_criteria import InvestigationCriteria
from backend.application.dto.procurement_record import ProcurementRecord
from backend.application.dto.search_options import SearchOptions
from backend.infrastructure.models.procurement import RupPaketDetailed


class ProcurementRepositoryImpl:
    """PostgreSQL implementation of ProcurementRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    @staticmethod
    def _safe_str(value: Optional[str]) -> str:
        """Normalize None to empty string."""
        return value or ""

    @staticmethod
    def _safe_int(value: Optional[int]) -> int:
        """Normalize None to 0."""
        return value or 0

    @staticmethod
    def _safe_float(value) -> float:
        """Normalize None to 0.0."""
        return float(value or 0)

    def _validate_options(self, options: Optional[SearchOptions]) -> None:
        """Validate pagination options."""
        if options:
            if options.limit is not None and options.limit < 0:
                raise ValueError("limit must be >= 0")
            if options.offset is not None and options.offset < 0:
                raise ValueError("offset must be >= 0")

    async def search(
        self,
        criteria: InvestigationCriteria,
        options: Optional[SearchOptions] = None,
    ) -> Sequence[ProcurementRecord]:
        """Search procurement records by criteria."""
        self._validate_options(options)
        stmt = self._build_statement(criteria, options)
        result = await self._session.execute(stmt)
        rows = result.scalars().all()
        return [self._to_record(row) for row in rows]

    def _build_statement(
        self,
        criteria: InvestigationCriteria,
        options: Optional[SearchOptions] = None,
    ):
        """Build SQLAlchemy statement with filters."""
        stmt = select(RupPaketDetailed)

        if criteria.institutions:
            stmt = stmt.where(
                RupPaketDetailed.nama_instansi.in_(criteria.institutions)
            )

        if criteria.vendors:
            stmt = stmt.where(
                RupPaketDetailed.nama_penyedia.in_(criteria.vendors)
            )

        if criteria.packages:
            stmt = stmt.where(
                RupPaketDetailed.kode_paket.in_(criteria.packages)
            )

        if criteria.years:
            stmt = stmt.where(
                RupPaketDetailed.tahun_anggaran.in_(criteria.years)
            )

        # Deterministic ordering: year, package_code, id (tie-breaker)
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
        """Explicit mapping from ORM model to DTO with null safety."""
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