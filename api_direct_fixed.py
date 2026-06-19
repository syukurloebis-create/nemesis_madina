from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid
from datetime import datetime
import json

from backend.infrastructure.database import get_db

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("/")
async def list_cases(db: AsyncSession = Depends(get_db)):
    """List all cases"""
    try:
        result = await db.execute(
            text("SELECT id, title, status, priority, created_at FROM cases ORDER BY created_at DESC LIMIT 100")
        )
        rows = result.fetchall()
        return JSONResponse(content=[
            {
                "id": row[0],
                "title": row[1],
                "status": row[2],
                "priority": row[3],
                "created_at": row[4].isoformat() if row[4] else None
            }
            for row in rows
        ])
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/")
async def create_case(request: Request, db: AsyncSession = Depends(get_db)):
    """Create a new case - supports both query params and JSON body"""
    try:
        # Try to get JSON body first
        try:
            body = await request.json()
            title = body.get("title")
            description = body.get("description")
            priority = body.get("priority", "MEDIUM")
        except:
            # Fallback to query parameters
            params = dict(request.query_params)
            title = params.get("title")
            description = params.get("description")
            priority = params.get("priority", "MEDIUM")
        
        if not title:
            return JSONResponse(status_code=400, content={"error": "title is required"})
        
        case_id = str(uuid.uuid4())
        
        await db.execute(
            text("""
                INSERT INTO cases (id, title, description, status, priority, case_metadata, created_at)
                VALUES (:id, :title, :desc, 'DRAFT', :priority, '{}'::json, NOW())
            """),
            {"id": case_id, "title": title, "desc": description, "priority": priority.upper()}
        )
        await db.commit()
        
        return JSONResponse(content={
            "id": case_id,
            "title": title,
            "description": description,
            "status": "DRAFT",
            "priority": priority.upper(),
            "message": "Case created successfully"
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db)):
    """Get case by ID"""
    try:
        result = await db.execute(
            text("SELECT id, title, description, status, priority, created_at FROM cases WHERE id = :id"),
            {"id": case_id}
        )
        row = result.fetchone()
        if not row:
            return JSONResponse(status_code=404, content={"error": "Case not found"})
        return JSONResponse(content={
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "created_at": row[5].isoformat() if row[5] else None
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.get("/stats/total")
async def get_total_cases(db: AsyncSession = Depends(get_db)):
    """Get total cases count"""
    result = await db.execute(text("SELECT COUNT(*) FROM cases"))
    count = result.scalar()
    return JSONResponse(content={"total_cases": count})
