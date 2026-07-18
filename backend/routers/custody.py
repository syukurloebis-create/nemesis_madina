"""
Custody Router - Fixed with infrastructure import
"""
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Fix import path
project_root = Path(__file__).resolve().parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import text

# ============================================================
# DATABASE IMPORT - TRY MULTIPLE SOURCES
# ============================================================

def get_database_functions():
    """Try multiple sources to get database functions"""
    
    # Strategy 1: Direct from database
    try:
        from backend.infrastructure.database import get_db
        return get_db
    except ImportError:
        pass
    
    # Strategy 2: From infrastructure.database
    try:
        from backend.infrastructure.database import get_db
        return get_db
    except ImportError:
        pass
    
    # Strategy 3: From backend.database
    try:
        from backend.database import get_db
        return get_db
    except ImportError:
        pass
    
    # Strategy 4: Create fallback
    try:
        from backend.database import SessionLocal
        def fallback_get_db():
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        return fallback_get_db
    except ImportError:
        pass
    
    # Strategy 5: Mock
    def mock_get_db():
        return None
    
    return mock_get_db

# Get database function
get_db = get_database_functions()

# ============================================================
# REST OF FILE (sama seperti sebelumnya)
# ============================================================

# Import services
try:
    from backend.services.custody_service import CustodyService
except ImportError:
    # Mock service if not available
    class CustodyService:
        def __init__(self, db, tenant_id):
            self.db = db
            self.tenant_id = tenant_id
        
        async def record_transfer(self, evidence_id, from_custodian, to_custodian, reason, transferred_by, notes=None):
            return {"status": "success", "message": "Transfer recorded"}
        
        async def get_custody_history(self, evidence_id):
            return []
        
        async def get_current_custodian(self, evidence_id):
            return None
        
        async def record_access(self, evidence_id, accessed_by, access_type, reason, duration=None):
            return {"status": "success", "message": "Access recorded"}
        
        async def get_access_history(self, evidence_id, limit):
            return []

# Import config
try:
    from config import settings
except ImportError:
    class Settings:
        DEFAULT_TENANT_ID = "default"
        ENV = "development"
    settings = Settings()

# Create router
router = APIRouter(prefix="/custody", tags=["custody"])


# ============================================================
# PYDANTIC MODELS
# ============================================================

class TransferRequest(BaseModel):
    """Request model for custody transfer"""
    from_custodian: str = Field(..., description="Current custodian")
    to_custodian: str = Field(..., description="New custodian")
    reason: str = Field(..., description="Reason for transfer")
    notes: Optional[str] = Field(None, description="Additional notes")

class TransferResponse(BaseModel):
    """Response model for custody transfer"""
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
    """Request model for access recording"""
    access_type: str = Field(..., description="Type of access: view, download, print, edit")
    reason: Optional[str] = Field(None, description="Reason for access")
    duration: Optional[int] = Field(None, description="Access duration in minutes")

class AccessRecordResponse(BaseModel):
    """Response model for access record"""
    id: str
    evidence_id: str
    accessed_by: str
    access_type: str
    reason: Optional[str]
    accessed_at: datetime
    duration: Optional[int]
    status: str

class CustodyHistoryResponse(BaseModel):
    """Response model for custody history"""
    evidence_id: str
    current_custodian: Optional[str]
    last_transfer_at: Optional[datetime]
    total_transfers: int
    history: List[Dict[str, Any]]

class AccessHistoryResponse(BaseModel):
    """Response model for access history"""
    evidence_id: str
    total_accesses: int
    access_log: List[Dict[str, Any]]

# ============================================================
# ENDPOINTS
# ============================================================

