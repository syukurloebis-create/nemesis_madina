#!/usr/bin/env python3
"""
FORCE BACKFILL - Menggunakan SQLAlchemy Core
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

async def force_backfill():
    """Force backfill case_id untuk semua data graph"""
    
    TARGET_CASE = "446e216d-eb0e-487e-8e6b-ec943468ea20"
    
    async for db in get_db():
        try:
            # 1. CEK DATA NULL
            logger.info("🔍 CEK DATA NULL:")
            
            result = await db.execute(text("""
                SELECT COUNT(*) FROM graph_entities WHERE case_id IS NULL
            """))
            null_entities = result.scalar()
            logger.info(f"  Entities NULL: {null_entities}")
            
            result = await db.execute(text("""
                SELECT COUNT(*) FROM graph_relationships WHERE case_id IS NULL
            """))
            null_relationships = result.scalar()
            logger.info(f"  Relationships NULL: {null_relationships}")
            
            # 2. UPDATE ENTITIES - FORCE
            logger.info("\n🔄 FORCE UPDATE ENTITIES...")
            
            # Gunakan UPDATE dengan WHERE yang sangat spesifik
            result = await db.execute(text("""
                UPDATE graph_entities 
                SET case_id = :case_id 
                WHERE case_id IS NULL
            """), {"case_id": TARGET_CASE})
            
            updated_entities = result.rowcount
            logger.info(f"  ✅ Updated {updated_entities} entities")
            
            # 3. UPDATE RELATIONSHIPS - FORCE
            logger.info("\n🔄 FORCE UPDATE RELATIONSHIPS...")
            
            result = await db.execute(text("""
                UPDATE graph_relationships 
                SET case_id = :case_id 
                WHERE case_id IS NULL
            """), {"case_id": TARGET_CASE})
            
            updated_relationships = result.rowcount
            logger.info(f"  ✅ Updated {updated_relationships} relationships")
            
            # 4. COMMIT
            await db.commit()
            logger.info("\n✅ COMMIT SUCCESS!")
            
            # 5. VERIFIKASI
            logger.info("\n📊 VERIFIKASI SETELAH UPDATE:")
            
            result = await db.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN case_id = :case_id THEN 1 END) as with_case_id
                FROM graph_entities
            """), {"case_id": TARGET_CASE})
            row = result.fetchone()
            logger.info(f"  Entities: {row[0]} total, {row[1]} with case_id")
            
            result = await db.execute(text("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN case_id = :case_id THEN 1 END) as with_case_id
                FROM graph_relationships
            """), {"case_id": TARGET_CASE})
            row = result.fetchone()
            logger.info(f"  Relationships: {row[0]} total, {row[1]} with case_id")
            
            # 6. SAMPLE DATA
            logger.info("\n📊 SAMPLE DATA:")
            result = await db.execute(text("""
                SELECT id, name, entity_type, case_id 
                FROM graph_entities 
                WHERE case_id = :case_id
                LIMIT 5
            """), {"case_id": TARGET_CASE})
            rows = result.fetchall()
            for row in rows:
                logger.info(f"  - {row[1]} ({row[2]}): {row[3]}")
            
            if updated_entities > 0 and updated_relationships > 0:
                logger.info("\n✅✅✅ BACKFILL COMPLETED SUCCESSFULLY!")
            else:
                logger.warning("\n⚠️ Tidak ada data yang diupdate. Cek kembali kondisi WHERE.")
                
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            await db.rollback()
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(force_backfill())
