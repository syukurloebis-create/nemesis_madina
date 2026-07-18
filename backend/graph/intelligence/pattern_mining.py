"""
Pattern Mining
Mendeteksi pola mencurigakan dalam graph
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging
import uuid

from .temporal_graph import temporal_graph, TemporalGraph

logger = logging.getLogger(__name__)


@dataclass
class SuspiciousPattern:
    """Suspicious pattern detected"""
    pattern_id: str
    type: str
    confidence: float
    description: str
    actors: List[str]
    evidence: List[Dict[str, Any]]
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pattern_id": self.pattern_id,
            "type": self.type,
            "confidence": self.confidence,
            "description": self.description,
            "actors": self.actors,
            "evidence": self.evidence,
            "timestamp": self.timestamp.isoformat()
        }


class PatternMiner:
    """
    Pattern Mining Engine
    Mendeteksi pola mencurigakan dalam graph
    """

    def __init__(self, graph: Optional[TemporalGraph] = None):
        self.graph = graph or temporal_graph
        self.patterns: List[SuspiciousPattern] = []

    def _get_neighbors(self, node_id: str) -> List[str]:
        """Get all neighbors of a node"""
        neighbors = set()
        for target, _ in self.graph.adjacency.get(node_id, []):
            neighbors.add(target)
        for source, _ in self.graph.reverse_adjacency.get(node_id, []):
            neighbors.add(source)
        return list(neighbors)

    def _get_all_nodes_in_cycles(self, cycles: List[List[str]]) -> Set[str]:
        """Get all nodes that are part of cycles"""
        nodes = set()
        for cycle in cycles:
            nodes.update(cycle)
        return nodes

    def _dfs_cycle(
        self,
        start: str,
        current: str,
        visited: Set[str],
        path: List[str],
        cycles: List[List[str]]
    ) -> None:
        """DFS for cycle detection"""
        for neighbor in self._get_neighbors(current):
            if neighbor == start and len(path) >= 3:
                cycles.append(path[:])
            elif neighbor not in visited:
                visited.add(neighbor)
                self._dfs_cycle(start, neighbor, visited, path + [neighbor], cycles)
                visited.remove(neighbor)

    def _find_chain(self, start_node: str, max_length: int = 5) -> List[str]:
        """Find a chain starting from a node"""
        chain = [start_node]
        current = start_node
        visited = {start_node}

        while len(chain) < max_length:
            neighbors = self._get_neighbors(current)
            candidate = None
            for neighbor in neighbors:
                if neighbor not in visited:
                    if len(self._get_neighbors(neighbor)) >= 2:
                        candidate = neighbor
                        break

            if candidate:
                chain.append(candidate)
                visited.add(candidate)
                current = candidate
            else:
                break

        return chain

    def _find_cycles(self, start: str, visited: Set[str]) -> List[List[str]]:
        """Find cycles starting from a node"""
        cycles = []
        self._dfs_cycle(start, start, {start}, [start], cycles)
        visited.update(self._get_all_nodes_in_cycles(cycles))
        return cycles

    def mine_all(self) -> List[SuspiciousPattern]:
        """Mine all suspicious patterns"""
        self.patterns = []

        # 1. Star pattern
        for node_id, node in self.graph.nodes.items():
            neighbors = self._get_neighbors(node_id)
            if len(neighbors) >= 5:
                score = len(neighbors) / 10
                if score > 0.5:
                    self.patterns.append(SuspiciousPattern(
                        pattern_id=f"star_{node_id}",
                        type="star_pattern",
                        confidence=min(score, 1.0),
                        description=f"Star pattern detected with {node.label} as hub ({len(neighbors)} connections)",
                        actors=[node_id] + neighbors[:5],
                        evidence=[{
                            "type": "star_pattern",
                            "hub": node_id,
                            "connections": len(neighbors),
                            "neighbors": neighbors[:10]
                        }]
                    ))

        # 2. Chain pattern
        for start_node in self.graph.nodes:
            chain = self._find_chain(start_node, max_length=5)
            if len(chain) >= 3:
                types = [self.graph.nodes[n].type for n in chain if n in self.graph.nodes]
                if types and len(set(types)) >= 2:
                    self.patterns.append(SuspiciousPattern(
                        pattern_id=f"chain_{start_node}_{len(chain)}",
                        type="chain_pattern",
                        confidence=0.6 + len(chain) * 0.05,
                        description=f"Chain pattern detected with {len(chain)} nodes",
                        actors=chain,
                        evidence=[{
                            "type": "chain_pattern",
                            "chain": chain,
                            "length": len(chain)
                        }]
                    ))

        # 3. Cycle pattern
        visited = set()
        for node_id in self.graph.nodes:
            if node_id not in visited:
                cycles = self._find_cycles(node_id, visited)
                for cycle in cycles:
                    if len(cycle) >= 3:
                        self.patterns.append(SuspiciousPattern(
                            pattern_id=f"cycle_{node_id}_{len(cycle)}",
                            type="cycle_pattern",
                            confidence=0.7 + len(cycle) * 0.02,
                            description=f"Cycle pattern detected with {len(cycle)} nodes",
                            actors=cycle,
                            evidence=[{
                                "type": "cycle_pattern",
                                "cycle": cycle,
                                "length": len(cycle)
                            }]
                        ))

        # 4. Temporal anomaly
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        for node_id, node in self.graph.nodes.items():
            if node.first_seen >= week_ago:
                neighbors = self._get_neighbors(node_id)
                if len(neighbors) >= 3:
                    self.patterns.append(SuspiciousPattern(
                        pattern_id=f"new_active_{node_id}",
                        type="temporal_anomaly",
                        confidence=min(len(neighbors) / 5, 1.0),
                        description=f"Newly appeared node with high activity: {node.label}",
                        actors=[node_id],
                        evidence=[{
                            "type": "temporal_anomaly",
                            "node": node_id,
                            "connections": len(neighbors),
                            "first_seen": node.first_seen.isoformat()
                        }]
                    ))

        # Sort by confidence
        self.patterns.sort(key=lambda x: x.confidence, reverse=True)
        return self.patterns

    def get_patterns_by_type(self, pattern_type: str) -> List[SuspiciousPattern]:
        """Get patterns by type"""
        return [p for p in self.patterns if p.type == pattern_type]

    def get_high_confidence_patterns(self, threshold: float = 0.7) -> List[SuspiciousPattern]:
        """Get patterns with confidence above threshold"""
        return [p for p in self.patterns if p.confidence >= threshold]

    def get_summary(self) -> Dict[str, Any]:
        """Get pattern mining summary"""
        return {
            "total_patterns": len(self.patterns),
            "by_type": {t: len(self.get_patterns_by_type(t))
                       for t in set(p.type for p in self.patterns)},
            "high_confidence": len(self.get_high_confidence_patterns()),
            "avg_confidence": sum(p.confidence for p in self.patterns) / len(self.patterns) if self.patterns else 0,
            "top_patterns": [p.to_dict() for p in self.patterns[:5]]
        }


# Singleton instance
pattern_miner = PatternMiner()