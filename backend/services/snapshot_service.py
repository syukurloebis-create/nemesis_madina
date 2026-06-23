"""
Snapshot Service - CACHE ONLY
Snapshot adalah cache dari replay result, BUKAN source of truth.
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from services.replay_service import ReplayService
from snapshot.models import Snapshot


class SnapshotService:
    """
    Snapshot as CACHE, NOT source of truth.
    - Store pre-computed replay results
    - Speed up repeated queries
    - Can be rebuilt anytime from events
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.replay_service = ReplayService(db)
    
    async def get_or_create(self, case_id: str, version: int) -> Dict[str, Any]:
        """
        Get snapshot from cache, or create from replay if not exists.
        """
        # Try to get from cache
        stmt = select(Snapshot).where(
            Snapshot.case_id == case_id,
            Snapshot.version == version
        )
        result = await self.db.execute(stmt)
        snapshot = result.scalar_one_or_none()
        
        if snapshot:
            return {
                "state": json.loads(snapshot.state) if isinstance(snapshot.state, str) else snapshot.state,
                "version": snapshot.version,
                "from_cache": True
            }
        
        # Create from replay (source of truth)
        state = await self.replay_service.get_state_at_version(case_id, version)
        
        # Save to cache
        new_snapshot = Snapshot(
            case_id=case_id,
            version=version,
            state=json.dumps(state),
            created_at=datetime.utcnow()
        )
        self.db.add(new_snapshot)
        await self.db.commit()
        
        return {
            "state": state,
            "version": version,
            "from_cache": False
        }
    
    async def rebuild_snapshot(self, case_id: str, version: int) -> Dict[str, Any]:
        """Force rebuild snapshot from events (bypass cache)"""
        state = await self.replay_service.get_state_at_version(case_id, version)
        
        # Update or create
        stmt = select(Snapshot).where(
            Snapshot.case_id == case_id,
            Snapshot.version == version
        )
        result = await self.db.execute(stmt)
        snapshot = result.scalar_one_or_none()
        
        if snapshot:
            snapshot.state = json.dumps(state)
            snapshot.updated_at = datetime.utcnow()
        else:
            snapshot = Snapshot(
                case_id=case_id,
                version=version,
                state=json.dumps(state),
                created_at=datetime.utcnow()
            )
            self.db.add(snapshot)
        
        await self.db.commit()
        
        return {
            "state": state,
            "version": version,
            "from_cache": False,
            "rebuilt": True
        }
    
    async def invalidate(self, case_id: str, version: Optional[int] = None):
        """Invalidate snapshot cache"""
        if version:
            await self.db.execute(
                text("DELETE FROM snapshots WHERE case_id = :case_id AND version = :version"),
                {"case_id": case_id, "version": version}
            )
        else:
            await self.db.execute(
                text("DELETE FROM snapshots WHERE case_id = :case_id"),
                {"case_id": case_id}
            )
        await self.db.commit()
