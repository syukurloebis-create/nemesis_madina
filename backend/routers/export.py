from fastapi import APIRouter, HTTPException, Depends, Query, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
import json
from datetime import datetime
import csv
from io import StringIO

router = APIRouter(prefix="/export", tags=["export"])

@router.get("/cases")
async def export_cases(
    format: str = Query("json", description="json or csv"),
    db: AsyncSession = Depends(get_db)
):
    """Export cases data"""
    try:
        # Fix: cast case_id ke text untuk join dengan evidence
        result = await db.execute(text("""
            SELECT 
                c.id,
                c.title,
                c.risk_score,
                c.risk_level,
                c.workflow_stage,
                c.status,
                c.created_at,
                (SELECT COUNT(*) FROM evidence e WHERE e.case_id = c.id::text) as evidence_count
            FROM cases c
            ORDER BY c.created_at DESC
        """))
        rows = result.fetchall()
        
        data = [
            {
                "id": row[0],
                "title": row[1],
                "risk_score": float(row[2]) if row[2] else 0,
                "risk_level": row[3],
                "workflow_stage": row[4],
                "status": row[5],
                "created_at": row[6].isoformat() if row[6] else None,
                "evidence_count": row[7] or 0
            }
            for row in rows
        ]
        
        if format == "csv":
            output = StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=cases_export_{datetime.now().strftime('%Y%m%d')}.csv"
                }
            )
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/evidence")
async def export_evidence(
    format: str = Query("json", description="json or csv"),
    db: AsyncSession = Depends(get_db)
):
    """Export evidence data"""
    try:
        result = await db.execute(text("""
            SELECT 
                id,
                filename,
                status,
                trust_score,
                confidence_level,
                file_type,
                uploaded_at,
                case_id
            FROM evidence
            ORDER BY uploaded_at DESC
        """))
        rows = result.fetchall()
        
        data = [
            {
                "id": row[0],
                "filename": row[1],
                "status": row[2],
                "trust_score": float(row[3]) if row[3] else 0,
                "confidence_level": row[4],
                "file_type": row[5],
                "uploaded_at": row[6].isoformat() if row[6] else None,
                "case_id": row[7]
            }
            for row in rows
        ]
        
        if format == "csv":
            output = StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return Response(
                content=output.getvalue(),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename=evidence_export_{datetime.now().strftime('%Y%m%d')}.csv"
                }
            )
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def export_summary(db: AsyncSession = Depends(get_db)):
    """Export executive summary"""
    try:
        result = await db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM cases) as total_cases,
                (SELECT COUNT(*) FROM cases WHERE risk_score >= 80) as high_risk,
                (SELECT COUNT(*) FROM cases WHERE status = 'OPEN') as open_cases,
                (SELECT COUNT(*) FROM cases WHERE status = 'CLOSED') as closed_cases,
                (SELECT COUNT(*) FROM evidence) as total_evidence,
                (SELECT COUNT(*) FROM evidence WHERE status = 'verified') as verified_evidence
        """))
        row = result.fetchone()
        
        return {
            "total_cases": row[0] or 0,
            "high_risk": row[1] or 0,
            "open_cases": row[2] or 0,
            "closed_cases": row[3] or 0,
            "total_evidence": row[4] or 0,
            "verified_evidence": row[5] or 0,
            "exported_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
