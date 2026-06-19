"""Evidence Repository - Database operations"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
import json

from backend.evidence.models import Evidence, EvidenceStatus


class EvidenceRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create(self, evidence: Evidence) -> Evidence:
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO evidence_store (
                    evidence_id, sha256_hash, filename, mime_type, file_size,
                    source_system, source_type, source_uri, uploaded_by,
                    uploaded_at, verified_at, verified_by, is_verified, status, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
            """,
                evidence.evidence_id,
                evidence.sha256_hash,
                evidence.filename,
                evidence.mime_type,
                evidence.file_size,
                evidence.source_system.value if hasattr(evidence.source_system, 'value') else evidence.source_system,
                evidence.source_type.value if hasattr(evidence.source_type, 'value') else evidence.source_type,
                evidence.source_uri,
                evidence.uploaded_by,
                evidence.uploaded_at,
                evidence.verified_at,
                evidence.verified_by,
                evidence.is_verified,
                evidence.status.value if hasattr(evidence.status, 'value') else evidence.status,
                json.dumps(evidence.metadata)
            )
            return evidence
    
    async def get_by_id(self, evidence_id: UUID) -> Optional[Evidence]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM evidence_store WHERE evidence_id = $1",
                evidence_id
            )
            if row:
                return self._row_to_evidence(row)
            return None
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Evidence]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM evidence_store ORDER BY uploaded_at DESC LIMIT $1 OFFSET $2",
                limit, offset
            )
            return [self._row_to_evidence(row) for row in rows]
    
    def _row_to_evidence(self, row) -> Evidence:
        return Evidence(
            evidence_id=row['evidence_id'],
            sha256_hash=row['sha256_hash'],
            filename=row['filename'],
            mime_type=row['mime_type'],
            file_size=row['file_size'],
            source_system=row['source_system'],
            source_type=row['source_type'],
            source_uri=row['source_uri'],
            uploaded_by=row['uploaded_by'],
            uploaded_at=row['uploaded_at'],
            verified_at=row['verified_at'],
            verified_by=row['verified_by'],
            is_verified=row['is_verified'],
            status=row['status'],
            metadata=row['metadata'] or {}
        )
