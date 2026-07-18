"""
NEMESIS Madina - Outbox Health Check
✅ Health endpoints for publisher
✅ Metrics for monitoring
"""

from typing import Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from backend.infrastructure.outbox.outbox import OutboxStatus


class OutboxHealthCheck:
    """Health check for outbox system."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def check(self) -> Dict[str, Any]:
        """Check health of outbox system."""
        # Count pending entries
        pending = await self._session.execute(
            select(func.count()).where(OutboxModel.status == OutboxStatus.PENDING)
        )
        
        # Count failed entries (stale > 1 hour)
        stale = await self._session.execute(
            select(func.count())
            .where(OutboxModel.status == OutboxStatus.FAILED)
            .where(OutboxModel.updated_at < datetime.now() - timedelta(hours=1))
        )
        
        # Count DLQ entries
        dlq = await self._session.execute(select(func.count()).select_from(DeadLetterModel))
        
        return {
            "status": "healthy" if pending.scalar() < 1000 else "degraded",
            "pending_count": pending.scalar(),
            "stale_failed_count": stale.scalar(),
            "dlq_count": dlq.scalar(),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }