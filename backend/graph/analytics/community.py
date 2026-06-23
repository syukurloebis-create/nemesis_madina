# graph/analytics/community.py - Community Detection
import logging
import networkx as nx
import community.community_louvain as community_louvain
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class CommunityDetector:
    """Detect communities in graph using Louvain algorithm"""
    
    def __init__(self, session: AsyncSession, case_id: str):
        self.session = session
        self.case_id = case_id
    
    async def detect_communities(self) -> Dict[int, List[str]]:
        """Detect communities using Louvain"""
        logger.info("🔍 Detecting communities...")
        
        # 1. Fetch edges
        result = await self.session.execute(text("""
            SELECT source_id, target_id, weight
            FROM graph_relationships
            WHERE case_id = :case_id
        """), {"case_id": self.case_id})
        edges = result.fetchall()
        
        if not edges:
            return {}
        
        # 2. Build graph (undirected for community detection)
        G = nx.Graph()
        for edge in edges:
            G.add_edge(edge[0], edge[1], weight=edge[2] or 1.0)
        
        # 3. Detect communities
        partition = community_louvain.best_partition(G, weight='weight')
        
        # 4. Save to database
        for entity_id, cluster_id in partition.items():
            await self.session.execute(text("""
                INSERT INTO graph_clusters (entity_id, cluster_id, created_at)
                VALUES (:entity_id, :cluster_id, NOW())
                ON CONFLICT (entity_id) DO UPDATE SET
                    cluster_id = EXCLUDED.cluster_id,
                    created_at = NOW()
            """), {"entity_id": entity_id, "cluster_id": cluster_id})
        
        await self.session.commit()
        
        # 5. Group by cluster
        communities = {}
        for entity_id, cluster_id in partition.items():
            if cluster_id not in communities:
                communities[cluster_id] = []
            communities[cluster_id].append(entity_id)
        
        logger.info(f"  ✅ Found {len(communities)} communities")
        return communities
