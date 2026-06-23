# graph/analytics/pagerank.py - PageRank Intelligence
import logging
import networkx as nx
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

logger = logging.getLogger(__name__)

class PageRankEngine:
    """Calculate PageRank scores for graph entities"""
    
    def __init__(self, session: AsyncSession, case_id: str):
        self.session = session
        self.case_id = case_id
    
    async def calculate_pagerank(self) -> Dict[str, float]:
        """Calculate PageRank for all entities"""
        logger.info("📊 Calculating PageRank...")
        
        # 1. Fetch edges
        result = await self.session.execute(text("""
            SELECT source_id, target_id, weight
            FROM graph_relationships
            WHERE case_id = :case_id
        """), {"case_id": self.case_id})
        edges = result.fetchall()
        
        if not edges:
            logger.warning("No edges found for PageRank")
            return {}
        
        # 2. Build NetworkX graph
        G = nx.DiGraph()
        for edge in edges:
            G.add_edge(edge[0], edge[1], weight=edge[2] or 1.0)
        
        # 3. Calculate PageRank
        pagerank = nx.pagerank(G, weight='weight')
        
        # 4. Save to database
        for entity_id, score in pagerank.items():
            await self.session.execute(text("""
                INSERT INTO graph_node_scores (entity_id, pagerank, calculated_at)
                VALUES (:entity_id, :pagerank, NOW())
                ON CONFLICT (entity_id) DO UPDATE SET
                    pagerank = EXCLUDED.pagerank,
                    calculated_at = NOW()
            """), {"entity_id": entity_id, "pagerank": score})
        
        await self.session.commit()
        
        logger.info(f"  ✅ PageRank calculated for {len(pagerank)} entities")
        return pagerank
