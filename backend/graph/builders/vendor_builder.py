"""
Vendor Graph Builder — Pure graph construction.

Replicates legacy vendor_graph_builder.py algorithm EXACTLY.
NO persistence, NO UUID, NO SQL.
"""

import logging
from typing import Dict, Any, List
from collections import defaultdict

from backend.graph.dto.graph_candidate import GraphCandidate, GraphNode, GraphEdge
from backend.graph.interfaces.graph_builder import IGraphBuilder

logger = logging.getLogger(__name__)


class VendorGraphBuilder(IGraphBuilder):
    """
    Vendor graph builder — pure graph construction.
    
    Replicates the legacy vendor_graph_builder.py algorithm EXACTLY.
    
    Algorithm:
    1. Build vendor → packages mapping
    2. Calculate vendor statistics (package_count, total_value, years)
    3. Build vendor → vendor edges (shared packages >= 2)
    4. Calculate edge weight = shared / max(pkg1, pkg2)
    
    NO persistence, NO UUID, NO SQL.
    """
    
    def builder_id(self) -> str:
        return "vendor"
    
    async def build(self, source_data: Dict[str, Any]) -> GraphCandidate:
        """
        Build vendor graph from source data.
        
        Args:
            source_data: Dictionary containing 'rows' from rup_paket_detailed
            
        Returns:
            Pure GraphCandidate — NO persistence details.
        """
        rows = source_data.get('rows', [])
        
        if not rows:
            logger.info("No vendor data found")
            return GraphCandidate()
        
        logger.info(f"Building vendor graph from {len(rows)} rows")
        
        # 1. Build vendor → packages mapping (EXACTLY like legacy)
        vendor_packages: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        vendor_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'package_count': 0,
            'total_value': 0,
            'years': set()
        })
        
        for row in rows:
            package_id = row.get('kode_paket')
            vendor = row.get('nama_penyedia')
            year = row.get('tahun_anggaran')
            value = float(row.get('total_nilai', 0) or 0)
            
            vendor_packages[vendor].append({
                'package_id': package_id,
                'year': year,
                'value': value
            })
            vendor_stats[vendor]['package_count'] += 1
            vendor_stats[vendor]['total_value'] += value
            if year:
                vendor_stats[vendor]['years'].add(year)
        
        # 2. Build nodes
        nodes: List[GraphNode] = []
        for vendor, stats in vendor_stats.items():
            nodes.append(GraphNode(
                name=vendor,
                node_type='vendor',
                external_id=vendor,
                properties={
                    'package_count': stats['package_count'],
                    'total_value': stats['total_value'],
                    'years': list(stats['years']),
                },
                confidence=1.0,
                risk_score=0.0,
            ))
        
        # 3. Build edges (EXACTLY like legacy)
        vendors = list(vendor_packages.keys())
        edges: List[GraphEdge] = []
        
        for i, v1 in enumerate(vendors):
            pkg_set_1 = {p['package_id'] for p in vendor_packages[v1]}
            for v2 in vendors[i+1:]:
                pkg_set_2 = {p['package_id'] for p in vendor_packages[v2]}
                shared = pkg_set_1 & pkg_set_2
                if len(shared) >= 2:
                    weight = len(shared) / max(len(pkg_set_1), len(pkg_set_2))
                    edges.append(GraphEdge(
                        source=v1,
                        target=v2,
                        relationship_type='vendor_cooccurrence',
                        weight=round(weight, 4),
                        properties={
                            'shared_packages': len(shared),
                            'sample_packages': list(shared)[:5],
                        }
                    ))
        
        # 4. Sort by shared_packages descending (same as legacy)
        edges.sort(
            key=lambda e: e.properties.get('shared_packages', 0),
            reverse=True
        )
        
        logger.info(f"Built vendor graph: {len(nodes)} nodes, {len(edges)} edges")
        
        return GraphCandidate(
            nodes=nodes,
            edges=edges,
            metadata={
                'builder_id': 'vendor',
                'node_count': len(nodes),
                'edge_count': len(edges),
                'total_value': sum(s['total_value'] for s in vendor_stats.values()),
                'total_packages': sum(s['package_count'] for s in vendor_stats.values()),
            }
        )
