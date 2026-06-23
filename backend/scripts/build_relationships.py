#!/usr/bin/env python3
"""
Run Relationship Builder - FIXED IMPORT
"""
import asyncio
import sys
import os

# ============ FIX: Tambahkan /app ke sys.path ============
BASE_DIR = "/app"
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# ============ FIX: Import yang benar ============
from database import get_db
from graph.services.relationship_builder import RelationshipBuilder
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    async for db in get_db():
        builder = RelationshipBuilder(db)
        results = await builder.build_all_relationships()
        logger.info(f"\n📊 FINAL RESULTS:")
        logger.info(f"  Shared Package: {results['shared_package']}")
        logger.info(f"  Vendor Similarity: {results['vendor_similarity']}")
        logger.info(f"  Method Similarity: {results['method_similarity']}")
        logger.info(f"  Financial Similarity: {results['financial_similarity']}")
        logger.info(f"  TOTAL: {results['total']}")

if __name__ == "__main__":
    asyncio.run(main())
