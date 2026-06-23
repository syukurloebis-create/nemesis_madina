#!/usr/bin/env python3
"""
NEMESIS INTELLIGENCE LAYER - FULL SYSTEM TEST (FIXED DEGREE QUERY)
"""

import asyncio
import sys

sys.path.insert(0, '.')

from infrastructure.database import AsyncSessionLocal
from sqlalchemy import text


async def test_intelligence_full():
    print("=" * 50)
    print("NEMESIS INTELLIGENCE LAYER - FULL TEST")
    print("=" * 50)
    print()

    async with AsyncSessionLocal() as session:
        
        # TEST 1: ENTITY DISTRIBUTION
        print("📊 ENTITY DISTRIBUTION:")
        result = await session.execute(
            text("SELECT entity_type, COUNT(*) FROM graph_entities GROUP BY entity_type")
        )
        for row in result:
            print(f"   {row[0]}: {row[1]}")
        print()

        # TEST 2: SAMPLE ENTITIES
        print("📋 SAMPLE ENTITIES:")
        result = await session.execute(
            text("SELECT entity_type, name FROM graph_entities LIMIT 10")
        )
        for row in result:
            print(f"   {row[0]}: {row[1]}")
        print()

        # TEST 3: RELATIONSHIP STATISTICS
        print("🔗 RELATIONSHIPS:")
        result = await session.execute(text("SELECT COUNT(*) FROM graph_relationships"))
        edge_count = result.scalar()
        print(f"   Total edges: {edge_count}")

        result = await session.execute(text("""
            SELECT MIN(weight), AVG(weight), MAX(weight) 
            FROM graph_relationships
        """))
        row = result.first()
        if row and row[0] is not None:
            print(f"   Weight range: {row[0]:.2f} - {row[2]:.2f} (avg: {row[1]:.2f})")
        print()

        # TEST 4: SAMPLE RELATIONSHIPS
        print("📋 SAMPLE RELATIONSHIPS:")
        result = await session.execute(text("""
            SELECT source_id, target_id, relationship_type, weight 
            FROM graph_relationships LIMIT 5
        """))
        for row in result:
            print(f"   {row[0]} -{row[2]}-> {row[1]}")
        print()

        # TEST 5: TOP 10 HIGHEST DEGREE NODES (FIXED QUERY!)
        print("🎯 TOP 10 HIGHEST DEGREE NODES:")
        result = await session.execute(text("""
            SELECT 
                ge.name,
                COUNT(gr.source_id) as degree
            FROM graph_entities ge
            LEFT JOIN graph_relationships gr ON ge.id = gr.source_id OR ge.id = gr.target_id
            GROUP BY ge.id, ge.name
            ORDER BY degree DESC
            LIMIT 10
        """))
        
        for row in result:
            print(f"   {row[0]}: {row[1]} connections")
        print()

        # TEST 6: POTENTIAL DUPLICATES
        print("🔍 POTENTIAL DUPLICATES (normalization needed):")
        result = await session.execute(text("""
            SELECT 
                LOWER(TRIM(name)) as normalized,
                COUNT(*) as count,
                ARRAY_AGG(name) as variants
            FROM graph_entities
            GROUP BY LOWER(TRIM(name))
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
        """))
        
        duplicate_count = 0
        for row in result:
            duplicate_count += 1
            variants = row[2][:3] if row[2] else []
            print(f"   {row[0]}: {row[1]} occurrences -> {variants}")
        
        if duplicate_count == 0:
            print("   No duplicates found")
        print()

        # TEST 7: COLLUSION DETECTION
        print("🚨 COLLUSION DETECTION:")
        try:
            from graph.relationship_graph import RelationshipGraph
            from intelligence.graph.collusion_detector import CollusionDetector
            
            result = await session.execute(
                text("SELECT source_id, target_id, weight FROM graph_relationships")
            )
            edges = result.fetchall()
            
            if edges:
                graph = RelationshipGraph()
                for edge in edges:
                    if edge[0] not in graph.nodes:
                        graph.add_node(edge[0], edge[0])
                    if edge[1] not in graph.nodes:
                        graph.add_node(edge[1], edge[1])
                    graph.add_edge(edge[0], edge[1], "RELATED", weight=edge[2] or 1.0)
                
                detector = CollusionDetector(graph)
                detections = detector.detect(threshold=0.45)
                
                if detections:
                    print(f"   Found {len(detections)} suspicious nodes:")
                    for d in detections[:10]:
                        print(f"   - {d['node']}: score={d['score']:.3f}, degree={d.get('degree', 0)}")
                else:
                    print("   No collusion detected")
            else:
                print("   No edges found")
        except Exception as e:
            print(f"   ⚠️ Detection error: {e}")
        print()

        print("=" * 50)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_intelligence_full())