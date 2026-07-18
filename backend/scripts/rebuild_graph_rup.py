#!/usr/bin/env python3
"""
Rebuild Graph Relationships dari Data RUP
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from backend.database import get_db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def rebuild_graph_from_rup():
    """Rebuild graph_relationships dari data RUP"""
    
    async for db in get_db():
        try:
            logger.info("🔄 Starting graph rebuild from RUP data...")
            
            # 1. Hapus relationships lama
            logger.info("🗑️  Clearing old relationships...")
            await db.execute(text("DELETE FROM graph_relationships"))
            
            # 2. Buat edges berdasarkan vendor yang muncul di package yang sama
            logger.info("🔗 Creating vendor co-occurrence edges...")
            
            result = await db.execute(text("""
                INSERT INTO graph_relationships (
                    source_id, target_id, relationship_type, 
                    weight, case_id, created_at
                )
                SELECT 
                    e1.id as source_id,
                    e2.id as target_id,
                    'vendor_cooccurrence' as relationship_type,
                    LEAST(COUNT(*) * 10 + 30, 100) as weight,
                    '446e216d-eb0e-487e-8e6b-ec943468ea20' as case_id,
                    NOW() as created_at
                FROM graph_entities e1
                JOIN graph_entities e2 ON e1.id < e2.id
                JOIN rup_paket_detailed r1 ON LOWER(r1.vendor_name) = LOWER(e1.name)
                JOIN rup_paket_detailed r2 ON LOWER(r2.vendor_name) = LOWER(e2.name)
                WHERE e1.entity_type = 'vendor' 
                  AND e2.entity_type = 'vendor'
                  AND r1.package_id = r2.package_id
                  AND r1.vendor_name != r2.vendor_name
                GROUP BY e1.id, e2.id
                HAVING COUNT(*) >= 1
                LIMIT 1000
            """))
            
            logger.info(f"  ✅ Created vendor co-occurrence edges")
            
            # 3. Buat edges berdasarkan kategori yang sama
            logger.info("📦 Creating category similarity edges...")
            
            result = await db.execute(text("""
                INSERT INTO graph_relationships (
                    source_id, target_id, relationship_type,
                    weight, case_id, created_at
                )
                SELECT 
                    e1.id as source_id,
                    e2.id as target_id,
                    'category_similarity' as relationship_type,
                    LEAST(COUNT(DISTINCT r1.category) * 15 + 20, 100) as weight,
                    '446e216d-eb0e-487e-8e6b-ec943468ea20' as case_id,
                    NOW() as created_at
                FROM graph_entities e1
                JOIN graph_entities e2 ON e1.id < e2.id
                JOIN rup_paket_detailed r1 ON LOWER(r1.vendor_name) = LOWER(e1.name)
                JOIN rup_paket_detailed r2 ON LOWER(r2.vendor_name) = LOWER(e2.name)
                WHERE e1.entity_type = 'vendor' 
                  AND e2.entity_type = 'vendor'
                  AND r1.category = r2.category
                  AND r1.vendor_name != r2.vendor_name
                GROUP BY e1.id, e2.id
                HAVING COUNT(DISTINCT r1.category) >= 1
                LIMIT 1000
            """))
            
            logger.info(f"  ✅ Created category similarity edges")
            
            # 4. Verifikasi
            result = await db.execute(text("""
                SELECT 
                    COUNT(*) as total_edges,
                    COUNT(DISTINCT relationship_type) as types,
                    ROUND(AVG(weight)::numeric, 2) as avg_weight
                FROM graph_relationships
            """))
            row = result.fetchone()
            
            logger.info(f"\n📊 GRAPH REBUILD COMPLETE:")
            logger.info(f"  Total Edges: {row[0]}")
            logger.info(f"  Relationship Types: {row[1]}")
            logger.info(f"  Average Weight: {row[2]:.2f}")
            
            # 5. Sample edges
            sample = await db.execute(text("""
                SELECT 
                    e1.name as source,
                    e2.name as target,
                    r.relationship_type,
                    r.weight
                FROM graph_relationships r
                JOIN graph_entities e1 ON r.source_id = e1.id
                JOIN graph_entities e2 ON r.target_id = e2.id
                LIMIT 5
            """))
            rows = sample.fetchall()
            logger.info("\n📋 SAMPLE EDGES:")
            for row in rows:
                logger.info(f"  {row[0]} -> {row[1]} ({row[2]}, weight: {row[3]})")
            
            await db.commit()
            logger.info("✅ Commit successful!")
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            await db.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(rebuild_graph_from_rup())
