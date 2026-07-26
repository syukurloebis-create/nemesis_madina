"""
Vendor Graph Builder - Builds relationships between vendors based on shared packages
FIXED: Removed ALL ::jsonb casts from SQL (use Python json.dumps + no cast)
"""

import asyncio
import json
import sys
from collections import defaultdict

sys.path.insert(0, '/app')

from backend.infrastructure.database import AsyncSessionLocal
from sqlalchemy import text


async def build_vendor_graph():
    """Build vendor graph from rup_paket_detailed data"""
    
    async with AsyncSessionLocal() as session:
        
        # Get all package-vendor relationships
        result = await session.execute(text("""
            SELECT 
                kode_paket,
                nama_penyedia,
                tahun_anggaran,
                total_nilai
            FROM rup_paket_detailed
            WHERE nama_penyedia IS NOT NULL
        """))
        
        rows = result.fetchall()
        
        if not rows:
            print("❌ No vendor data found")
            return None
        
        # Map packages to vendors
        package_vendors = defaultdict(list)
        vendor_packages = defaultdict(list)
        vendor_stats = defaultdict(lambda: {'package_count': 0, 'total_value': 0, 'years': set()})
        
        for row in rows:
            package_id = row[0]
            vendor = row[1]
            year = row[2]
            value = float(row[3]) if row[3] else 0
            
            package_vendors[package_id].append({
                'vendor': vendor,
                'year': year,
                'value': value
            })
            vendor_packages[vendor].append({
                'package_id': package_id,
                'year': year,
                'value': value
            })
            vendor_stats[vendor]['package_count'] += 1
            vendor_stats[vendor]['total_value'] += value
            if year:
                vendor_stats[vendor]['years'].add(year)
        
        # Build vendor-vendor edges based on shared packages
        edges = []
        vendors = list(vendor_packages.keys())
        
        print(f"📊 Building vendor graph for {len(vendors)} vendors...")
        
        for i, v1 in enumerate(vendors):
            pkg_set_1 = {p['package_id'] for p in vendor_packages[v1]}
            
            for v2 in vendors[i+1:]:
                pkg_set_2 = {p['package_id'] for p in vendor_packages[v2]}
                shared = pkg_set_1 & pkg_set_2
                
                if len(shared) >= 2:
                    weight = len(shared) / max(len(pkg_set_1), len(pkg_set_2))
                    
                    edges.append({
                        'source': v1,
                        'target': v2,
                        'shared_packages': len(shared),
                        'weight': round(weight, 4),
                        'shared_package_ids': list(shared)[:5]
                    })
        
        edges.sort(key=lambda x: x['shared_packages'], reverse=True)
        
        print(f"\n🏗️ Vendor Graph Summary:")
        print(f"   Vendors: {len(vendors)}")
        print(f"   Edges (>=2 shared packages): {len(edges)}")
        
        if edges:
            print(f"\n🤝 TOP 10 VENDOR COLLABORATIONS:")
            for edge in edges[:10]:
                print(f"   {edge['source'][:35]} ↔ {edge['target'][:35]}: {edge['shared_packages']} shared packages")
        
        return {
            'nodes': vendors,
            'edges': edges,
            'vendor_stats': dict(vendor_stats),
            'node_count': len(vendors),
            'edge_count': len(edges)
        }


