"""Chain of Custody Repository"""

import asyncpg
from typing import List, Optional
from uuid import UUID
from datetime import datetime
import json

from .models import CustodyRecord, CustodyAction


class CustodyRepository:
    """Repository for chain of custody operations"""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def add_record(self, record: CustodyRecord) -> CustodyRecord:
        """Add custody record"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO evidence_custody (
                    custody_id, evidence_id, action, actor, timestamp,
                    hash_before, hash_after, ip_address, reason, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
                record.custody_id,
                record.evidence_id,
                record.action.value if hasattr(record.action, 'value') else record.action,
                record.actor,
                record.timestamp,
                record.hash_before,
                record.hash_after,
                record.ip_address,
                record.reason,
                json.dumps(record.metadata)
            )
            return record
    
    async def get_chain(self, evidence_id: UUID) -> List[CustodyRecord]:
        """Get full custody chain for evidence"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT * FROM evidence_custody 
                WHERE evidence_id = $1 
                ORDER BY timestamp ASC
            """, evidence_id)
            return [self._row_to_record(row) for row in rows]
    
    async def get_latest(self, evidence_id: UUID) -> Optional[CustodyRecord]:
        """Get latest custody record"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM evidence_custody 
                WHERE evidence_id = $1 
                ORDER BY timestamp DESC 
                LIMIT 1
            """, evidence_id)
            return self._row_to_record(row) if row else None
    
    def _row_to_record(self, row) -> CustodyRecord:
        return CustodyRecord(
            custody_id=row['custody_id'],
            evidence_id=row['evidence_id'],
            action=row['action'],
            actor=row['actor'],
            timestamp=row['timestamp'],
            hash_before=row['hash_before'],
            hash_after=row['hash_after'],
            ip_address=row['ip_address'],
            reason=row['reason'],
            metadata=row['metadata'] or {}
        )
