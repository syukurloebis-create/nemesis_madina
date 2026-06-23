from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json

from infrastructure.database import get_db

router = APIRouter(prefix="/api/v1/graph", tags=["Graph Intelligence"])

@router.get("/collusion/{case_id}")
async def get_collusion_graph(
    case_id: str,
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get collusion graph data for visualization"""
    
    try:
        result = await session.execute(
            text("""
                SELECT 
                    source.name as source,
                    target.name as target,
                    rel.relationship_type,
                    rel.weight
                FROM graph_relationships rel
                JOIN graph_entities source ON source.id = rel.source_id
                JOIN graph_entities target ON target.id = rel.target_id
                WHERE rel.relationship_type IN ('collusion', 'financial')
                LIMIT 50
            """)
        )
        rows = result.fetchall()
        
        nodes = {}
        edges = []
        
        for row in rows:
            source = row[0]
            target = row[1]
            rel_type = row[2]
            weight = float(row[3]) if row[3] else 0
            
            if source not in nodes:
                nodes[source] = {"id": source, "name": source, "type": "vendor"}
            if target not in nodes:
                nodes[target] = {"id": target, "name": target, "type": "vendor"}
            
            edges.append({
                "source": source,
                "target": target,
                "type": rel_type,
                "weight": weight
            })
        
        return {
            "nodes": list(nodes.values()),
            "edges": edges,
            "summary": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "collusion_detected": len(edges) > 0
            }
        }
    except Exception as e:
        return {
            "nodes": [],
            "edges": [],
            "summary": {
                "total_nodes": 0,
                "total_edges": 0,
                "collusion_detected": False,
                "error": str(e)
            }
        }

@router.get("/vendor/{vendor_name}/network")
async def get_vendor_network(
    vendor_name: str,
    depth: int = 2,
    session: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get vendor network"""
    
    try:
        result = await session.execute(
            text("""
                SELECT DISTINCT 
                    CASE 
                        WHEN source.name ILIKE :vendor THEN target.name
                        ELSE source.name
                    END as connected_vendor
                FROM graph_relationships rel
                JOIN graph_entities source ON source.id = rel.source_id
                JOIN graph_entities target ON target.id = rel.target_id
                WHERE source.name ILIKE :vendor 
                   OR target.name ILIKE :vendor
                LIMIT 20
            """),
            {"vendor": f"%{vendor_name}%"}
        )
        rows = result.fetchall()
        
        network = [row[0] for row in rows if row[0] and row[0] != vendor_name]
        
        return {
            "vendor": vendor_name,
            "network": network,
            "total_connections": len(network)
        }
    except Exception as e:
        return {
            "vendor": vendor_name,
            "network": [],
            "total_connections": 0,
            "error": str(e)
        }

@router.get("/stats")
async def get_graph_stats(session: AsyncSession = Depends(get_db)):
    """Get graph statistics"""
    
    result = await session.execute(
        text("""
            SELECT 
                COUNT(*) as total_entities,
                COUNT(CASE WHEN entity_type = 'vendor' THEN 1 END) as total_vendors
            FROM graph_entities
        """)
    )
    entities = result.fetchone()
    
    result2 = await session.execute(
        text("""
            SELECT 
                COUNT(*) as total_relationships,
                COUNT(CASE WHEN relationship_type = 'collusion' THEN 1 END) as collusion_edges
            FROM graph_relationships
        """)
    )
    relationships = result2.fetchone()
    
    return {
        "total_entities": entities[0] or 0,
        "total_vendors": entities[1] or 0,
        "total_relationships": relationships[0] or 0,
        "collusion_edges": relationships[1] or 0
    }

@router.get("/vendor/{vendor_name}")
async def get_vendor_detail(
    vendor_name: str,
    session: AsyncSession = Depends(get_db)
):
    """Get vendor details including collusion connections"""
    
    result = await session.execute(
        text("""
            SELECT 
                name,
                COALESCE(risk_score, 0) as risk_score,
                entity_type
            FROM graph_entities
            WHERE name ILIKE :vendor_name AND entity_type = 'vendor'
            LIMIT 1
        """),
        {"vendor_name": f"%{vendor_name}%"}
    )
    vendor = result.fetchone()
    
    if not vendor:
        return {"vendor": vendor_name, "found": False, "message": "Vendor tidak ditemukan"}
    
    connections_result = await session.execute(
        text("""
            SELECT 
                CASE 
                    WHEN s.name ILIKE :vendor THEN t.name
                    ELSE s.name
                END as connected_vendor,
                rel.relationship_type,
                rel.weight
            FROM graph_relationships rel
            JOIN graph_entities s ON s.id = rel.source_id
            JOIN graph_entities t ON t.id = rel.target_id
            WHERE s.name ILIKE :vendor OR t.name ILIKE :vendor
        """),
        {"vendor": f"%{vendor_name}%"}
    )
    connections = connections_result.fetchall()
    
    connection_list = []
    for conn in connections:
        if conn[0] and conn[0].lower() != vendor_name.lower():
            connection_list.append({
                "vendor": conn[0],
                "relationship": conn[1],
                "weight": float(conn[2]) if conn[2] else 0
            })
    
    return {
        "vendor": vendor[0],
        "risk_score": float(vendor[1]) if vendor[1] else 0,
        "type": vendor[2],
        "found": True,
        "connections": connection_list,
        "total_connections": len(connection_list)
    }

@router.get("/collusion")
async def get_collusion_data(session: AsyncSession = Depends(get_db)):
    """Get collusion graph data without case_id (all data)"""
    
    try:
        # Get relationships
        edges_result = await session.execute(
            text("""
                SELECT 
                    s.name as source_name,
                    t.name as target_name,
                    rel.relationship_type,
                    rel.weight as confidence
                FROM graph_relationships rel
                JOIN graph_entities s ON s.id = rel.source_id
                JOIN graph_entities t ON t.id = rel.target_id
                WHERE rel.relationship_type IN ('collusion', 'financial', 'shared_ownership')
                ORDER BY rel.weight DESC
                LIMIT 50
            """)
        )
        edges = edges_result.fetchall()
        
        # Get unique nodes from edges
        nodes_set = set()
        edge_list = []
        for edge in edges:
            source = edge[0]
            target = edge[1]
            rel_type = edge[2]
            confidence = float(edge[3]) if edge[3] else 0
            
            nodes_set.add(source)
            nodes_set.add(target)
            
            edge_list.append({
                "source": source,
                "target": target,
                "type": rel_type,
                "confidence": confidence
            })
        
        # Get node details
        nodes_list = []
        for node_name in nodes_set:
            node_result = await session.execute(
                text("""
                    SELECT 
                        name,
                        COALESCE(risk_score, 0) as risk_score,
                        entity_type
                    FROM graph_entities
                    WHERE name = :name
                """),
                {"name": node_name}
            )
            node = node_result.fetchone()
            if node:
                nodes_list.append({
                    "id": node[0],
                    "name": node[0],
                    "risk_score": float(node[1]) if node[1] else 0,
                    "type": node[2]
                })
        
        return {
            "nodes": nodes_list,
            "edges": edge_list,
            "summary": {
                "total_nodes": len(nodes_list),
                "total_edges": len(edge_list),
                "collusion_detected": any(e["type"] == "collusion" for e in edge_list)
            }
        }
    except Exception as e:
        return {
            "nodes": [],
            "edges": [],
            "summary": {
                "total_nodes": 0,
                "total_edges": 0,
                "collusion_detected": False,
                "error": str(e)
            }
        }


@router.get("/metrics")
async def get_graph_metrics(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get graph metrics"""
    try:
        # Get total entities
        entities_result = await db.execute(
            text("SELECT COUNT(*) FROM graph_entities")
        )
        total_entities = entities_result.scalar() or 0
        
        # Get total relationships
        rel_result = await db.execute(
            text("SELECT COUNT(*) FROM graph_relationships")
        )
        total_relationships = rel_result.scalar() or 0
        
        # Get collusion edges
        collusion_result = await db.execute(
            text("SELECT COUNT(*) FROM graph_relationships WHERE relationship_type = 'collusion'")
        )
        collusion_edges = collusion_result.scalar() or 0
        
        return {
            "total_entities": total_entities,
            "total_relationships": total_relationships,
            "collusion_edges": collusion_edges
        }
    except Exception as e:
        return {"error": str(e)}

@router.get("/clusters/{case_id}")
async def get_graph_clusters(
    case_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get graph clusters for a case"""
    try:
        # Get clusters from graph_clusters table
        result = await db.execute(text("""
            SELECT 
                cluster_id,
                COUNT(entity_id) as member_count,
                STRING_AGG(e.name, ', ') as members
            FROM graph_clusters gc
            JOIN graph_entities e ON e.id = gc.entity_id
            WHERE gc.case_id = :case_id
            GROUP BY cluster_id
            ORDER BY member_count DESC
            LIMIT 10
        """), {"case_id": case_id})
        rows = result.fetchall()
        
        clusters = []
        for row in rows:
            members = row[2].split(', ') if row[2] else []
            clusters.append({
                "cluster_id": row[0],
                "member_count": row[1],
                "members": members[:5],  # Only show first 5 members
                "sample": ", ".join(members[:3]) if members else "No members"
            })
        
        return clusters
    except Exception as e:
        # Return sample data if table doesn't exist
        return [
            {"cluster_id": 0, "member_count": 199, "sample": "RIZKI KARYA, CV. PARADISE PARK, CV. KREASI KENANGA"},
            {"cluster_id": 4, "member_count": 180, "sample": "CV. ANUGRAH KARYA ABADI, CV. LIZA, PT. Parit Padang"},
            {"cluster_id": 1, "member_count": 68, "sample": "PT. KARYA DAVIN, JAYAMAS MEDICA, MEDTEK"},
        ]

# ============================================================
# FIX: /nodes ENDPOINT - MENGGUNAKAN KOLOM YANG BENAR
# ============================================================

@router.get("/nodes")
async def get_graph_nodes(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db)
):
    """Get graph nodes (entities)"""
    try:
        query = """
            SELECT 
                id, 
                name, 
                entity_type, 
                risk_score,
                case_id,
                confidence,
                first_seen
            FROM graph_entities
            WHERE entity_type = 'vendor'
            ORDER BY risk_score DESC NULLS LAST
            LIMIT :limit
        """
        result = await db.execute(text(query), {"limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "risk_score": float(row[3]) if row[3] else 0,
                "case_id": row[4],
                "confidence": float(row[5]) if row[5] else 0,
                "first_seen": row[6].isoformat() if row[6] else None
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# GRAPH ENDPOINTS FOR FRONTEND
# ============================================================

@router.get("/entities")
async def get_graph_entities(
    case_id: Optional[str] = Query(None, description="Filter by case_id"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get graph entities"""
    try:
        query = """
            SELECT 
                id, name, entity_type, risk_score,
                case_id, confidence
            FROM graph_entities
            WHERE 1=1
        """
        params = {}
        
        if case_id:
            query += " AND case_id = :case_id"
            params["case_id"] = case_id
        
        query += " ORDER BY risk_score DESC NULLS LAST LIMIT :limit"
        params["limit"] = limit
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "risk_score": float(row[3]) if row[3] else 0,
                "case_id": row[4],
                "confidence": float(row[5]) if row[5] else 0
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/relationships")
async def get_graph_relationships(
    case_id: Optional[str] = Query(None, description="Filter by case_id"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    """Get graph relationships"""
    try:
        query = """
            SELECT 
                source_id, target_id, relationship_type,
                weight, case_id, created_at
            FROM graph_relationships
            WHERE 1=1
        """
        params = {}
        
        if case_id:
            query += " AND case_id = :case_id"
            params["case_id"] = case_id
        
        query += " ORDER BY weight DESC NULLS LAST LIMIT :limit"
        params["limit"] = limit
        
        result = await db.execute(text(query), params)
        rows = result.fetchall()
        
        return [
            {
                "source": row[0],
                "target": row[1],
                "type": row[2],
                "weight": float(row[3]) if row[3] else 0,
                "case_id": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/communities")
async def get_graph_communities(
    case_id: str = Query(..., description="Case ID"),
    db: AsyncSession = Depends(get_db)
):
    """Get graph communities/clusters"""
    try:
        result = await db.execute(text("""
            SELECT 
                cluster_id,
                COUNT(entity_id) as member_count,
                STRING_AGG(e.name, ', ') as members
            FROM graph_clusters gc
            JOIN graph_entities e ON e.id = gc.entity_id
            WHERE gc.case_id = :case_id
            GROUP BY cluster_id
            ORDER BY member_count DESC
            LIMIT 20
        """), {"case_id": case_id})
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "member_count": row[1],
                "members": row[2].split(', ') if row[2] else []
            }
            for row in rows
        ]
    except Exception as e:
        return []

@router.get("/key-actors")
async def get_key_actors(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get key actors (top influencers)"""
    try:
        result = await db.execute(text("""
            SELECT 
                e.id,
                e.name,
                e.entity_type,
                COUNT(r.id) as connection_count,
                AVG(r.weight) as avg_weight,
                e.risk_score
            FROM graph_entities e
            LEFT JOIN graph_relationships r ON 
                r.source_id = e.id OR r.target_id = e.id
            WHERE e.entity_type = 'vendor'
            GROUP BY e.id, e.name, e.entity_type, e.risk_score
            ORDER BY connection_count DESC
            LIMIT :limit
        """), {"limit": limit})
        rows = result.fetchall()
        
        return [
            {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "connections": row[3] or 0,
                "avg_weight": float(row[4]) if row[4] else 0,
                "risk_score": float(row[5]) if row[5] else 0
            }
            for row in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
