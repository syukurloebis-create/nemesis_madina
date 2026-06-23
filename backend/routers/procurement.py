# routers/procurement.py - Procurement Endpoints
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List, Dict, Any, Optional

from database import get_db

router = APIRouter(prefix="/api/v1/procurement", tags=["procurement"])

@router.get("/vendors")
async def get_vendors(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get list of vendors from RUP data"""
    try:
        query = """
            SELECT 
                nama_penyedia as name,
                COUNT(*) as package_count,
                SUM(total_nilai) as total_value,
                AVG(total_nilai) as avg_value
            FROM rup_paket_detailed
            WHERE nama_penyedia IS NOT NULL AND nama_penyedia != ''
            GROUP BY nama_penyedia
            ORDER BY total_value DESC
            LIMIT :limit OFFSET :offset
        """
        result = await db.execute(text(query), {"limit": limit, "offset": offset})
        rows = result.fetchall()
        
        return [
            {
                "name": row[0],
                "package_count": row[1] or 0,
                "total_value": float(row[2]) if row[2] else 0,
                "avg_value": float(row[3]) if row[3] else 0
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_procurement_stats(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get procurement statistics from RUP data"""
    try:
        # ============ FIX: Query dengan indentasi yang benar ============
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
        return {
            "total_vendors": 0,
            "total_packages": 0,
            "total_value": 0,
            "avg_value": 0,
            "total_years": 0
        }

# ============ FIX: Hapus duplikasi code di bawah ============
# Endpoint kedua /stats (duplikat) dihapus
# Pastikan tidak ada code tambahan di luar fungsi
