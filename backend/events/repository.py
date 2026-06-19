# backend/events/repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional  # ← TAMBAHKAN IMPORT INI
from datetime import datetime
import uuid
import json
import hashlib
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class EventRepository:
    def __init__(self, session: AsyncSession, tenant_id: str = None):
        self.session = session
        self.tenant_id = tenant_id or settings.DEFAULT_TENANT_ID
    
    async def append(
        self,
        aggregate_id: str,
        aggregate_type: str,
        event_type: str,
        payload: Dict[str, Any],
        metadata: Dict[str, Any],
        created_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Append event to event store"""
        
        event_uuid = uuid.uuid4()
        timestamp = datetime.utcnow()
        
        # Get next version for this case
        version = await self._get_next_version(aggregate_id)
        
        # Calculate event hash
        event_hash = self._calculate_event_hash(
            event_uuid=event_uuid,
            case_id=aggregate_id,
            event_type=event_type,
            data=payload,
            timestamp=timestamp,
            version=version
        )
        
        # Get previous event for hash chain
        previous = await self._get_last_event(aggregate_id)
        previous_hash = previous.get('event_hash') if previous else None
        
        # Insert event
        query = text("""
            INSERT INTO events (
                event_id, case_id, event_type, data, timestamp, version, 
                user_id, event_hash, previous_hash, created_at
            ) VALUES (
                :event_id, :case_id, :event_type, :data, :timestamp, :version,
                :user_id, :event_hash, :previous_hash, :created_at
            )
            RETURNING id, commit_position
        """)
        
        result = await self.session.execute(query, {
            "event_id": event_uuid,
            "case_id": aggregate_id,
            "event_type": event_type,
            "data": json.dumps(payload),
            "timestamp": timestamp,
            "version": version,
            "user_id": created_by or metadata.get("actor_id", "system"),
            "event_hash": event_hash,
            "previous_hash": previous_hash,
            "created_at": timestamp
        })
        
        row = result.fetchone()
        await self.session.commit()
        
        if row:
            if hasattr(row, '_mapping'):
                row_dict = dict(row._mapping)
            else:
                row_dict = dict(zip(row.keys(), row))
            
            return {
                "id": row_dict.get('id'),
                "event_id": str(event_uuid),
                "case_id": aggregate_id,
                "event_type": event_type,
                "data": payload,
                "timestamp": timestamp.isoformat(),
                "version": version,
                "event_hash": event_hash,
                "previous_hash": previous_hash,
                "commit_position": row_dict.get('commit_position')
            }
        
        return {}
    
    async def get_events(
        self,
        aggregate_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get events for a case"""
        query = text("""
            SELECT 
                id, event_id, case_id, event_type, data, timestamp, version,
                user_id, event_hash, previous_hash, commit_position, created_at
            FROM events
            WHERE case_id = :case_id
            ORDER BY version ASC
            LIMIT :limit
        """)
        
        result = await self.session.execute(query, {
            "case_id": aggregate_id,
            "limit": limit
        })
        
        events = []
        for row in result.fetchall():
            if hasattr(row, '_mapping'):
                row_dict = dict(row._mapping)
            else:
                row_dict = dict(zip(row.keys(), row))
            
            events.append({
                "id": row_dict.get('id'),
                "event_id": str(row_dict.get('event_id')) if row_dict.get('event_id') else None,
                "case_id": str(row_dict.get('case_id')) if row_dict.get('case_id') else None,
                "event_type": row_dict.get('event_type'),
                "data": row_dict.get('data'),
                "timestamp": row_dict.get('timestamp').isoformat() if row_dict.get('timestamp') else None,
                "version": row_dict.get('version'),
                "user_id": row_dict.get('user_id'),
                "event_hash": row_dict.get('event_hash'),
                "previous_hash": row_dict.get('previous_hash'),
                "commit_position": row_dict.get('commit_position'),
                "created_at": row_dict.get('created_at').isoformat() if row_dict.get('created_at') else None
            })
        
        return events
    
    async def get_total_event_count(self) -> int:
        """Get total number of events"""
        result = await self.session.execute(text("SELECT COUNT(*) FROM events"))
        return result.scalar()
    
    async def _get_next_version(self, case_id: str) -> int:
        """Get next version number for a case"""
        query = text("SELECT COALESCE(MAX(version), 0) + 1 FROM events WHERE case_id = :case_id")
        result = await self.session.execute(query, {"case_id": case_id})
        val = result.scalar()
        return val if val else 1
    
    async def _get_last_event(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get last event for a case"""
        query = text("""
            SELECT id, event_id, case_id, event_type, data, timestamp, version, 
                   user_id, created_at, event_hash, previous_hash, commit_position
            FROM events 
            WHERE case_id = :case_id 
            ORDER BY version DESC 
            LIMIT 1
        """)
        
        result = await self.session.execute(query, {"case_id": case_id})
        row = result.fetchone()
        
        if row:
            if hasattr(row, '_mapping'):
                row_dict = dict(row._mapping)
            else:
                row_dict = dict(zip(row.keys(), row))
            
            return {
                "id": row_dict.get('id'),
                "event_id": str(row_dict.get('event_id')) if row_dict.get('event_id') else None,
                "case_id": str(row_dict.get('case_id')) if row_dict.get('case_id') else None,
                "event_type": row_dict.get('event_type'),
                "data": row_dict.get('data'),
                "timestamp": row_dict.get('timestamp'),
                "version": row_dict.get('version'),
                "user_id": row_dict.get('user_id'),
                "event_hash": row_dict.get('event_hash'),
                "previous_hash": row_dict.get('previous_hash'),
                "commit_position": row_dict.get('commit_position')
            }
        return None
    
    def _calculate_event_hash(
        self,
        event_uuid: uuid.UUID,
        case_id: str,
        event_type: str,
        data: dict,
        timestamp: datetime,
        version: int
    ) -> str:
        """Calculate event hash for integrity verification"""
        # Gunakan format yang sama dengan database
        block = {
            "event_id": str(event_uuid),
            "case_id": str(case_id),
            "event_type": event_type,
            "data": data,
            "timestamp": timestamp.isoformat(),  # ← PASTIKAN FORMAT SAMA
            "version": version
        }
        # Gunakan sort_keys=True untuk konsistensi
        canonical = json.dumps(block, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(canonical.encode()).hexdigest()