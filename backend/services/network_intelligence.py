"""
Network Intelligence Service - Sederhana
"""
import psycopg2
from typing import Dict, Any, List

DB_CONFIG = {
    'host': 'postgres',
    'port': 5432,
    'database': 'nemesis_db',
    'user': 'nemesis',
    'password': 'nemesis123'
}

def get_key_actors():
    """Get key actors from graph"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                ge.id,
                ge.name,
                ge.risk_score,
                COUNT(gr.id) as connection_count
            FROM graph_entities ge
            LEFT JOIN graph_relationships gr ON ge.id = gr.source_id OR ge.id = gr.target_id
            GROUP BY ge.id
            ORDER BY connection_count DESC
            LIMIT 10
        """)
        rows = cur.fetchall()
        return [
            {
                "id": row[0],
                "name": row[1],
                "risk_score": float(row[2]) if row[2] else 0,
                "connections": row[3]
            }
            for row in rows
        ]
    finally:
        cur.close()
        conn.close()

def get_communities():
    """Detect communities (simple grouping)"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    try:
        # Get all relationships
        cur.execute("SELECT source_id, target_id FROM graph_relationships")
        edges = cur.fetchall()
        
        # Build graph and find components
        graph = {}
        for src, tgt in edges:
            if src not in graph:
                graph[src] = set()
            if tgt not in graph:
                graph[tgt] = set()
            graph[src].add(tgt)
            graph[tgt].add(src)
        
        # Find connected components
        visited = set()
        communities = []
        for node in graph:
            if node not in visited:
                queue = [node]
                visited.add(node)
                community = []
                while queue:
                    current = queue.pop(0)
                    community.append(current)
                    for neighbor in graph.get(current, []):
                        if neighbor not in visited:
                            visited.add(neighbor)
                            queue.append(neighbor)
                communities.append(community)
        
        return {
            "total_communities": len(communities),
            "largest_size": max([len(c) for c in communities]) if communities else 0
        }
    finally:
        cur.close()
        conn.close()
