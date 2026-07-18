# graph/services/relationship_builder.py - FINANCIAL FIXED
import logging
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class RelationshipBuilder:
    def __init__(self, session: AsyncSession, case_id: Optional[str] = None):
        self.session = session
        self.case_id = case_id or "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    async def build_all_relationships(self) -> Dict[str, Any]:
        logger.info(f"🚀 Starting Relationship Builder for case: {self.case_id}")
        results = {"shared_package": 0, "vendor_similarity": 0, "method_similarity": 0, "financial_similarity": 0, "total": 0}
        
        try:
            results["shared_package"] = await self._build_shared_package()
            results["vendor_similarity"] = await self._build_vendor_similarity()
            results["method_similarity"] = await self._build_method_similarity()
            results["financial_similarity"] = await self._build_financial_similarity()
            results["total"] = sum(results.values())
            await self.session.commit()
            logger.info(f"✅ Complete: {results}")
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Failed: {e}")
            raise
        return results
    
    async def _build_shared_package(self) -> int:
        logger.info("  📦 Building shared package...")
        result = await self.session.execute(text("""
            INSERT INTO graph_relationships (source_id, target_id, relationship_type, weight, case_id, created_at)
            SELECT e1.id, e2.id, 'shared_package',
                   LEAST(COUNT(*) * 15 + 30, 100),
                   CAST(:case_id AS VARCHAR), NOW()
            FROM graph_entities e1
            JOIN graph_entities e2 ON e1.id < e2.id
            JOIN rup_paket_detailed r1 ON LOWER(r1.nama_penyedia) = LOWER(e1.name)
            JOIN rup_paket_detailed r2 ON LOWER(r2.nama_penyedia) = LOWER(e2.name)
            WHERE e1.entity_type = 'vendor' AND e2.entity_type = 'vendor'
              AND e1.case_id = :case_id AND e2.case_id = :case_id
              AND LOWER(TRIM(r1.nama_paket)) = LOWER(TRIM(r2.nama_paket))
              AND LOWER(r1.nama_penyedia) != LOWER(r2.nama_penyedia)
            GROUP BY e1.id, e2.id HAVING COUNT(*) >= 2
        """), {"case_id": self.case_id})
        await self.session.commit()
        logger.info(f"    ✅ {result.rowcount} edges")
        return result.rowcount
    
    async def _build_vendor_similarity(self) -> int:
        logger.info("  🔤 Building vendor similarity (TRIGRAM)...")
        result = await self.session.execute(text("""
            INSERT INTO graph_relationships
            (
                source_id,
                target_id,
                relationship_type,
                weight,
                case_id,
                created_at
            )
            SELECT
                e1.id,
                e2.id,
                CASE
                    WHEN similarity(
                        LOWER(e1.name),
                        LOWER(e2.name)
                    ) >= 0.85
                    THEN 'same_entity_candidate'
                    ELSE 'vendor_name_similarity'
                END,
                LEAST(
                    similarity(
                        LOWER(e1.name),
                        LOWER(e2.name)
                    ) * 100,
                    100
                ),
                CAST(:case_id AS VARCHAR),
                NOW()
            FROM graph_entities e1
            JOIN graph_entities e2
                ON e1.id < e2.id
            WHERE
                e1.entity_type = 'vendor'
                AND e2.entity_type = 'vendor'
                AND e1.case_id = :case_id
                AND e2.case_id = :case_id
                AND e1.name <> e2.name
                AND similarity(
                    LOWER(e1.name),
                    LOWER(e2.name)
                ) >= 0.70
            ORDER BY
                similarity(
                    LOWER(e1.name),
                    LOWER(e2.name)
                ) DESC
            LIMIT 2000
        """),
        {
            "case_id": self.case_id
        })
        await self.session.commit()
        logger.info(
            f"    ✅ {result.rowcount} edges"
        )
        return result.rowcount

    
    async def _build_method_similarity(self) -> int:
        logger.info("  📂 Building method similarity...")
        result = await self.session.execute(text("""
            INSERT INTO graph_relationships (source_id, target_id, relationship_type, weight, case_id, created_at)
            SELECT e1.id, e2.id, 'method_similarity',
                   LEAST(40 + (COUNT(*) * 3), 70),
                   CAST(:case_id AS VARCHAR), NOW()
            FROM graph_entities e1
            JOIN graph_entities e2 ON e1.id < e2.id
            JOIN rup_paket_detailed r1 ON LOWER(r1.nama_penyedia) = LOWER(e1.name)
            JOIN rup_paket_detailed r2 ON LOWER(r2.nama_penyedia) = LOWER(e2.name)
            WHERE e1.entity_type = 'vendor' AND e2.entity_type = 'vendor'
              AND e1.case_id = :case_id AND e2.case_id = :case_id
              AND r1.metode_pengadaan = r2.metode_pengadaan
              AND LOWER(r1.nama_penyedia) != LOWER(r2.nama_penyedia)
            GROUP BY e1.id, e2.id HAVING COUNT(*) >= 2
            LIMIT 2000
        """), {"case_id": self.case_id})
        await self.session.commit()
        logger.info(f"    ✅ {result.rowcount} edges")
        return result.rowcount
    
    async def _build_financial_similarity(self) -> int:
        """Build financial similarity - STRICT + CORRECT SQL"""
        logger.info("  💰 Building financial similarity (STRICT)...")
        
        # ============ FIX: Kolom lengkap ============
        result = await self.session.execute(text("""
            INSERT INTO graph_relationships (source_id, target_id, relationship_type, weight, case_id, created_at)
            WITH vendor_avg AS (
                SELECT 
                    e.id,
                    e.name,
                    e.case_id,
                    AVG(r.total_nilai) as avg_value,
                    COUNT(DISTINCT r.tahun_anggaran) as year_count,
                    COUNT(DISTINCT r.metode_pengadaan) as method_count
                FROM graph_entities e
                JOIN rup_paket_detailed r ON LOWER(r.nama_penyedia) = LOWER(e.name)
                WHERE e.entity_type = 'vendor' AND e.case_id = :case_id
                  AND r.total_nilai > 0
                GROUP BY e.id, e.name, e.case_id
                HAVING COUNT(*) >= 3
            )
            SELECT 
                v1.id as source_id,
                v2.id as target_id,
                'financial_similarity' as relationship_type,
                LEAST(
                    (1 - ABS(v1.avg_value - v2.avg_value) / GREATEST(v1.avg_value, v2.avg_value)) * 50 +
                    (CASE WHEN v1.year_count = v2.year_count THEN 20 ELSE 0 END) +
                    (CASE WHEN v1.method_count = v2.method_count THEN 10 ELSE 0 END),
                    100
                ) as weight,
                CAST(:case_id AS VARCHAR) as case_id,
                NOW() as created_at
            FROM vendor_avg v1
            JOIN vendor_avg v2 ON v1.id < v2.id
            WHERE ABS(v1.avg_value - v2.avg_value) / GREATEST(v1.avg_value, v2.avg_value) < 0.15
              AND v1.case_id = :case_id AND v2.case_id = :case_id
            ORDER BY weight DESC
            LIMIT 5000
        """), {"case_id": self.case_id})
        
        await self.session.commit()
        logger.info(f"    ✅ {result.rowcount} edges")
        return result.rowcount