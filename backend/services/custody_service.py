"""
Custody Service
Handles evidence custody chain logic
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import text

class CustodyService:
    """Service for managing evidence custody chain"""
    
    def __init__(self, db: Session, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def record_transfer(
        self,
        evidence_id: str,
        from_custodian: str,
        to_custodian: str,
        reason: str,
        transferred_by: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Record custody transfer"""
        # Validate input
        if not evidence_id:
            raise ValueError("evidence_id is required")
        if not to_custodian:
            raise ValueError("to_custodian is required")
        
        # Generate ID
        transfer_id = str(uuid.uuid4())
        
        # Close previous transfers
        query = text("""
            UPDATE custody_chain
            SET status = 'closed', updated_at = :updated_at
            WHERE evidence_id = :evidence_id AND status = 'active'
        """)
        self.db.execute(query, {
            "evidence_id": evidence_id,
            "updated_at": datetime.utcnow()
        })
        
        # Create new transfer
        query = text("""
            INSERT INTO custody_chain (
                id, evidence_id, from_custodian, to_custodian,
                reason, transferred_by, transferred_at, status, notes,
                tenant_id, created_at, updated_at
            ) VALUES (
                :id, :evidence_id, :from_custodian, :to_custodian,
                :reason, :transferred_by, :transferred_at, 'active', :notes,
                :tenant_id, :created_at, :updated_at
            )
        """)
        
        now = datetime.utcnow()
        self.db.execute(query, {
            "id": transfer_id,
            "evidence_id": evidence_id,
            "from_custodian": from_custodian,
            "to_custodian": to_custodian,
            "reason": reason,
            "transferred_by": transferred_by,
            "transferred_at": now,
            "notes": notes,
            "tenant_id": self.tenant_id,
            "created_at": now,
            "updated_at": now
        })
        
        self.db.commit()
        
        return {
            "id": transfer_id,
            "evidence_id": evidence_id,
            "from_custodian": from_custodian,
            "to_custodian": to_custodian,
            "reason": reason,
            "transferred_by": transferred_by,
            "transferred_at": now,
            "status": "active",
            "notes": notes
        }
    
    async def get_current_custodian(self, evidence_id: str) -> Optional[str]:
        """Get current custodian for evidence"""
        query = text("""
            SELECT to_custodian
            FROM custody_chain
            WHERE evidence_id = :evidence_id AND status = 'active'
            ORDER BY transferred_at DESC
            LIMIT 1
        """)
        result = self.db.execute(query, {"evidence_id": evidence_id})
        row = result.fetchone()
        return row[0] if row else None
    
    async def get_custody_history(self, evidence_id: str) -> List[Dict[str, Any]]:
        """Get complete custody history"""
        query = text("""
            SELECT 
                id,
                from_custodian,
                to_custodian,
                reason,
                transferred_by,
                transferred_at,
                status,
                notes
            FROM custody_chain
            WHERE evidence_id = :evidence_id
            ORDER BY transferred_at ASC
        """)
        result = self.db.execute(query, {"evidence_id": evidence_id})
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "from_custodian": row[1],
                "to_custodian": row[2],
                "reason": row[3],
                "transferred_by": row[4],
                "transferred_at": row[5].isoformat() if row[5] else None,
                "status": row[6],
                "notes": row[7]
            }
            for row in rows
        ]
    
    async def record_access(
        self,
        evidence_id: str,
        accessed_by: str,
        access_type: str,
        reason: Optional[str] = None,
        duration: Optional[int] = None
    ) -> Dict[str, Any]:
        """Record evidence access"""
        access_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        query = text("""
            INSERT INTO access_log (
                id, evidence_id, accessed_by, access_type,
                reason, duration, accessed_at, status,
                tenant_id, created_at
            ) VALUES (
                :id, :evidence_id, :accessed_by, :access_type,
                :reason, :duration, :accessed_at, 'recorded',
                :tenant_id, :created_at
            )
        """)
        
        self.db.execute(query, {
            "id": access_id,
            "evidence_id": evidence_id,
            "accessed_by": accessed_by,
            "access_type": access_type,
            "reason": reason,
            "duration": duration,
            "accessed_at": now,
            "tenant_id": self.tenant_id,
            "created_at": now
        })
        
        self.db.commit()
        
        return {
            "id": access_id,
            "evidence_id": evidence_id,
            "accessed_by": accessed_by,
            "access_type": access_type,
            "reason": reason,
            "duration": duration,
            "accessed_at": now,
            "status": "recorded"
        }
    
    async def get_access_history(self, evidence_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get access history"""
        query = text("""
            SELECT 
                id,
                accessed_by,
                access_type,
                reason,
                duration,
                accessed_at,
                status
            FROM access_log
            WHERE evidence_id = :evidence_id
            ORDER BY accessed_at DESC
            LIMIT :limit
        """)
        result = self.db.execute(query, {"evidence_id": evidence_id, "limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "accessed_by": row[1],
                "access_type": row[2],
                "reason": row[3],
                "duration": row[4],
                "accessed_at": row[5].isoformat() if row[5] else None,
                "status": row[6]
            }
            for row in rows
        ]