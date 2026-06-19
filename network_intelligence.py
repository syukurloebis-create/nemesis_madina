"""
Network Intelligence Service
- Community detection
- Risk propagation
- Key actor analysis
- Collusion detection
"""
import psycopg2
from typing import Dict, Any, List, Set
from collections import defaultdict
import math

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

class NetworkIntelligence:
    """Service untuk network analysis"""

    def get_vendor_network(self, vendor_id: str = None) -> Dict[str, Any]:
        """Get complete vendor network"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            if vendor_id:
                cur.execute("""
                    SELECT id, name, entity_type, risk_score
                    FROM graph_entities
                    WHERE id = %s OR id IN (
                        SELECT target_id FROM graph_relationships WHERE source_id = %s
                        UNION SELECT source_id FROM graph_relationships WHERE target_id = %s
                    )
                """, (vendor_id, vendor_id, vendor_id))
            else:
                cur.execute("""
                    SELECT id, name, entity_type, risk_score
                    FROM graph_entities
                    LIMIT 100
                """)
            
            nodes = cur.fetchall()
            
            # Get relationships
            cur.execute("""
                SELECT source_id, target_id, relationship_type, weight
                FROM graph_relationships
                WHERE source_id IN (SELECT id FROM graph_entities)
                AND target_id IN (SELECT id FROM graph_entities)
            """)
            edges = cur.fetchall()
            
            return {
                "nodes": [
                    {
                        "id": row[0],
                        "name": row[1],
                        "type": row[2],
                        "risk_score": float(row[3]) if row[3] else 0
                    }
                    for row in nodes
                ],
                "edges": [
                    {
                        "source": row[0],
                        "target": row[1],
                        "type": row[2],
                        "weight": float(row[3]) if row[3] else 1.0
                    }
                    for row in edges
                ],
                "total_nodes": len(nodes),
                "total_edges": len(edges)
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

    def detect_communities(self) -> Dict[str, Any]:
        """Detect communities using simple clustering"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Get all relationships
            cur.execute("""
                SELECT source_id, target_id, weight
                FROM graph_relationships
            """)
            edges = cur.fetchall()
            
            # Build adjacency
            graph = defaultdict(set)
            for edge in edges:
                graph[edge[0]].add(edge[1])
                graph[edge[1]].add(edge[0])
            
            # Simple community detection (connected components)
            visited = set()
            communities = []
            
            for node in graph:
                if node not in visited:
                    # BFS
                    queue = [node]
                    visited.add(node)
                    community = []
                    
                    while queue:
                        current = queue.pop(0)
                        community.append(current)
                        for neighbor in graph[current]:
                            if neighbor not in visited:
                                visited.add(neighbor)
                                queue.append(neighbor)
                    
                    communities.append(community)
            
            # Get entity names
            communities_with_names = []
            for comm in communities:
                cur.execute(
                    "SELECT id, name FROM graph_entities WHERE id = ANY(%s)",
                    (comm,)
                )
                entities = cur.fetchall()
                communities_with_names.append({
                    "size": len(comm),
                    "entities": [
                        {"id": row[0], "name": row[1]} for row in entities
                    ]
                })
            
            return {
                "total_communities": len(communities),
                "communities": communities_with_names,
                "largest_community": max(communities, key=len) if communities else []
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

    def propagate_risk(self, source_vendor_id: str) -> Dict[str, Any]:
        """Propagate risk from source vendor to connected entities"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Get source risk
            cur.execute("""
                SELECT risk_score FROM graph_entities WHERE id = %s
            """, (source_vendor_id,))
            source = cur.fetchone()
            
            if not source:
                return {"error": "Vendor not found"}
            
            source_risk = float(source[0]) if source[0] else 0
            
            # Get all relationships
            cur.execute("""
                SELECT 
                    CASE WHEN source_id = %s THEN target_id ELSE source_id END as connected_id,
                    weight,
                    relationship_type
                FROM graph_relationships
                WHERE source_id = %s OR target_id = %s
            """, (source_vendor_id, source_vendor_id, source_vendor_id))
            edges = cur.fetchall()
            
            propagated = []
            for edge in edges:
                connected_id = edge[0]
                weight = float(edge[1]) if edge[1] else 1.0
                rel_type = edge[2]
                
                # Calculate propagated risk (decay factor: 0.7)
                propagated_risk = source_risk * weight * 0.7
                
                # Get entity info
                cur.execute("""
                    SELECT id, name, risk_score FROM graph_entities WHERE id = %s
                """, (connected_id,))
                entity = cur.fetchone()
                
                if entity:
                    propagated.append({
                        "entity_id": entity[0],
                        "entity_name": entity[1],
                        "current_risk": float(entity[2]) if entity[2] else 0,
                        "propagated_risk": round(propagated_risk, 2),
                        "relationship_type": rel_type,
                        "weight": weight
                    })
            
            return {
                "source_id": source_vendor_id,
                "source_risk": source_risk,
                "propagated_to": len(propagated),
                "results": propagated
            }
            
        except Exception as e:
            return {"error": str(e)}
        finally:
            cur.close()
            conn.close()

    def find_key_actors(self) -> List[Dict[str, Any]]:
        """Find key actors using degree centrality"""
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        try:
            # Calculate degree (number of connections)
            cur.execute("""
                SELECT 
                    entity_id,
                    COUNT(*) as degree,
                    AVG(weight) as avg_weight
                FROM (
                    SELECT source_id as entity_id, weight FROM graph_relationships
                    UNION ALL
                    SELECT target_id as entity_id, weight FROM graph_relationships
                ) as all_edges
                GROUP BY entity_id
                ORDER BY degree DESC
                LIMIT 10
            """)
            rows = cur.fetchall()
            
            key_actors = []
            for row in rows:
                cur.execute("""
                    SELECT id, name, risk_score FROM graph_entities WHERE id = %s
                """, (row[0],))
                entity = cur.fetchone()
                
                if entity:
                    key_actors.append({
                        "entity_id": entity[0],
                        "name": entity[1],
                        "risk_score": float(entity[2]) if entity[2] else 0,
                        "degree": row[1],
                        "avg_weight": float(row[2]) if row[2] else 0
                    })
            
            return key_actors
            
        except Exception as e:
            return [{"error": str(e)}]
        finally:
            cur.close()
            conn.close()

network = NetworkIntelligence()

def get_vendor_network(vendor_id: str = None) -> Dict[str, Any]:
    return network.get_vendor_network(vendor_id)

def detect_communities() -> Dict[str, Any]:
    return network.detect_communities()

def propagate_risk(vendor_id: str) -> Dict[str, Any]:
    return network.propagate_risk(vendor_id)

def find_key_actors() -> List[Dict[str, Any]]:
    return network.find_key_actors()
