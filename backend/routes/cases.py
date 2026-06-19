# backend/routers/cases.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

from backend.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.config import settings

router = APIRouter(prefix="/cases", tags=["cases"])


# Request/Response Models
class CreateCaseRequest(BaseModel):
    title: str
    description: str


class UpdateCaseRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class CaseResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    assigned_to: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]


# ============================================================
# STATS ENDPOINTS (MUST BE FIRST - before /{case_id})
# ============================================================

@router.get("/stats/total")
async def get_case_stats_total(db: AsyncSession = Depends(get_db)):
    """Get total cases count"""
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM cases"))
        total = result.scalar()
        return {"total_cases": total or 0}
    except Exception as e:
        print(f"Error: {e}")
        return {"total_cases": 0}


@router.get("/stats")
async def get_case_stats(db: AsyncSession = Depends(get_db)):
    """Get case statistics"""
    try:
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'OPEN' THEN 1 END) as open,
                COUNT(CASE WHEN status = 'IN_PROGRESS' THEN 1 END) as in_progress,
                COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) as closed,
                COUNT(CASE WHEN status = 'ARCHIVED' THEN 1 END) as archived
            FROM cases
        """))
        row = result.fetchone()
        
        return {
            "total": row[0] or 0,
            "open": row[1] or 0,
            "in_progress": row[2] or 0,
            "closed": row[3] or 0,
            "archived": row[4] or 0
        }
    except Exception as e:
        print(f"Error: {e}")
        return {"total": 0, "open": 0, "in_progress": 0, "closed": 0, "archived": 0}


# ============================================================
# CRUD ENDPOINTS
# ============================================================

@router.get("/", response_model=List[CaseResponse])
async def get_all_cases(
    limit: int = Query(100, le=1000),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db)
):
    """Get all cases"""
    try:
        result = await db.execute(
            text("SELECT id, title, description, status, priority, assigned_to, created_at, updated_at FROM cases ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
            {"limit": limit, "offset": offset}
        )
        cases = result.fetchall()
        return [
            {
                "id": str(c[0]),
                "title": c[1],
                "description": c[2],
                "status": c[3],
                "priority": c[4],
                "assigned_to": c[5],
                "created_at": c[6].isoformat() if c[6] else None,
                "updated_at": c[7].isoformat() if c[7] else None
            }
            for c in cases
        ]
    except Exception as e:
        print(f"Error: {e}")
        return []


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get case by ID"""
    try:
        result = await db.execute(
            text("SELECT id, title, description, status, priority, assigned_to, created_at, updated_at FROM cases WHERE id = :case_id"),
            {"case_id": case_id}
        )
        case = result.fetchone()
        
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return {
            "id": str(case[0]),
            "title": case[1],
            "description": case[2],
            "status": case[3],
            "priority": case[4],
            "assigned_to": case[5],
            "created_at": case[6].isoformat() if case[6] else None,
            "updated_at": case[7].isoformat() if case[7] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=CaseResponse)
async def create_case(
    request: CreateCaseRequest,
    db: AsyncSession = Depends(get_db),
    actor_id: str = "admin"
):
    """Create a new case"""
    try:
        import uuid
        case_id = uuid.uuid4()
        timestamp = datetime.utcnow()
        
        result = await db.execute(
            text("""
                INSERT INTO cases (id, title, description, status, priority, created_at, updated_at, tenant_id)
                VALUES (:id, :title, :description, 'OPEN', 'MEDIUM', :created_at, :updated_at, :tenant_id)
                RETURNING id, title, description, status, priority, assigned_to, created_at, updated_at
            """),
            {
                "id": str(case_id),
                "title": request.title,
                "description": request.description,
                "created_at": timestamp,
                "updated_at": timestamp,
                "tenant_id": settings.DEFAULT_TENANT_ID
            }
        )
        
        row = result.fetchone()
        await db.commit()
        
        return {
            "id": str(row[0]),
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "assigned_to": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None
        }
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    request: UpdateCaseRequest,
    db: AsyncSession = Depends(get_db),
    actor_id: str = "admin"
):
    """Update a case"""
    try:
        updates = []
        params = {"id": case_id}
        
        if request.title:
            updates.append("title = :title")
            params["title"] = request.title
        if request.description:
            updates.append("description = :description")
            params["description"] = request.description
        
        if not updates:
            case = await get_case(case_id, db)
            return case
        
        updates.append("updated_at = NOW()")
        
        query = text(f"""
            UPDATE cases 
            SET {', '.join(updates)}
            WHERE id = :id
            RETURNING id, title, description, status, priority, assigned_to, created_at, updated_at
        """)
        
        result = await db.execute(query, params)
        row = result.fetchone()
        await db.commit()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return {
            "id": str(row[0]),
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "assigned_to": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
# ============================================================
# CASE ANALYSIS ENDPOINT
# ============================================================

@router.get("/{case_id}/analysis")
async def get_case_analysis(
    case_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get comprehensive analysis for a specific case.
    Includes event timeline, evidence count, and integrity status.
    """
    from sqlalchemy import text
    import uuid
    
    try:
        # Validate UUID
        try:
            uuid.UUID(case_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid case_id format")
        
        # Get case details
        case_result = await session.execute(
            text("""
                SELECT id, title, description, status, priority, created_at, updated_at
                FROM cases 
                WHERE id = :case_id
            """),
            {"case_id": case_id}
        )
        case = case_result.fetchone()
        
        if not case:
            raise HTTPException(status_code=404, detail=f"Case {case_id} not found")
        
        # Get event statistics
        event_result = await session.execute(
            text("""
                SELECT 
                    COUNT(*) as total_events,
                    MIN(created_at) as first_event,
                    MAX(created_at) as last_event,
                    COUNT(DISTINCT event_type) as unique_event_types
                FROM events 
                WHERE aggregate_id = :case_id AND aggregate_type = 'CASE'
            """),
            {"case_id": case_id}
        )
        event_stats = event_result.fetchone()
        
        # Get evidence count
        evidence_result = await session.execute(
            text("SELECT COUNT(*) FROM evidence WHERE case_id = :case_id"),
            {"case_id": case_id}
        )
        evidence_count = evidence_result.scalar() or 0
        
        # Get findings count (with null handling)
        try:
            findings_result = await session.execute(
                text("SELECT COUNT(*) FROM findings WHERE case_id = :case_id"),
                {"case_id": case_id}  # ← PASTIKAN PARAMETER DI SINI!
            )
            findings_count = findings_result.scalar() or 0
        except Exception as e:
            logger.warning(f"Could not query findings: {e}")
            findings_count = 0
        
        # Get custody chain count
        custody_result = await session.execute(
            text("SELECT COUNT(*) FROM custody WHERE evidence_id IN (SELECT id FROM evidence WHERE case_id = :case_id)"),
            {"case_id": case_id}
        )
        custody_count = custody_result.scalar() or 0
        
        return {
            "case": {
                "id": str(case[0]),
                "title": case[1],
                "description": case[2],
                "status": case[3],
                "priority": case[4],
                "created_at": str(case[5]) if case[5] else None,
                "updated_at": str(case[6]) if case[6] else None
            },
            "statistics": {
                "total_events": event_stats[0] or 0,
                "first_event_at": str(event_stats[1]) if event_stats[1] else None,
                "last_event_at": str(event_stats[2]) if event_stats[2] else None,
                "unique_event_types": event_stats[3] or 0,
                "evidence_count": evidence_count,
                "findings_count": findings_count,
                "custody_actions": custody_count
            },
            "analysis_status": "available"
        }
    except HTTPException:
        raise
    except Exception as e:
        return {
            "case_id": case_id,
            "error": str(e),
            "analysis_status": "error"
        }
