# backend/services/custody_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class CustodyService:
    """Service for evidence chain of custody tracking"""
    
    def __init__(self, session: AsyncSession, tenant_id: str = None):
        self.session = session
        self.tenant_id = tenant_id
    
    async def _get_next_version(self, case_id: str) -> int:
        """Get next version number for a case"""
        result = await self.session.execute(
            text("SELECT COALESCE(MAX(version), 0) + 1 FROM events WHERE case_id = :case_id"),
            {"case_id": case_id}
        )
        return result.scalar() or 1
    
    async def _get_last_event_hash(self, case_id: str) -> Optional[str]:
        """Get last event hash for chain"""
        result = await self.session.execute(
            text("SELECT event_hash FROM events WHERE case_id = :case_id ORDER BY version DESC LIMIT 1"),
            {"case_id": case_id}
        )
        row = result.fetchone()
        return row[0] if row else None
    
    async def _get_case_id_for_evidence(self, evidence_id: str) -> Optional[str]:
        """Get case_id for an evidence"""
        result = await self.session.execute(
            text("SELECT case_id FROM evidence_files WHERE id = :evidence_id"),
            {"evidence_id": evidence_id}
        )
        row = result.fetchone()
        return str(row[0]) if row else None
    
    async def record_transfer(
        self,
        evidence_id: str,
        from_custodian: str,
        to_custodian: str,
        reason: str,
        transferred_by: str
    ) -> Dict[str, Any]:
        """Record evidence custody transfer"""
        
        transfer_id = uuid.uuid4()
        timestamp = datetime.utcnow()
        
        query = text("""
            INSERT INTO custody_chain (
                id, evidence_id, from_custodian, to_custodian, 
                reason, transferred_by, transferred_at, status
            ) VALUES (
                :id, :evidence_id, :from_custodian, :to_custodian,
                :reason, :transferred_by, :transferred_at, :status
            )
        """)
        
        await self.session.execute(query, {
            "id": str(transfer_id),
            "evidence_id": evidence_id,
            "from_custodian": from_custodian,
            "to_custodian": to_custodian,
            "reason": reason,
            "transferred_by": transferred_by,
            "transferred_at": timestamp,
            "status": "COMPLETED"
        })
        
        # Get case_id for this evidence
        case_id = await self._get_case_id_for_evidence(evidence_id)
        
        if case_id:
            # Get next version
            version = await self._get_next_version(case_id)
            
            # Get previous hash for chain
            previous_hash = await self._get_last_event_hash(case_id)
            
            # Prepare event data
            event_data = {
                "evidence_id": evidence_id,
                "from_custodian": from_custodian,
                "to_custodian": to_custodian,
                "reason": reason
            }
            
            # Calculate event hash
            event_hash = hashlib.sha256(
                json.dumps({
                    "event_id": str(uuid.uuid4()),
                    "case_id": case_id,
                    "event_type": "EVIDENCE_TRANSFERRED",
                    "data": event_data,
                    "timestamp": timestamp.isoformat(),
                    "version": version
                }, sort_keys=True).encode()
            ).hexdigest()
            
            # Create audit event with hash
            event_query = text("""
                INSERT INTO events (
                    event_id, case_id, event_type, data, timestamp, version, user_id, event_hash, previous_hash
                ) VALUES (
                    :event_id, :case_id, :event_type, :data, :timestamp,
                    :version, :user_id, :event_hash, :previous_hash
                )
            """)
            
            await self.session.execute(event_query, {
                "event_id": str(uuid.uuid4()),
                "case_id": case_id,
                "event_type": "EVIDENCE_TRANSFERRED",
                "data": json.dumps(event_data),
                "timestamp": timestamp,
                "version": version,
                "user_id": transferred_by,
                "event_hash": event_hash,
                "previous_hash": previous_hash
            })
        
        await self.session.commit()
        
        return {
            "id": str(transfer_id),
            "evidence_id": evidence_id,
            "from_custodian": from_custodian,
            "to_custodian": to_custodian,
            "reason": reason,
            "transferred_at": timestamp.isoformat()
        }
    
    async def get_custody_history(self, evidence_id: str) -> List[Dict[str, Any]]:
        """Get full custody history for evidence"""
        
        query = text("""
            SELECT id, from_custodian, to_custodian, reason, 
                   transferred_by, transferred_at, status
            FROM custody_chain
            WHERE evidence_id = :evidence_id
            ORDER BY transferred_at ASC
        """)
        
        result = await self.session.execute(query, {"evidence_id": evidence_id})
        rows = result.fetchall()
        
        return [
            {
                "id": str(r[0]),
                "from_custodian": r[1],
                "to_custodian": r[2],
                "reason": r[3],
                "transferred_by": r[4],
                "transferred_at": r[5].isoformat() if r[5] else None,
                "status": r[6]
            }
            for r in rows
        ]
    
    async def get_current_custodian(self, evidence_id: str) -> Optional[str]:
        """Get current custodian of evidence"""
        
        query = text("""
            SELECT to_custodian
            FROM custody_chain
            WHERE evidence_id = :evidence_id
            ORDER BY transferred_at DESC
            LIMIT 1
        """)
        
        result = await self.session.execute(query, {"evidence_id": evidence_id})
        row = result.fetchone()
        
        return row[0] if row else None
    
    async def record_access(
        self,
        evidence_id: str,
        accessed_by: str,
        access_type: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """Record evidence access (view, download, print)"""
        
        query = text("""
            INSERT INTO evidence_access_log (
                id, evidence_id, accessed_by, access_type, reason, accessed_at
            ) VALUES (
                :id, :evidence_id, :accessed_by, :access_type, :reason, :accessed_at
            )
        """)
        
        access_id = uuid.uuid4()
        timestamp = datetime.utcnow()
        
        await self.session.execute(query, {
            "id": str(access_id),
            "evidence_id": evidence_id,
            "accessed_by": accessed_by,
            "access_type": access_type,
            "reason": reason,
            "accessed_at": timestamp
        })
        
        await self.session.commit()
        
        return {
            "id": str(access_id),
            "evidence_id": evidence_id,
            "accessed_by": accessed_by,
            "access_type": access_type,
            "accessed_at": timestamp.isoformat()
        }
    
    async def get_access_history(self, evidence_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get evidence access history"""
        
        query = text("""
            SELECT id, accessed_by, access_type, reason, accessed_at
            FROM evidence_access_log
            WHERE evidence_id = :evidence_id
            ORDER BY accessed_at DESC
            LIMIT :limit
        """)
        
        result = await self.session.execute(query, {
            "evidence_id": evidence_id,
            "limit": limit
        })
        
        rows = result.fetchall()
        
        return [
            {
                "id": str(r[0]),
                "accessed_by": r[1],
                "access_type": r[2],
                "reason": r[3],
                "accessed_at": r[4].isoformat() if r[4] else None
            }
            for r in rows
        ]