async def insert_vendor_graph_to_db(graph_data):
    """Insert vendor graph to database tables - NO CAST IN SQL"""
    
    if not graph_data or not graph_data['nodes']:
        print("⚠️ No vendor data to insert")
        return
    
    async with AsyncSessionLocal() as session:
        
        # Clear existing vendor graph entities
        await session.execute(text("DELETE FROM graph_entities WHERE entity_type = 'vendor'"))
        await session.commit()
        
        # Insert vendor nodes
        print(f"\n📝 Inserting {len(graph_data['nodes'])} vendor nodes...")
        
        for vendor in graph_data['nodes']:
            stats = graph_data['vendor_stats'].get(vendor, {})
            extra_data = json.dumps({
                'package_count': stats.get('package_count', 0),
                'total_value': stats.get('total_value', 0),
                'years': list(stats.get('years', []))
            })
            
            # FIX: No ::jsonb cast - just pass as parameter
            await session.execute(text("""
                INSERT INTO graph_entities (id, name, entity_type, confidence, risk_score, first_seen, extra_data)
                VALUES (gen_random_uuid()::text, :name, 'vendor', 1.0, 0.0, NOW(), :extra_data)
            """), {
                'name': vendor,
                'extra_data': extra_data
            })
        
        await session.commit()
        print(f"   ✅ Inserted {len(graph_data['nodes'])} vendor nodes")
        
        # Insert vendor-vendor edges
        if graph_data['edges']:
            print(f"📝 Inserting {len(graph_data['edges'])} vendor edges...")
            
            for edge in graph_data['edges']:
                # Get source ID
                result = await session.execute(text("""
                    SELECT id FROM graph_entities WHERE name = :name AND entity_type = 'vendor'
                """), {'name': edge['source']})
                source_id = result.scalar()
                
                # Get target ID
                result = await session.execute(text("""
                    SELECT id FROM graph_entities WHERE name = :name AND entity_type = 'vendor'
                """), {'name': edge['target']})
                target_id = result.scalar()
                
                if source_id and target_id:
                    extra_data = json.dumps({
                        'shared_packages': edge['shared_packages'],
                        'sample_packages': edge['shared_package_ids']
                    })
                    
                    # FIX: No ::jsonb cast here either
                    await session.execute(text("""
                        INSERT INTO graph_relationships (
                            source_id, target_id, relationship_type, weight, extra_data
                        ) VALUES (
                            :source_id, :target_id, 'VENDOR_COLLUSION', :weight, :extra_data
                        )
                    """), {
                        'source_id': source_id,
                        'target_id': target_id,
                        'weight': edge['weight'],
                        'extra_data': extra_data
                    })
            
            await session.commit()
            print(f"   ✅ Inserted {len(graph_data['edges'])} vendor edges")
        else:
            print("   ⚠️ No vendor edges to insert")


async def verify_vendor_graph():
    """Verify vendor graph insertion"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(text("""
            SELECT COUNT(*) FROM graph_entities WHERE entity_type = 'vendor'
        """))
        node_count = result.scalar()
        
        result = await session.execute(text("""
            SELECT COUNT(*) FROM graph_relationships WHERE relationship_type = 'VENDOR_COLLUSION'
        """))
        edge_count = result.scalar()
        
        print(f"\n📊 VERIFICATION:")
        print(f"   Vendor nodes in graph_entities: {node_count}")
        print(f"   Vendor edges in graph_relationships: {edge_count}")


async def main():
    print("=" * 60)
    print("VENDOR GRAPH BUILDER (FIXED - NO CAST)")
    print("=" * 60)
    print()
    
    print("🔍 Building vendor graph from rup_paket_detailed...")
    graph = await build_vendor_graph()
    
    if not graph:
        print("❌ Failed to build vendor graph")
        return
    
    print("\n💾 Inserting vendor graph to database...")
    await insert_vendor_graph_to_db(graph)
    
    await verify_vendor_graph()
    
    print("\n" + "=" * 60)
    print("✅ VENDOR GRAPH BUILD COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
    async def build_vendor_graph(self, case_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Build vendor graph with optional case_id
        
        Args:
            case_id: Optional case_id to associate graph with
            
        Returns:
            Dictionary with build statistics
        """
        try:
            # ============ FIX: Track case_id ============
            if case_id:
                self.logger.info(f"Building graph for case: {case_id}")
            
            # Insert entities with case_id
            for vendor in vendors:
                entity_id = str(uuid.uuid4())
                await self.session.execute(
                    text("""
                        INSERT INTO graph_entities (
                            id, name, entity_type, case_id, 
                            confidence, risk_score, first_seen, extra_data
                        )
                        VALUES (
                            :id, :name, :entity_type, :case_id,
                            :confidence, :risk_score, :first_seen, :extra_data
                        )
                        ON CONFLICT (id) DO UPDATE SET
                            case_id = EXCLUDED.case_id,
                            confidence = EXCLUDED.confidence,
                            risk_score = EXCLUDED.risk_score,
                            last_seen = CURRENT_TIMESTAMP
                    """),
                    {
                        "id": entity_id,
                        "name": vendor['name'],
                        "entity_type": "vendor",
                        "case_id": case_id,  # FIX: Include case_id
                        "confidence": vendor.get('confidence', 0.5),
                        "risk_score": vendor.get('risk_score', 0),
                        "first_seen": datetime.now(),
                        "extra_data": json.dumps(vendor.get('extra_data', {}))
                    }
                )
            
            return {
                "entities_created": len(vendors),
                "relationships_created": len(relationships),
                "case_id": case_id,
                "status": "success"
            }
            
        except Exception as e:
            self.logger.error(f"Error building vendor graph: {str(e)}")
            raise
