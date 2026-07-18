"""
Finding Repository - SEDERHANA

Hanya menggunakan model yang tersedia (Finding dari evidence.models.py).
Tidak bergantung pada model FindingEvent, FindingDecision, dll.
"""

from typing import List, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.evidence.models import Finding

from backend.dto.finding_dto import (
    FindingDTO,
    TimelineEventDTO,
    EvidenceDTO,
    DecisionDTO,
    ActionLogDTO,
    SLADTO
)
from backend.mapper.orm_mapper import OrmMapper


class FindingRepository:
    """
    Repository sederhana untuk Finding.

    HANYA menggunakan model yang tersedia di backend.evidence.models.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_findings_by_case(self, case_id: str) -> List[FindingDTO]:
        """Get all findings untuk sebuah case -> DTO."""
        result = await self.db.execute(
            select(Finding)
            .where(Finding.case_id == case_id)
            .order_by(Finding.created_at.desc())
        )
        findings = result.scalars().all()
        return OrmMapper.to_dto_list(findings, FindingDTO)

    # ============================================================
    # Method lain DIKEMBALIKAN KOSONG (belum tersedia di branch ini)
    # ============================================================

    async def get_evidence_batch(self, finding_ids: List[str]) -> Dict[str, List[EvidenceDTO]]:
        """SEMENTARA: Evidence batch - belum diimplementasikan."""
        return {}

    async def get_timeline_batch(self, finding_ids: List[str]) -> Dict[str, List[TimelineEventDTO]]:
        """SEMENTARA: Timeline events - belum tersedia."""
        return {}

    async def get_decision_batch(self, finding_ids: List[str]) -> Dict[str, Optional[DecisionDTO]]:
        """SEMENTARA: Decisions - belum tersedia."""
        return {}

    async def get_actions_batch(self, finding_ids: List[str]) -> Dict[str, List[ActionLogDTO]]:
        """SEMENTARA: Action logs - belum tersedia."""
        return {}

    async def get_sla_batch(self, finding_ids: List[str]) -> Dict[str, List[SLADTO]]:
        """SEMENTARA: SLA events - belum tersedia."""
        return {}