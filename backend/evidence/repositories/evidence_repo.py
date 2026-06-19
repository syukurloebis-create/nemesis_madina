"""Evidence Repository - Database operations for evidence"""

import asyncpg
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import json

from backend.evidence.models import Evidence, EvidenceStatus, SourceSystem, EvidenceType


class EvidenceRepository:
    """Repository for evidence operations"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create(self, evidence: Evidence) -> Evidence:
        """Create new evidence record"""
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
        """Get evidence by ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM evidence_store WHERE evidence_id = $1",
                evidence_id
            )
            if row:
                return self._row_to_evidence(row)
            return None
    
    async def update_status(self, evidence_id: UUID, status: EvidenceStatus) -> Optional[Evidence]:
        """Update evidence status"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                UPDATE evidence_store 
                SET status = $2, updated_at = NOW()
                WHERE evidence_id = $1
                RETURNING *
            """, evidence_id, status.value if hasattr(status, 'value') else status)
            return self._row_to_evidence(row) if row else None
    
    async def mark_verified(self, evidence_id: UUID, verified_by: str, is_valid: bool) -> Optional[Evidence]:
        """Mark evidence as verified"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                UPDATE evidence_store 
                SET is_verified = $2, verified_at = NOW(), verified_by = $3, status = $4
                WHERE evidence_id = $1
                RETURNING *
            """, evidence_id, is_valid, verified_by, 
                EvidenceStatus.VERIFIED.value if is_valid else EvidenceStatus.INVALID.value)
            return self._row_to_evidence(row) if row else None
    
    async def list_evidence(
        self,
        limit: int = 100,
        offset: int = 0,
        source_system: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Evidence]:
        """List evidence with filters"""
        query = "SELECT * FROM evidence_store WHERE 1=1"
        params = []
        param_index = 1
        
        if source_system:
            query += f" AND source_system = ${param_index}"
            params.append(source_system)
            param_index += 1
        
        if status:
            query += f" AND status = ${param_index}"
            params.append(status)
            param_index += 1
        
        query += f" ORDER BY uploaded_at DESC LIMIT ${param_index} OFFSET ${param_index + 1}"
        params.extend([limit, offset])
        
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
            return [self._row_to_evidence(row) for row in rows]
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get evidence statistics"""
        async with self.pool.acquire() as conn:
            total = await conn.fetchval("SELECT COUNT(*) FROM evidence_store")
            verified = await conn.fetchval("SELECT COUNT(*) FROM evidence_store WHERE is_verified = true")
            by_status = await conn.fetch("""
                SELECT status, COUNT(*) FROM evidence_store GROUP BY status
            """)
            by_source = await conn.fetch("""
                SELECT source_system, COUNT(*) FROM evidence_store GROUP BY source_system
            """)
            
            return {
                "total_evidence": total,
                "verified_evidence": verified,
                "verification_rate": round(verified / total * 100, 2) if total > 0 else 0,
                "by_status": {row['status']: row['count'] for row in by_status},
                "by_source": {row['source_system']: row['count'] for row in by_source}
            }
    
    def _row_to_evidence(self, row) -> Evidence:
        """Convert database row to Evidence model"""
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