@router.get("/", response_model=Dict[str, Any])
async def get_custody_records(
    evidence_id: Optional[str] = Query(None, description="Filter by evidence ID"),
    custodian: Optional[str] = Query(None, description="Filter by custodian"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """
    Get custody records with optional filters
    """
    try:
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
            WHERE 1=1
        """
        params = []
        
        if evidence_id:
            query += " AND c.evidence_id = ?"
            params.append(evidence_id)
        
        if custodian:
            query += " AND (c.from_custodian = ? OR c.to_custodian = ?)"
            params.extend([custodian, custodian])
        
        query += " ORDER BY c.transferred_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        result = db.execute(text(query), params)
        records = result.fetchall()
        
        return {
            "data": [dict(row._mapping) for row in records],
            "total": len(records),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get custody records: {str(e)}"
        )

@router.post("/{evidence_id}/transfer", response_model=TransferResponse)
async def record_transfer(
    evidence_id: str,
    request: TransferRequest,
    db: Session = Depends(get_db),
    transferred_by: str = Query("system", description="User performing the transfer")
):
    """
    Record evidence custody transfer
    """
    try:
        service = CustodyService(db, settings.DEFAULT_TENANT_ID)
        result = await service.record_transfer(
            evidence_id=evidence_id,
            from_custodian=request.from_custodian,
            to_custodian=request.to_custodian,
            reason=request.reason,
            transferred_by=transferred_by,
            notes=request.notes
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record transfer: {str(e)}"
        )

@router.get("/{evidence_id}/history", response_model=CustodyHistoryResponse)
async def get_custody_history(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete custody history for evidence
    """
    try:
        service = CustodyService(db, settings.DEFAULT_TENANT_ID)
        history = await service.get_custody_history(evidence_id)
        current = await service.get_current_custodian(evidence_id)
        
        # Get last transfer time
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get custody history: {str(e)}"
        )

@router.get("/{evidence_id}/current", response_model=Dict[str, Any])
async def get_current_custodian(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    """
    Get current custodian for evidence
    """
    try:
        service = CustodyService(db, settings.DEFAULT_TENANT_ID)
        custodian = await service.get_current_custodian(evidence_id)
        
        # Get last transfer details
        query = text("""
            SELECT transferred_at, transferred_by, reason
            FROM custody_chain
            WHERE evidence_id = :evidence_id
            ORDER BY transferred_at DESC
            LIMIT 1
        """)
        result = db.execute(query, {"evidence_id": evidence_id})
        last_transfer = result.fetchone()
        
        return {
            "evidence_id": evidence_id,
            "current_custodian": custodian,
            "last_transfer_at": last_transfer[0] if last_transfer else None,
            "last_transferred_by": last_transfer[1] if last_transfer else None,
            "last_transfer_reason": last_transfer[2] if last_transfer else None
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get current custodian: {str(e)}"
        )

@router.post("/{evidence_id}/access", response_model=AccessRecordResponse)
async def record_access(
    evidence_id: str,
    request: AccessRecordRequest,
    db: Session = Depends(get_db),
    accessed_by: str = Query("system", description="User accessing the evidence")
):
    """
    Record evidence access
    """
    try:
        service = CustodyService(db, settings.DEFAULT_TENANT_ID)
        result = await service.record_access(
            evidence_id=evidence_id,
            accessed_by=accessed_by,
            access_type=request.access_type,
            reason=request.reason,
            duration=request.duration
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record access: {str(e)}"
        )

@router.get("/{evidence_id}/access", response_model=AccessHistoryResponse)
async def get_access_history(
    evidence_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    access_type: Optional[str] = Query(None, description="Filter by access type"),
    db: Session = Depends(get_db)
):
    """
    Get evidence access history
    """
    try:
        service = CustodyService(db, settings.DEFAULT_TENANT_ID)
        history = await service.get_access_history(evidence_id, limit)
        
        # Filter by access type if provided
        if access_type:
            history = [h for h in history if h.get('access_type') == access_type]
        
        return AccessHistoryResponse(
            evidence_id=evidence_id,
            total_accesses=len(history),
            access_log=history
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get access history: {str(e)}"
        )

@router.get("/evidence/{evidence_id}/custody", response_model=Dict[str, Any])
async def get_evidence_custody(
    evidence_id: str,
    db: Session = Depends(get_db)
):
    """
    Get complete custody information for evidence
    """
    try:
        # Get current custodian
        query = text("""
            SELECT to_custodian, transferred_at, transferred_by, reason, notes
            FROM custody_chain
            WHERE evidence_id = :evidence_id
            ORDER BY transferred_at DESC
            LIMIT 1
        """)
        result = db.execute(query, {"evidence_id": evidence_id})
        current = result.fetchone()
        
        # Get full history
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
        result = db.execute(query, {"evidence_id": evidence_id})
        history_rows = result.fetchall()
        
        # Build history list
        history_list = []
        for row in history_rows:
            history_list.append({
                "id": str(row[0]),
                "from_custodian": row[1],
                "to_custodian": row[2],
                "reason": row[3],
                "transferred_by": row[4],
                "transferred_at": row[5].isoformat() if row[5] else None,
                "status": row[6],
                "notes": row[7]
            })
        
        return {
            "evidence_id": evidence_id,
            "current_custodian": current[0] if current else None,
            "current_custodian_since": current[1].isoformat() if current and current[1] else None,
            "last_transferred_by": current[2] if current else None,
            "last_transfer_reason": current[3] if current else None,
            "history": history_list,
            "total_transfers": len(history_list)
        }
    except Exception as e:
        # Log error but return graceful response
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

def get_custody_service(db: Session):
    """Dependency for CustodyService"""
    return CustodyService(db, settings.DEFAULT_TENANT_ID)