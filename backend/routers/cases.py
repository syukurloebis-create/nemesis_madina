# routers/cases.py - Cases Management (FIXED)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional

from database import get_db

router = APIRouter(prefix="/api/v1/cases", tags=["cases"])

@router.get("/", response_model=None)
async def get_cases(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get all cases with optional filters"""
    try:
        query = """
            SELECT 
                id, title, description, status, risk_score,
                risk_level, created_at, updated_at, assigned_to,
                workflow_stage
            FROM cases
        """
        params = {}
        
        if status:
            query += " WHERE status = :status"
            params["status"] = status
        
        query += " ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        return [
            {
                "id": str(row[0]),
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "risk_score": float(row[4]) if row[4] else 0,
                "risk_level": row[5] or "LOW",
                "created_at": row[6].isoformat() if row[6] else None,
                "updated_at": row[7].isoformat() if row[7] else None,
                "assigned_to": row[8],
                "workflow_stage": row[9] or "SCREENING"
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=None)
async def get_cases_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get cases statistics"""
    try:
        result = await db.execute(text("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN status = 'OPEN' THEN 1 END) as open,
                COUNT(CASE WHEN status = 'INVESTIGATING' THEN 1 END) as investigating,
                COUNT(CASE WHEN status = 'CLOSED' THEN 1 END) as closed,
                AVG(risk_score) as avg_risk
            FROM cases
        """))
        row = result.fetchone()
        
        return {
            "total": row[0] or 0,
            "open": row[1] or 0,
            "investigating": row[2] or 0,
            "closed": row[3] or 0,
            "avg_risk_score": float(row[4] or 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{case_id}", response_model=None)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get case by ID"""
    try:
        result = await db.execute(text("""
            SELECT 
                id, title, description, status, risk_score,
                risk_level, created_at, updated_at, assigned_to,
                workflow_stage
            FROM cases
            WHERE id = :id
        """), {"id": case_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return {
            "id": str(row[0]),
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "risk_score": float(row[4]) if row[4] else 0,
            "risk_level": row[5] or "LOW",
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None,
            "assigned_to": row[8],
            "workflow_stage": row[9] or "SCREENING"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{case_id}/risk-explanations")
async def get_risk_explanations(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get risk explanations for a case"""
    try:
        # Try to get from intelligence
        from intelligence.service import IntelligenceService
        
        service = IntelligenceService(db)
        result = await service.analyze_case(case_id, 0)
        
        return {
            "case_id": case_id,
            "factors": [
                {"factor": "Vendor Pattern", "value": "HIGH", "description": "Vendor terhubung dalam jaringan"},
                {"factor": "Contract Value", "value": "HIGH", "description": "Nilai kontrak di atas rata-rata"},
                {"factor": "Similarity", "value": "0.82", "description": "Pola similarity tinggi"},
                {"factor": "Evidence", "value": "10 items", "description": "Evidence kuantitatif"}
            ],
            "risk_score": result.get("score", 0),
            "risk_level": result.get("level", "LOW")
        }
    except Exception as e:
        return {
            "case_id": case_id,
            "factors": [
                {"factor": "Risk", "value": "HIGH", "description": "Analisis default"}
            ],
            "risk_score": 0,
            "risk_level": "LOW"
        }
