from fastapi import APIRouter
from backend.infrastructure.database import AsyncSessionLocal
from sqlalchemy import text

router = APIRouter(prefix="/procurement", tags=["procurement"])

@router.get("/stats")
async def get_procurement_stats():
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM rup_paket_detailed"))
        total_packages = result.scalar() or 0
        
        result = await session.execute(text("SELECT SUM(total_nilai) FROM rup_paket_detailed"))
        total_value = float(result.scalar() or 0)
        
        result = await session.execute(text("SELECT COUNT(DISTINCT nama_penyedia) FROM rup_paket_detailed WHERE nama_penyedia IS NOT NULL"))
        unique_vendors = result.scalar() or 0
        
        result = await session.execute(text("SELECT COUNT(*) FROM graph_relationships WHERE relationship_type = 'VENDOR_COLLUSION'"))
        collusion_edges = result.scalar() or 0
        
        return {
            "total_packages": total_packages,
            "total_value": total_value,
            "unique_vendors": unique_vendors,
            "collusion_edges": collusion_edges,
        }

@router.get("/vendors")
async def get_vendors(limit: int = 100):
    async with AsyncSessionLocal() as session:
        query = """
            SELECT nama_penyedia as name, COUNT(*) as package_count, SUM(total_nilai) as total_value
            FROM rup_paket_detailed
            WHERE nama_penyedia IS NOT NULL
            GROUP BY nama_penyedia
            ORDER BY package_count DESC
            LIMIT :limit
        """
        result = await session.execute(text(query), {'limit': limit})
        vendors = []
        for row in result.fetchall():
            vendors.append({
                "name": row[0],
                "package_count": row[1],
                "total_value": float(row[2]) if row[2] else 0
            })
        return {"vendors": vendors, "total": len(vendors)}
