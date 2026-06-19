# backend/intelligence/graph/detectors/collusion_detector.py

"""
Collusion Detector with Deduplication
"""

from typing import List, Dict, Any
from collections import defaultdict
import hashlib
import logging

logger = logging.getLogger(__name__)


class CollusionDetector:
    
    def __init__(self):
        self._seen_patterns = set()
    
    def _hash_pattern(self, pattern: Dict) -> str:
        entities = sorted(pattern.get("entities", []))
        pattern_type = pattern.get("type", "unknown")
        key = f"{pattern_type}|{'|'.join(entities)}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def _is_duplicate(self, pattern: Dict) -> bool:
        pattern_hash = self._hash_pattern(pattern)
        if pattern_hash in self._seen_patterns:
            return True
        self._seen_patterns.add(pattern_hash)
        return False
    
    def reset(self):
        self._seen_patterns.clear()
    
    def detect_triangles(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        self.reset()
        
        if len(nodes) < 3 or len(edges) < 3:
            return []
        
        adj = defaultdict(set)
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                adj[source].add(target)
        
        node_ids = set(n["id"] for n in nodes)
        node_name_map = {n["id"]: n["name"] for n in nodes}
        
        triangles = []
        
        for a in node_ids:
            for b in adj.get(a, set()):
                if b not in node_ids:
                    continue
                for c in adj.get(b, set()):
                    if c not in node_ids:
                        continue
                    if a in adj.get(c, set()):
                        triangle_nodes = sorted([a, b, c])
                        entity_names = [node_name_map.get(n, n) for n in triangle_nodes]
                        
                        total_amount = 0
                        for edge in edges:
                            props = edge.get("properties", {})
                            if edge["source"] == a and edge["target"] == b:
                                total_amount += props.get("amount", 0)
                            if edge["source"] == b and edge["target"] == c:
                                total_amount += props.get("amount", 0)
                            if edge["source"] == c and edge["target"] == a:
                                total_amount += props.get("amount", 0)
                        
                        pattern = {
                            "type": "financial_triangle",
                            "entities": entity_names,
                            "node_ids": triangle_nodes,
                            "cycle": f"{entity_names[0]} → {entity_names[1]} → {entity_names[2]} → {entity_names[0]}",
                            "total_amount": total_amount,
                            "confidence": 0.85,
                            "severity": min(1.0, total_amount / 10000000000) if total_amount else 0.7,
                            "description": f"Circular financial flow detected: {' → '.join(entity_names)} → {entity_names[0]}",
                        }
                        
                        if not self._is_duplicate(pattern):
                            triangles.append(pattern)
                            logger.info(f"New triangle detected: {pattern['cycle'][:50]}...")
                        else:
                            logger.debug(f"Skipping duplicate triangle")
                        
                        break
                else:
                    continue
                break
        
        logger.info(f"{len(triangles)} unique triangles found")
        return triangles
    
    def calculate_collusion_risk(self, triangles: List[Dict]) -> float:
        if not triangles:
            return 0.0
        
        triangle_risk = min(len(triangles) * 25, 50)
        severity_sum = sum(t.get("severity", 0) for t in triangles)
        severity_bonus = min(50, (severity_sum / len(triangles)) * 50) if triangles else 0
        
        return min(100, triangle_risk + severity_bonus)


collusion_detector = CollusionDetector()