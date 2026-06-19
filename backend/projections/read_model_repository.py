# backend/projections/read_model_repository.py
import asyncpg
from typing import List, Dict, Any, Optional

class ReadModelRepository:
    """Repository untuk query read model (CQRS)."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def get_entity_trust(self, entity_id: str) -> Optional[Dict]:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT entity_id, trust_score, last_update FROM entity_trust_summary WHERE entity_id = $1",
                entity_id
            )
            return dict(row) if row else None
    
    async def list_high_risk_entities(self, limit: int = 20) -> List[Dict]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT entity_id, trust_score, last_update
                FROM entity_trust_summary
                ORDER BY trust_score ASC
                LIMIT $1
                """,
                limit
            )
            return [dict(row) for row in rows]
