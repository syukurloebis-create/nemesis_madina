from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from backend.infrastructure.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/api/procurement", tags=["procurement"])

@router.get("/list")
async def list_procurement(limit: int = 100):
    """List procurement tanpa auth untuk testing"""
    try:
        from backend.infrastructure.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("""
                SELECT id, procurement_id, title, vendor, amount, date, created_at
                FROM procurement_records
                ORDER BY date DESC
                LIMIT :limit
            """), {"limit": limit})
            
            records = []
            for r in result.fetchall():
                records.append({
                    "id": r[0],
                    "procurement_id": r[1],
                    "title": r[2],
                    "vendor": r[3],
                    "amount": float(r[4]) if r[4] else 0,
                    "date": str(r[5]) if r[5] else None,
                    "created_at": str(r[6]) if r[6] else None
                })
            
            return {"records": records, "count": len(records), "success": True}
    except Exception as e:
        return {"records": [], "count": 0, "success": False, "error": str(e)}

@router.get("/stats")
async def procurement_stats():
    """Statistik procurement tanpa auth"""
    try:
        from backend.infrastructure.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("""
                SELECT 
                    COUNT(*) as total_records,
                    COALESCE(SUM(amount), 0) as total_amount,
                    COUNT(DISTINCT vendor) as unique_vendors,
                    COALESCE(AVG(amount), 0) as avg_amount
                FROM procurement_records
            """))
            row = result.fetchone()
            
            return {
                "total_records": row[0],
                "total_amount": float(row[1]) if row[1] else 0,
                "unique_vendors": row[2],
                "avg_amount": float(row[3]) if row[3] else 0,
                "success": True
            }
    except Exception as e:
        return {"success": False, "error": str(e)}

@router.get("/vendors")
async def vendor_analysis():
    """Analisis vendor tanpa auth"""
    try:
        from backend.infrastructure.database import AsyncSessionLocal
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(text("""
                SELECT 
                    vendor,
                    COUNT(*) as contract_count,
                    COALESCE(SUM(amount), 0) as total_amount,
                    COALESCE(AVG(amount), 0) as avg_amount
                FROM procurement_records
                GROUP BY vendor
                ORDER BY total_amount DESC
            """))
            
            vendors = []
            for r in result.fetchall():
                vendors.append({
                    "vendor": r[0],
                    "contract_count": r[1],
                    "total_amount": float(r[2]) if r[2] else 0,
                    "avg_amount": float(r[3]) if r[3] else 0
                })
            
            return {"vendors": vendors, "total": len(vendors), "success": True}
    except Exception as e:
        return {"vendors": [], "total": 0, "success": False, "error": str(e)}
