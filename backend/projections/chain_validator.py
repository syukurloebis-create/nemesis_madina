# backend/projections/chain_validator.py
import asyncio
from typing import Optional
import asyncpg
from core.events.lineage_verifier import LineageVerifier

class ChainValidator:
    """Background worker for chain integrity validation."""
    
    def __init__(self, pool: asyncpg.Pool, interval: int = 3600):
        self.pool = pool
        self.interval = interval
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        self._running = True
        self._task = asyncio.create_task(self._run())
        print("✅ Chain validator started")
    
    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            await self._task
        print("🛑 Chain validator stopped")
    
    async def _run(self):
        while self._running:
            try:
                await self._validate_all_aggregates()
                await asyncio.sleep(self.interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Chain validator error: {e}")
                await asyncio.sleep(60)
    
    async def _validate_all_aggregates(self):
        """Periodic validation of all aggregate chains."""
        async with self.pool.acquire() as conn:
            aggregates = await conn.fetch(
                "SELECT DISTINCT aggregate_id FROM event_lineage"
            )
        
        verifier = LineageVerifier(self.pool)
        broken_chains = []
        
        for agg in aggregates:
            result = await verifier.verify_aggregate_chain(agg["aggregate_id"])
            if not result["verified"]:
                broken_chains.append({
                    "aggregate_id": agg["aggregate_id"],
                    "broken_at": result["broken_at_sequence"]
                })
        
        if broken_chains:
            print(f"⚠️ Found {len(broken_chains)} broken chains!")
            # Store alert in anomalies table
            await self._store_anomaly_alert(broken_chains)
    
    async def _store_anomaly_alert(self, broken_chains: list):
        async with self.pool.acquire() as conn:
            for chain in broken_chains:
                await conn.execute(
                    """
                    INSERT INTO anomalies (entity_id, anomaly_type, severity, details, detected_at)
                    VALUES ($1, 'chain_break', 0.9, $2, NOW())
                    """,
                    chain["aggregate_id"],
                    f"Hash chain broken at sequence {chain['broken_at']}"
                )
