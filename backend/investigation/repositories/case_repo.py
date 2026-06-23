"""Investigation Case Repository - Updated to match schema"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
import json
from datetime import datetime

from investigation.models import (
    InvestigationCase, Finding, CaseStatus
)


class InvestigationCaseRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create(self, case: InvestigationCase) -> InvestigationCase:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO investigation_case (
                    case_id, title, description, status, priority,
                    assigned_to, evidence_ids, findings, timeline,
                    created_at, updated_at, metadata, risk_level
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
            """,
                case.case_id,
                case.title,
                case.description,
                case.status.value,
                case.priority.value,
                case.assigned_to,
                [str(eid) for eid in case.evidence_ids],
                json.dumps([f.dict() for f in case.findings]),
                json.dumps(case.timeline),
                case.created_at,
                case.updated_at,
                json.dumps(case.metadata),
                case.risk_level
            )
            return case
    
    async def get_by_id(self, case_id: UUID) -> Optional[InvestigationCase]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM investigation_case WHERE case_id = $1",
                case_id
            )
            if row:
                return self._row_to_case(row)
            return None
    
    async def list_cases(self, limit: int = 100, offset: int = 0) -> List[InvestigationCase]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM investigation_case ORDER BY created_at DESC LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [self._row_to_case(row) for row in rows]
    
    def _row_to_case(self, row) -> InvestigationCase:
        findings_data = json.loads(row['findings']) if row['findings'] else []
        findings = [Finding(**f) for f in findings_data]
        
        return InvestigationCase(
            case_id=row['case_id'],
            case_number=row['case_number'],
            title=row['title'],
            description=row['description'],
            status=row['status'],
            priority=row['priority'],
            risk_level=row['risk_level'],
            assigned_to=row['assigned_to'],
            evidence_ids=[UUID(eid) for eid in row['evidence_ids']] if row['evidence_ids'] else [],
            findings=findings,
            timeline=json.loads(row['timeline']) if row['timeline'] else [],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            closed_at=row['closed_at'],
            metadata=row['metadata'] or {}
        )


class FindingRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create(self, finding: Finding) -> Finding:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO finding (
                    finding_id, case_id, title, description, severity, status,
                    evidence_ids, trace_ids, recommendation, response,
                    created_at, updated_at, resolved_at, resolved_by
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
            """,
                finding.finding_id,
                finding.case_id,
                finding.title,
                finding.description,
                finding.severity.value,
                finding.status.value,
                [str(eid) for eid in finding.evidence_ids],
                [str(tid) for tid in finding.trace_ids],
                finding.recommendation,
                finding.response,
                finding.created_at,
                finding.updated_at,
                finding.resolved_at,
                finding.resolved_by
            )
            return finding
    
    async def get_by_case(self, case_id: UUID) -> List[Finding]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM finding WHERE case_id = $1 ORDER BY created_at DESC",
                case_id
            )
            return [self._row_to_finding(row) for row in rows]
    
    def _row_to_finding(self, row) -> Finding:
        return Finding(
            finding_id=row['finding_id'],
            finding_number=row['finding_number'],
            case_id=row['case_id'],
            title=row['title'],
            description=row['description'],
            severity=row['severity'],
            status=row['status'],
            evidence_ids=[UUID(eid) for eid in row['evidence_ids']] if row['evidence_ids'] else [],
            trace_ids=[UUID(tid) for tid in row['trace_ids']] if row['trace_ids'] else [],
            recommendation=row['recommendation'],
            response=row['response'],
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            resolved_at=row['resolved_at'],
            resolved_by=row['resolved_by']
        )
