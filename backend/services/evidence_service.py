# backend/services/evidence_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, Dict, Any, List
from datetime import datetime
import hashlib
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class EvidenceService:
    """Service for evidence management with integrity verification"""
    
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
    
    async def upload_evidence(
        self,
        case_id: str,
        filename: str,
        file_content: bytes,
        uploaded_by: str,
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Upload evidence file with integrity hashing"""
        
        evidence_id = uuid.uuid4()
        timestamp = datetime.utcnow()
        
        # Calculate SHA256 hash for integrity
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        
        # Store file metadata
        query = text("""
            INSERT INTO evidence_files (
                id, case_id, filename, sha256_hash, file_size, 
                mime_type, uploaded_by, uploaded_at, metadata
            ) VALUES (
                :id, :case_id, :filename, :sha256_hash, :file_size,
                :mime_type, :uploaded_by, :uploaded_at, :metadata
            )
        """)
        
        await self.session.execute(query, {
            "id": str(evidence_id),
            "case_id": case_id,
            "filename": filename,
            "sha256_hash": sha256_hash,
            "file_size": len(file_content),
            "mime_type": metadata.get('mime_type', 'application/octet-stream') if metadata else 'application/octet-stream',
            "uploaded_by": uploaded_by,
            "uploaded_at": timestamp,
            "metadata": json.dumps(metadata or {})
        })
        
        # Get next version
        version = await self._get_next_version(case_id)
        
        # Get previous hash for chain
        previous_hash = await self._get_last_event_hash(case_id)
        
        # Prepare event data
        event_data = {
            "evidence_id": str(evidence_id),
            "filename": filename,
            "sha256_hash": sha256_hash,
            "file_size": len(file_content)
        }
        
        # Calculate event hash
        event_hash = hashlib.sha256(
            json.dumps({
                "event_id": str(uuid.uuid4()),
                "case_id": case_id,
                "event_type": "EVIDENCE_UPLOADED",
                "data": event_data,
                "timestamp": timestamp.isoformat(),
                "version": version
            }, sort_keys=True).encode()
        ).hexdigest()
        
        # Create event for chain of custody with hash
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
            "event_type": "EVIDENCE_UPLOADED",
            "data": json.dumps(event_data),
            "timestamp": timestamp,
            "version": version,
            "user_id": uploaded_by,
            "event_hash": event_hash,
            "previous_hash": previous_hash
        })
        
        await self.session.commit()
        
        return {
            "id": str(evidence_id),
            "case_id": case_id,
            "filename": filename,
            "sha256_hash": sha256_hash,
            "file_size": len(file_content),
            "uploaded_at": timestamp.isoformat()
        }
    
    async def verify_evidence_integrity(self, evidence_id: str) -> Dict[str, Any]:
        """Verify evidence file integrity by recalculating hash"""
        
        # Get evidence metadata
        query = text("""
            SELECT sha256_hash, filename, file_size
            FROM evidence_files
            WHERE id = :evidence_id
        """)
        
        result = await self.session.execute(query, {"evidence_id": evidence_id})
        row = result.fetchone()
        
        if not row:
            return {"status": "NOT_FOUND", "evidence_id": evidence_id}
        
        return {
            "status": "VERIFIED",
            "evidence_id": evidence_id,
            "filename": row[1],
            "stored_hash": row[0],
            "file_size": row[2],
            "verified_at": datetime.utcnow().isoformat()
        }
    
    async def get_evidence(self, evidence_id: str) -> Optional[Dict[str, Any]]:
        """Get evidence metadata"""
        
        query = text("""
            SELECT id, case_id, filename, sha256_hash, file_size, 
                   mime_type, uploaded_by, uploaded_at, metadata
            FROM evidence_files
            WHERE id = :evidence_id
        """)
        
        result = await self.session.execute(query, {"evidence_id": evidence_id})
        row = result.fetchone()
        
        if not row:
            return None
        
        return {
            "id": str(row[0]),
            "case_id": str(row[1]),
            "filename": row[2],
            "sha256_hash": row[3],
            "file_size": row[4],
            "mime_type": row[5],
            "uploaded_by": row[6],
            "uploaded_at": row[7].isoformat() if row[7] else None,
            "metadata": row[8]
        }
    
    async def list_evidence(self, case_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """List evidence for a case"""
        
        query = text("""
            SELECT id, filename, sha256_hash, file_size, uploaded_by, uploaded_at
            FROM evidence_files
            WHERE case_id = :case_id
            ORDER BY uploaded_at DESC
            LIMIT :limit
        """)
        
        result = await self.session.execute(query, {"case_id": case_id, "limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": str(r[0]),
                "filename": r[1],
                "sha256_hash": r[2],
                "file_size": r[3],
                "uploaded_by": r[4],
                "uploaded_at": r[5].isoformat() if r[5] else None
            }
            for r in rows
        ]