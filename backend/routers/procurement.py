# routers/procurement.py - Procurement dari RUP (3.630 data)
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.database import get_db
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/procurement", tags=["procurement"])

@router.get("/vendors")
async def get_vendors(
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get vendors from RUP data"""
    try:
        query = """
            SELECT 
                nama_penyedia as name,
                COUNT(*) as total_packages,
                COALESCE(SUM(total_nilai), 0) as total_value,
                CASE 
                    WHEN COALESCE(SUM(total_nilai), 0) > 1000000000 THEN 85
                    WHEN COALESCE(SUM(total_nilai), 0) > 500000000 THEN 75
                    WHEN COALESCE(SUM(total_nilai), 0) > 100000000 THEN 60
                    WHEN COALESCE(SUM(total_nilai), 0) > 50000000 THEN 45
                    ELSE 30
                END as risk_score,
                COUNT(DISTINCT nama_instansi) as instansi_count
            FROM rup_paket_detailed
            WHERE nama_penyedia IS NOT NULL AND nama_penyedia != ''
            GROUP BY nama_penyedia
            ORDER BY risk_score DESC, total_value DESC
            LIMIT :limit
        """
        result = await db.execute(text(query), {"limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "name": row[0],
                "total_packages": row[1] or 0,
                "total_value": float(row[2]) if row[2] else 0,
                "risk_score": float(row[3]) if row[3] else 0,
                "instansi_count": row[4] or 0
            }
            for row in rows
        ]
    except Exception as e:
        logger.error(f"Error getting vendors: {str(e)}")
        return []

@router.get("/stats")
async def get_procurement_stats(db: AsyncSession = Depends(get_db)):
    try:
        query = """
            SELECT 
                COUNT(DISTINCT nama_penyedia) as total_vendors,
                COUNT(*) as total_packages,
                COALESCE(SUM(total_nilai), 0) as total_value,
                COALESCE(AVG(total_nilai), 0) as avg_value,
                COUNT(DISTINCT tahun_anggaran) as total_years
            FROM rup_paket_detailed
            WHERE nama_penyedia IS NOT NULL AND nama_penyedia != ''
        """
        result = await db.execute(text(query))
        row = result.fetchone()
        
        return {
            "total_vendors": row[0] or 0,
            "total_packages": row[1] or 0,
            "total_value": float(row[2]) if row[2] else 0,
            "avg_value": float(row[3]) if row[3] else 0,
            "total_years": row[4] or 0
        }
    except Exception as e:
        logger.error(f"Error getting procurement stats: {str(e)}")
        return {"total_vendors": 0, "total_packages": 0, "total_value": 0, "avg_value": 0, "total_years": 0}
