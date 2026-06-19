# routers/rup.py - RUP endpoints with 3.630 data
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from backend.database import get_db
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/rup", tags=["rup"])

@router.get("/data")
async def get_rup_data(
    tahun: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Get RUP data from database"""
    try:
        query = """
            SELECT 
                id,
                kode_paket,
                kode_rup,
                tahun_anggaran as tahun,
                nama_instansi as instansi,
                satuan_kerja,
                nama_penyedia as vendor,
                nama_paket,
                total_nilai as pagu,
                nilai_pdn,
                sumber_transaksi,
                sumber_dana,
                metode_pengadaan,
                jenis_pengadaan,
                status_paket as status,
                created_at,
                updated_at
            FROM rup_paket_detailed
            WHERE 1=1
        """
        params = {}
        
        if tahun:
            query += " AND tahun_anggaran = :tahun"
            params["tahun"] = int(tahun)
        
        if status:
            query += " AND status_paket = :status"
            params["status"] = status
        
        if search:
            query += """ AND (
                LOWER(nama_paket) LIKE LOWER(:search) OR 
                LOWER(nama_instansi) LIKE LOWER(:search) OR
                LOWER(nama_penyedia) LIKE LOWER(:search) OR
                LOWER(kode_rup) LIKE LOWER(:search)
            )"""
            params["search"] = f"%{search}%"
        
        # Count total
        count_query = query.replace(
            "SELECT id, kode_paket, kode_rup, tahun_anggaran as tahun, nama_instansi as instansi, satuan_kerja, nama_penyedia as vendor, nama_paket, total_nilai as pagu, nilai_pdn, sumber_transaksi, sumber_dana, metode_pengadaan, jenis_pengadaan, status_paket as status, created_at, updated_at",
            "SELECT COUNT(*)"
        )
        count_result = await db.execute(text(count_query), params)
        total = count_result.scalar() or 0
        
        query += " ORDER BY tahun_anggaran DESC, total_nilai DESC LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = offset
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        return {
            "data": [
                {
                    "id": str(row[0]),
                    "kode_paket": row[1] or "-",
                    "kode_rup": row[2] or "-",
                    "tahun": row[3],
                    "instansi": row[4] or "-",
                    "satuan_kerja": row[5] or "-",
                    "vendor": row[6] or "-",
                    "nama_paket": row[7] or "-",
                    "pagu": float(row[8]) if row[8] else 0,
                    "nilai_pdn": float(row[9]) if row[9] else 0,
                    "sumber_transaksi": row[10] or "-",
                    "sumber_dana": row[11] or "-",
                    "metode_pengadaan": row[12] or "-",
                    "jenis_pengadaan": row[13] or "-",
                    "status": row[14] or "-",
                    "created_at": row[15].isoformat() if row[15] else None,
                    "updated_at": row[16].isoformat() if row[16] else None
                }
                for row in rows
            ],
            "total": total
        }
    except Exception as e:
        logger.error(f"Error getting RUP data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_rup_stats(db: AsyncSession = Depends(get_db)):
    """Get RUP statistics"""
    try:
        query = """
            SELECT 
                COUNT(*) as total,
                COALESCE(SUM(total_nilai), 0) as total_pagu,
                COUNT(DISTINCT nama_instansi) as total_instansi,
                COUNT(DISTINCT nama_penyedia) as total_vendor,
                COUNT(CASE WHEN status_paket = 'Selesai' THEN 1 END) as selesai,
                COUNT(CASE WHEN status_paket = 'Dalam Proses' THEN 1 END) as dalam_proses,
                COUNT(DISTINCT tahun_anggaran) as total_years,
                MIN(tahun_anggaran) as tahun_min,
                MAX(tahun_anggaran) as tahun_max
            FROM rup_paket_detailed
        """
        result = await db.execute(text(query))
        row = result.fetchone()
        
        return {
            "total": row[0] or 0,
            "total_pagu": float(row[1]) if row[1] else 0,
            "total_instansi": row[2] or 0,
            "total_vendor": row[3] or 0,
            "selesai": row[4] or 0,
            "dalam_proses": row[5] or 0,
            "total_years": row[6] or 0,
            "tahun_min": row[7] or 0,
            "tahun_max": row[8] or 0
        }
    except Exception as e:
        logger.error(f"Error getting RUP stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/years")
async def get_rup_years(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT DISTINCT tahun_anggaran FROM rup_paket_detailed ORDER BY tahun_anggaran DESC"))
        return [row[0] for row in result.fetchall()]
    except Exception as e:
        logger.error(f"Error getting RUP years: {str(e)}")
        return []

@router.get("/statuses")
async def get_rup_statuses(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT DISTINCT status_paket FROM rup_paket_detailed ORDER BY status_paket"))
        return [row[0] for row in result.fetchall()]
    except Exception as e:
        logger.error(f"Error getting RUP statuses: {str(e)}")
        return []
