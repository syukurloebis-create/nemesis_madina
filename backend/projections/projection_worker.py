# backend/projections/projection_worker.py
import asyncio
import json
from typing import Optional
import asyncpg

class ProjectionWorker:
    """Background worker untuk materialized view dan read model."""
    
    def __init__(self, pool: asyncpg.Pool, interval: int = 60):
        self.pool = pool
        self.interval = interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run())
        print("✅ Projection worker started")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            await self._task
        print("🛑 Projection worker stopped")
    
    async def _run(self):
        while self._running:
            try:
                await self._refresh_materialized_views()
                await self._update_read_models()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Projection worker error: {e}")
                await asyncio.sleep(5)
    
    async def _refresh_materialized_views(self):
        """Refresh materialized views di PostgreSQL."""
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY entity_latest_trust")
                print("✅ Materialized view refreshed")
            except Exception as e:
                print(f"⚠️ Materialized view refresh failed: {e}")
    
    async def _update_read_models(self):
        """Update read model tables."""
        async with self.pool.acquire() as conn:
            # Update entity trust summary
            await conn.execute("""
                INSERT INTO entity_trust_summary (entity_id, trust_score, last_update)
                SELECT aggregate_id, (payload->>'trust_score')::float, MAX(occurred_at)
                FROM event_lineage
                WHERE event_type IN ('entity.registered', 'trust.updated')
                GROUP BY aggregate_id, (payload->>'trust_score')::float
                ON CONFLICT (entity_id) DO UPDATE SET
                    trust_score = EXCLUDED.trust_score,
                    last_update = EXCLUDED.last_update
            """)
