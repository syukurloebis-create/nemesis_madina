"""Investigation Case Service - Simplified"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

from backend.investigation.models import (
    InvestigationCase, InvestigationCaseCreate, Finding, FindingCreate,
    CaseStatus
)
from backend.investigation.repositories.case_repo import InvestigationCaseRepository, FindingRepository


class InvestigationCaseService:
    def __init__(self, case_repo: InvestigationCaseRepository, finding_repo: FindingRepository):
        self.case_repo = case_repo
        self.finding_repo = finding_repo
    
    async def create_case(self, case_data: InvestigationCaseCreate) -> InvestigationCase:
        case = InvestigationCase(
            title=case_data.title,
            description=case_data.description,
            priority=case_data.priority,
            assigned_to=case_data.assigned_to,
            evidence_ids=case_data.evidence_ids,
            metadata=case_data.metadata
        )
        return await self.case_repo.create(case)
    
    async def get_case(self, case_id: UUID) -> Optional[InvestigationCase]:
        return await self.case_repo.get_by_id(case_id)
    
    async def add_finding(self, finding_data: FindingCreate) -> Optional[Finding]:
        finding = Finding(
            case_id=finding_data.case_id,
            title=finding_data.title,
            description=finding_data.description,
            severity=finding_data.severity,
            evidence_ids=finding_data.evidence_ids,
            trace_ids=finding_data.trace_ids,
            recommendation=finding_data.recommendation
        )
        return await self.finding_repo.create(finding)
    
    async def get_case_findings(self, case_id: UUID) -> List[Finding]:
        return await self.finding_repo.get_by_case(case_id)
    
    async def list_cases(self, limit: int = 100, offset: int = 0) -> List[InvestigationCase]:
        return await self.case_repo.list_cases(limit, offset)
    
    async def get_statistics(self) -> Dict[str, Any]:
        cases = await self.case_repo.list_cases(limit=1000)
        return {
            "total_cases": len(cases),
            "by_status": {},
            "by_priority": {}
        }
