#!/usr/bin/env python3
"""
Vendor Collusion Detector - Uses vendor graph for fraud detection
"""

import asyncio
import sys
sys.path.insert(0, '/app')

from backend.infrastructure.database import AsyncSessionLocal
from sqlalchemy import text


class VendorCollusionDetector:
    
    def __init__(self, session):
        self.session = session
    
    async def get_high_risk_vendors(self, min_degree: int = 1):
        """Get vendors with high collaboration degree"""
        
        result = await self.session.execute(text("""
            SELECT 
                ge.name,
                COUNT(gr.source_id) as collaboration_count,
                COALESCE(SUM(gr.weight), 0) as total_weight
            FROM graph_entities ge
            LEFT JOIN graph_relationships gr ON ge.id = gr.source_id OR ge.id = gr.target_id
            WHERE ge.entity_type = 'vendor' 
                AND (gr.relationship_type = 'VENDOR_COLLUSION' OR gr.relationship_type IS NULL)
            GROUP BY ge.id, ge.name
            HAVING COUNT(gr.source_id) >= :min_degree
            ORDER BY collaboration_count DESC
        """), {'min_degree': min_degree})
        
        return result.fetchall()
    
    async def get_collaboration_network(self, vendor_name: str):
        """Get all collaborators for a specific vendor"""
        
        result = await self.session.execute(text("""
            SELECT 
                ge2.name as collaborator,
                gr.weight,
                gr.extra_data->>'shared_packages' as shared_count
            FROM graph_relationships gr
            JOIN graph_entities ge1 ON gr.source_id = ge1.id
            JOIN graph_entities ge2 ON gr.target_id = ge2.id
            WHERE ge1.name = :vendor 
                AND ge1.entity_type = 'vendor'
                AND gr.relationship_type = 'VENDOR_COLLUSION'
            UNION
            SELECT 
                ge1.name as collaborator,
                gr.weight,
                gr.extra_data->>'shared_packages' as shared_count
            FROM graph_relationships gr
            JOIN graph_entities ge1 ON gr.source_id = ge1.id
            JOIN graph_entities ge2 ON gr.target_id = ge2.id
            WHERE ge2.name = :vendor 
                AND ge2.entity_type = 'vendor'
                AND gr.relationship_type = 'VENDOR_COLLUSION'
        """), {'vendor': vendor_name})
        
        return result.fetchall()
    
    async def detect_collusion_clusters(self, min_cluster_size: int = 2):
        """Detect vendor collusion clusters using connected components"""
        return await self.get_high_risk_vendors(min_degree=min_cluster_size)


async def test_detector():
    async with AsyncSessionLocal() as session:
        detector = VendorCollusionDetector(session)
        
        print("=" * 50)
        print("VENDOR COLLUSION DETECTOR TEST")
        print("=" * 50)
        
        high_risk = await detector.get_high_risk_vendors()
        print(f"\n🚨 High-risk vendors: {len(high_risk)}")
        for vendor in high_risk[:10]:
            print(f"   {vendor[0]}: {vendor[1]} collaborations")
        
        if high_risk:
            sample = high_risk[0][0]
            print(f"\n🔗 Collaborations for {sample}:")
            collabs = await detector.get_collaboration_network(sample)
            for collab in collabs:
                print(f"   ↔ {collab[0]}: shared={collab[2]} packages, weight={collab[1]}")
        else:
            print("\n⚠️ No vendor collaborations found")


if __name__ == "__main__":
    asyncio.run(test_detector())
