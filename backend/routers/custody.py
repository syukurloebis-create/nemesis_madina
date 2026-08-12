"""
Custody Router - Tenant-Aware, Async
"""
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from backend.database import get_db
from backend.services.custody_service import CustodyService
from backend.config import settings

router = APIRouter(prefix="/custody", tags=["custody"])


# ============================================================
# PYDANTIC MODELS
# ============================================================

class TransferRequest(BaseModel):
    from_custodian: str = Field(..., description="Current custodian")
    to_custodian: str = Field(..., description="New custodian")
    reason: str = Field(..., description="Reason for transfer")
    notes: Optional[str] = Field(None, description="Additional notes")


class TransferResponse(BaseModel):
    id: str
    evidence_id: str
    from_custodian: str
    to_custodian: str
    reason: str
    transferred_by: str
    transferred_at: datetime
    status: str
    notes: Optional[str] = None


class AccessRecordRequest(BaseModel):
    access_type: str = Field(..., description="Type of access: view, download, print, edit")
    reason: Optional[str] = Field(None, description="Reason for access")
    duration: Optional[int] = Field(None, description="Access duration in minutes")


class AccessRecordResponse(BaseModel):
    id: str
    evidence_id: str
    accessed_by: str
    access_type: str
    reason: Optional[str]
    accessed_at: datetime
    duration: Optional[int]
    status: str


class CustodyHistoryResponse(BaseModel):
    evidence_id: str
    current_custodian: Optional[str]
    last_transfer_at: Optional[datetime]
    total_transfers: int
    history: List[Dict[str, Any]]


class AccessHistoryResponse(BaseModel):
    evidence_id: str
    total_accesses: int
    access_log: List[Dict[str, Any]]


# ============================================================
# TENANT CONTEXT HELPER
# ============================================================

def get_tenant_id(request: Request) -> str:
    """Extract tenant_id from request state"""
    tenant_id = getattr(request.state, 'tenant_id', None)
    if tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing tenant context. Ensure X-Tenant-ID header is provided."
        )
    return tenant_id


# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/", response_model=Dict[str, Any])
async def get_custody_records(
    request: Request,
    evidence_id: Optional[str] = Query(None, description="Filter by evidence ID"),
    custodian: Optional[str] = Query(None, description="Filter by custodian"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: AsyncSession = Depends(get_db)
):
    try:
        tenant_id = get_tenant_id(request)

        query = """
            SELECT
                c.id,
                c.evidence_id,
                c.from_custodian,
                c.to_custodian,
                c.reason,
                c.transferred_by,
                c.transferred_at,
                c.status,
                c.notes
            FROM custody_chain c
            WHERE c.tenant_id = :tenant_id
        """
        params = {"tenant_id": tenant_id}

        if evidence_id:
            query += " AND c.evidence_id = :evidence_id"
            params["evidence_id"] = evidence_id

        if custodian:
            query += " AND (c.from_custodian = :custodian OR c.to_custodian = :custodian)"
            params["custodian"] = custodian

        query += " ORDER BY c.transferred_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset

        result = await db.execute(text(query), params)
        records = result.fetchall()

        return {
            "data": [dict(row._mapping) for row in records],
            "total": len(records),
            "limit": limit,
            "offset": offset
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get custody records: {str(e)}"
        )


@router.post("/{evidence_id}/transfer", response_model=TransferResponse)
async def record_transfer(
    request: Request,
    evidence_id: str,
    transfer: TransferRequest,
    db: AsyncSession = Depends(get_db),
    transferred_by: str = Query("system", description="User performing the transfer")
):
    try:
        tenant_id = get_tenant_id(request)
        service = CustodyService(db, tenant_id)
        result = await service.record_transfer(
            evidence_id=evidence_id,
            from_custodian=transfer.from_custodian,
            to_custodian=transfer.to_custodian,
            reason=transfer.reason,
            transferred_by=transferred_by,
            notes=transfer.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record transfer: {str(e)}"
        )


@router.get("/{evidence_id}/history", response_model=CustodyHistoryResponse)
async def get_custody_history(
    request: Request,
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        tenant_id = get_tenant_id(request)
        service = CustodyService(db, tenant_id)
        history = await service.get_custody_history(evidence_id)
        current = await service.get_current_custodian(evidence_id)

        last_transfer = None
        if history and len(history) > 0:
            last_transfer = history[-1].get('transferred_at')

        return CustodyHistoryResponse(
            evidence_id=evidence_id,
            current_custodian=current,
            last_transfer_at=last_transfer,
            total_transfers=len(history),
            history=history
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get custody history: {str(e)}"
        )


@router.get("/{evidence_id}/current", response_model=Dict[str, Any])
async def get_current_custodian(
    request: Request,
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        tenant_id = get_tenant_id(request)
        service = CustodyService(db, tenant_id)
        custodian = await service.get_current_custodian(evidence_id)

        query = text("""
            SELECT transferred_at, transferred_by, reason
            FROM custody_chain
            WHERE evidence_id = :evidence_id
              AND tenant_id = :tenant_id
            ORDER BY transferred_at DESC
            LIMIT 1
        """)
        result = await db.execute(query, {
            "evidence_id": evidence_id,
            "tenant_id": tenant_id
        })
        last_transfer = result.fetchone()

        return {
            "evidence_id": evidence_id,
            "current_custodian": custodian,
            "last_transfer_at": last_transfer[0] if last_transfer else None,
            "last_transferred_by": last_transfer[1] if last_transfer else None,
            "last_transfer_reason": last_transfer[2] if last_transfer else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current custodian: {str(e)}"
        )


@router.post("/{evidence_id}/access", response_model=AccessRecordResponse)
async def record_access(
    request: Request,
    evidence_id: str,
    access: AccessRecordRequest,
    db: AsyncSession = Depends(get_db),
    accessed_by: str = Query("system", description="User accessing the evidence")
):
    try:
        tenant_id = get_tenant_id(request)
        service = CustodyService(db, tenant_id)
        result = await service.record_access(
            evidence_id=evidence_id,
            accessed_by=accessed_by,
            access_type=access.access_type,
            reason=access.reason,
            duration=access.duration
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record access: {str(e)}"
        )


@router.get("/{evidence_id}/access", response_model=AccessHistoryResponse)
async def get_access_history(
    request: Request,
    evidence_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    access_type: Optional[str] = Query(None, description="Filter by access type"),
    db: AsyncSession = Depends(get_db)
):
    try:
        tenant_id = get_tenant_id(request)
        service = CustodyService(db, tenant_id)
        history = await service.get_access_history(evidence_id, limit)

        if access_type:
            history = [h for h in history if h.get('access_type') == access_type]

        return AccessHistoryResponse(
            evidence_id=evidence_id,
            total_accesses=len(history),
            access_log=history
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get access history: {str(e)}"
        )


@router.get("/evidence/{evidence_id}/custody", response_model=Dict[str, Any])
async def get_evidence_custody(
    request: Request,
    evidence_id: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        tenant_id = get_tenant_id(request)

        query = text("""
            SELECT to_custodian, transferred_at, transferred_by, reason, notes
            FROM custody_chain
            WHERE evidence_id = :evidence_id
              AND tenant_id = :tenant_id
            ORDER BY transferred_at DESC
            LIMIT 1
        """)
        result = await db.execute(query, {
            "evidence_id": evidence_id,
            "tenant_id": tenant_id
        })
        current = result.fetchone()

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
              AND tenant_id = :tenant_id
            ORDER BY transferred_at ASC
        """)
        result = await db.execute(query, {
            "evidence_id": evidence_id,
            "tenant_id": tenant_id
        })
        history_rows = result.fetchall()

        history_list = [
            {
                "id": str(row[0]),
                "from_custodian": row[1],
                "to_custodian": row[2],
                "reason": row[3],
                "transferred_by": row[4],
                "transferred_at": row[5].isoformat() if row[5] else None,
                "status": row[6],
                "notes": row[7]
            }
            for row in history_rows
        ]

        return {
            "evidence_id": evidence_id,
            "current_custodian": current[0] if current else None,
            "current_custodian_since": current[1].isoformat() if current and current[1] else None,
            "last_transferred_by": current[2] if current else None,
            "last_transfer_reason": current[3] if current else None,
            "history": history_list,
            "total_transfers": len(history_list)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting custody: {e}")
        return {
            "evidence_id": evidence_id,
            "current_custodian": None,
            "history": [],
            "total_transfers": 0,
            "error": str(e) if "development" in str(settings.ENV) else None
        }


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_custody_service(db: AsyncSession, request: Request):
    tenant_id = getattr(request.state, 'tenant_id', settings.DEFAULT_TENANT_ID)
    return CustodyService(db, tenant_id)