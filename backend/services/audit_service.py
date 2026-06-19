# backend/services/audit_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from datetime import datetime
import uuid
import json
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Service for audit logging"""
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: str,
        action: str,
        resource: str,
        resource_id: Optional[str] = None,
        details: Optional[dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        """Log user action for audit trail"""
        
        # Cek struktur tabel terlebih dahulu
        # Sesuaikan kolom dengan yang ada di database Anda
        query = text("""
            INSERT INTO audit_log (
                user_id, action, resource_id, details, timestamp
            ) VALUES (
                :user_id, :action, :resource_id, :details, :timestamp
            )
        """)
        
        await db.execute(query, {
            "user_id": user_id,
            "action": action,
            "resource_id": resource_id or resource,
            "details": json.dumps(details or {}),
            "timestamp": datetime.utcnow()
        })
        
        await db.commit()
        logger.info(f"AUDIT: {user_id} - {action} on {resource} {resource_id or ''}")