# backend/projections/replay_engine.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncpg

class ReplayEngine:
    """Event replay untuk temporal reconstruction dan snapshot rebuilding."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def replay_aggregate(self, aggregate_id: str) -> List[Dict[str, Any]]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT event_id, event_type, payload, sequence_num, 
                       schema_version, occurred_at, correlation_id, metadata
                FROM event_lineage
                WHERE aggregate_id = $1
                ORDER BY sequence_num ASC
                """,
                aggregate_id
            )
            return [dict(row) for row in rows]
    
    async def get_aggregate_info(self, aggregate_id: str) -> Dict:
        """Get aggregate summary information."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT 
                    COUNT(*) as total_events,
                    MIN(sequence_num) as first_seq,
                    MAX(sequence_num) as last_seq,
                    MIN(occurred_at) as first_event_at,
                    MAX(occurred_at) as last_event_at
                FROM event_lineage
                WHERE aggregate_id = $1
                """,
                aggregate_id
            )
            return dict(row) if row else {"total_events": 0}
    
    async def rebuild_state(self, aggregate_id: str, initial_state: dict = None) -> dict:
        events = await self.replay_aggregate(aggregate_id)
        state = initial_state or {}
        for event in events:
            event_type = event["event_type"]
            payload = event["payload"]
            if event_type == "order.created":
                state.update({
                    "order_id": payload.get("order_id"),
                    "status": "created",
                    "created_at": event["occurred_at"]
                })
            elif event_type == "order.updated":
                state.update(payload)
            elif event_type == "order.cancelled":
                state["status"] = "cancelled"
            state["last_sequence"] = event["sequence_num"]
        return state
