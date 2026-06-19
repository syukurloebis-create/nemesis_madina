# backend/projections/dlq_repository.py
import asyncpg
from typing import List, Dict, Any, Optional
from datetime import datetime

class DLQRepository:
    """Repository untuk Dead Letter Queue management."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def add_failed_event(self, event_id: str, aggregate_id: str, 
                                event_type: str, payload: dict, error: str) -> None:
        """Add failed event to DLQ."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO dead_letter_queue (event_id, aggregate_id, event_type, payload, error_message)
                VALUES ($1, $2, $3, $4, $5)
                """,
                event_id, aggregate_id, event_type, json.dumps(payload), error
            )
    
    async def list_unresolved(self, limit: int = 100) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, event_id, aggregate_id, event_type, error_message, failed_at
                FROM dead_letter_queue
                WHERE is_resolved = FALSE
                ORDER BY failed_at ASC
                LIMIT $1
                """,
                limit
            )
            return [dict(row) for row in rows]
    
    async def mark_resolved(self, dlq_id: str) -> bool:
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE dead_letter_queue 
                SET is_resolved = TRUE, resolved_at = NOW()
                WHERE id = $1 AND is_resolved = FALSE
                """,
                dlq_id
            )
            return "UPDATE 1" in result
