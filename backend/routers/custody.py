# backend/routers/custody.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List

from backend.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.services.custody_service import CustodyService
from backend.config import settings

router = APIRouter(prefix="/custody", tags=["custody"])


class TransferRequest(BaseModel):
    from_custodian: str
    to_custodian: str
    reason: str


class AccessRecordRequest(BaseModel):
    access_type: str  # view, download, print
    reason: Optional[str] = None


@router.post("/{evidence_id}/transfer")
async def record_transfer(
    evidence_id: str,
    request: TransferRequest,
    db: AsyncSession = Depends(get_db),
    transferred_by: str = "admin"
):
    """Record evidence custody transfer"""
    service = CustodyService(db, settings.DEFAULT_TENANT_ID)
    
    try:
        result = await service.record_transfer(
            evidence_id=evidence_id,
            from_custodian=request.from_custodian,
            to_custodian=request.to_custodian,
            reason=request.reason,
            transferred_by=transferred_by
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{evidence_id}/history")
async def get_custody_history(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get custody history for evidence"""
    service = CustodyService(db, settings.DEFAULT_TENANT_ID)
    
    history = await service.get_custody_history(evidence_id)
    return {"evidence_id": evidence_id, "history": history, "count": len(history)}


@router.get("/{evidence_id}/current")
async def get_current_custodian(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get current custodian"""
    service = CustodyService(db, settings.DEFAULT_TENANT_ID)
    
    custodian = await service.get_current_custodian(evidence_id)
    return {"evidence_id": evidence_id, "current_custodian": custodian}


@router.post("/{evidence_id}/access")
async def record_access(
    evidence_id: str,
    request: AccessRecordRequest,
    db: AsyncSession = Depends(get_db),
    accessed_by: str = "admin"
):
    """Record evidence access"""
    service = CustodyService(db, settings.DEFAULT_TENANT_ID)
    
    result = await service.record_access(
        evidence_id=evidence_id,
        accessed_by=accessed_by,
        access_type=request.access_type,
        reason=request.reason
    )
    return result


@router.get("/{evidence_id}/access")
async def get_access_history(
    evidence_id: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get evidence access history"""
    service = CustodyService(db, settings.DEFAULT_TENANT_ID)
    
    history = await service.get_access_history(evidence_id, limit)
    return {"evidence_id": evidence_id, "access_log": history, "count": len(history)}


@router.get("/evidence/{evidence_id}/custody")
async def get_evidence_custody(
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get custody information for evidence"""
    from sqlalchemy import text
    
    try:
        # Get current custodian
        query = text("""
            SELECT to_custodian, transferred_at
            FROM custody_chain
            WHERE evidence_id = :evidence_id
            ORDER BY transferred_at DESC
            LIMIT 1
        """)
        
        result = await db.execute(query, {"evidence_id": evidence_id})
        current = result.fetchone()
        
        # Get full history
        query = text("""
            SELECT id, from_custodian, to_custodian, reason, transferred_by, transferred_at, status
            FROM custody_chain
            WHERE evidence_id = :evidence_id
            ORDER BY transferred_at ASC
        """)
        
        result = await db.execute(query, {"evidence_id": evidence_id})
        history = result.fetchall()
        
        history_list = []
        for row in history:
            history_list.append({
                "id": str(row[0]),
                "from_custodian": row[1],
                "to_custodian": row[2],
                "reason": row[3],
                "transferred_by": row[4],
                "transferred_at": row[5].isoformat() if row[5] else None,
                "status": row[6]
            })
        
        return {
            "evidence_id": evidence_id,
            "current_custodian": current[0] if current else None,
            "last_transfer_at": current[1].isoformat() if current and current[1] else None,
            "history": history_list,
            "total_transfers": len(history_list)
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "evidence_id": evidence_id,
            "current_custodian": None,
            "history": [],
            "total_transfers": 0
        }