#!/usr/bin/env python3
"""
NEMESIS FASE 3 - Create Lineage Tracking System
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

LINEAGE_DIR = PROJECT_ROOT / "backend" / "lineage"

def create_lineage_structure():
    """Create lineage directory structure"""
    print("\n[1/5] Creating lineage directory...")
    LINEAGE_DIR.mkdir(parents=True, exist_ok=True)
    return True

def create_init():
    """Create __init__.py for lineage module"""
    print("\n[2/5] Creating lineage __init__.py...")
    
    content = '''"""
NEMESIS Lineage Module - Track Data Lineage
"""

from backend.lineage.tracker import LineageTracker, LineageNode, LineageEdge
from backend.lineage.verifier import LineageVerifier
from backend.lineage.graph import LineageGraph
from backend.lineage.exporter import LineageExporter

__all__ = [
    'LineageTracker',
    'LineageNode',
    'LineageEdge',
    'LineageVerifier',
    'LineageGraph',
    'LineageExporter'
]
'''
    
    file_path = LINEAGE_DIR / "__init__.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_tracker():
    """Create tracker.py - core lineage tracking"""
    print("\n[3/5] Creating lineage tracker...")
    
    content = '''"""
Lineage Tracker - Track Data Lineage
"""

from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict
import uuid


@dataclass
class LineageNode:
    """Node in lineage graph"""
    id: str
    type: str  # input, transform, decision, output, evidence, event
    name: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    hash: Optional[str] = None


@dataclass
class LineageEdge:
    """Edge in lineage graph"""
    source: str
    target: str
    relationship: str  # produces, consumes, derives, verifies
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class LineageTracker:
    """Track lineage of data through the system"""
    
    def __init__(self):
        self.nodes: Dict[str, LineageNode] = {}
        self.edges: List[LineageEdge] = []
        self._current_context: Optional[str] = None
        self._context_stack: List[str] = []
    
    def create_node(
        self,
        node_type: str,
        name: str,
        metadata: Dict[str, Any] = None,
        node_id: str = None
    ) -> LineageNode:
        """Create a new lineage node"""
        node = LineageNode(
            id=node_id or str(uuid.uuid4()),
            type=node_type,
            name=name,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.nodes[node.id] = node
        
        # Link to current context if exists
        if self._current_context:
            self.add_edge(self._current_context, node.id, "contains")
        
        return node
    
    def add_edge(
        self,
        source: str,
        target: str,
        relationship: str,
        metadata: Dict[str, Any] = None
    ) -> LineageEdge:
        """Add edge between nodes"""
        if source not in self.nodes:
            raise ValueError(f"Source node {source} not found")
        if target not in self.nodes:
            raise ValueError(f"Target node {target} not found")
        
        edge = LineageEdge(
            source=source,
            target=target,
            relationship=relationship,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.edges.append(edge)
        
        # Update node relationships
        self.nodes[source].outputs.append(target)
        self.nodes[target].inputs.append(source)
        
        return edge
    
    def start_context(self, context_id: str, metadata: Dict[str, Any] = None):
        """Start a new lineage context (e.g., a processing pipeline)"""
        self._context_stack.append(self._current_context)
        self._current_context = context_id
        
        # Create context node if not exists
        if context_id not in self.nodes:
            self.create_node(
                node_type="context",
                name=context_id,
                metadata=metadata,
                node_id=context_id
            )
    
    def end_context(self) -> Optional[str]:
        """End current lineage context"""
        self._current_context = self._context_stack.pop() if self._context_stack else None
        return self._current_context
    
    def get_lineage(self, node_id: str, depth: int = 10) -> List[LineageNode]:
        """Get full lineage (ancestors) of a node"""
        lineage = []
        visited = set()
        
        def traverse(current_id: str, current_depth: int):
            if current_depth > depth or current_id in visited:
                return
            visited.add(current_id)
            
            node = self.nodes.get(current_id)
            if node:
                lineage.append(node)
                for input_id in node.inputs:
                    traverse(input_id, current_depth + 1)
        
        traverse(node_id, 0)
        return lineage
    
    def get_impact(self, node_id: str, depth: int = 10) -> List[LineageNode]:
        """Get all nodes impacted by a node (descendants)"""
        impact = []
        visited = set()
        
        def traverse(current_id: str, current_depth: int):
            if current_depth > depth or current_id in visited:
                return
            visited.add(current_id)
            
            node = self.nodes.get(current_id)
            if node:
                impact.append(node)
                for output_id in node.outputs:
                    traverse(output_id, current_depth + 1)
        
        traverse(node_id, 0)
        return impact
    
    def get_path(self, source: str, target: str) -> Optional[List[str]]:
        """Find path between two nodes using BFS"""
        if source not in self.nodes or target not in self.nodes:
            return None
        
        from collections import deque
        queue = deque([(source, [source])])
        visited = {source}
        
        while queue:
            node, path = queue.popleft()
            
            if node == target:
                return path
            
            for next_node in self.nodes[node].outputs:
                if next_node not in visited:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
        
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get lineage metrics"""
        return {
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "node_types": self._count_node_types(),
            "relationship_types": self._count_relationships(),
            "avg_fan_in": self._avg_fan_in(),
            "avg_fan_out": self._avg_fan_out()
        }
    
    def _count_node_types(self) -> Dict[str, int]:
        counts = defaultdict(int)
        for node in self.nodes.values():
            counts[node.type] += 1
        return dict(counts)
    
    def _count_relationships(self) -> Dict[str, int]:
        counts = defaultdict(int)
        for edge in self.edges:
            counts[edge.relationship] += 1
        return dict(counts)
    
    def _avg_fan_in(self) -> float:
        if not self.nodes:
            return 0.0
        total = sum(len(node.inputs) for node in self.nodes.values())
        return total / len(self.nodes)
    
    def _avg_fan_out(self) -> float:
        if not self.nodes:
            return 0.0
        total = sum(len(node.outputs) for node in self.nodes.values())
        return total / len(self.nodes)
    
    def clear(self):
        """Clear all lineage data"""
        self.nodes.clear()
        self.edges.clear()
        self._current_context = None
        self._context_stack.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Export lineage to dictionary"""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type,
                    "name": n.name,
                    "timestamp": n.timestamp.isoformat(),
                    "metadata": n.metadata,
                    "inputs": n.inputs,
                    "outputs": n.outputs,
                    "hash": n.hash
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "source": e.source,
                    "target": e.target,
                    "relationship": e.relationship,
                    "timestamp": e.timestamp.isoformat(),
                    "metadata": e.metadata
                }
                for e in self.edges
            ],
            "metrics": self.get_metrics()
        }
'''
    
    file_path = LINEAGE_DIR / "tracker.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_verifier():
    """Create verifier.py - lineage verification"""
    print("\n[4/5] Creating lineage verifier...")
    
    content = '''"""
Lineage Verifier - Verify Lineage Integrity
"""

from typing import List, Dict, Any, Tuple
from backend.lineage.tracker import LineageTracker, LineageNode
from backend.evidence.hashing import EvidenceHasher


class LineageVerifier:
    """Verify lineage integrity and completeness"""
    
    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
        self.hasher = EvidenceHasher()
    
    def verify_node_integrity(self, node_id: str) -> Tuple[bool, str]:
        """Verify a node's hash matches its content"""
        node = self.tracker.nodes.get(node_id)
        if not node:
            return False, f"Node {node_id} not found"
        
        if node.hash:
            # Recompute hash
            node_data = f"{node.id}{node.type}{node.name}{node.timestamp.isoformat()}"
            computed = self.hasher.quick_hash(node_data)
            
            if computed != node.hash:
                return False, f"Hash mismatch for node {node_id}"
        
        return True, "OK"
    
    def verify_chain_completeness(self, start_id: str, end_id: str) -> Dict[str, Any]:
        """Verify that a complete path exists between nodes"""
        path = self.tracker.get_path(start_id, end_id)
        
        if not path:
            return {
                "complete": False,
                "reason": f"No path found from {start_id} to {end_id}"
            }
        
        # Verify each step
        issues = []
        for i in range(len(path) - 1):
            source = path[i]
            target = path[i + 1]
            
            # Check edge exists
            edge_exists = any(
                e.source == source and e.target == target
                for e in self.tracker.edges
            )
            
            if not edge_exists:
                issues.append(f"Missing edge: {source} -> {target}")
        
        return {
            "complete": len(issues) == 0,
            "path": path,
            "path_length": len(path) - 1,
            "issues": issues
        }
    
    def verify_orphan_nodes(self) -> List[str]:
        """Find nodes with no connections"""
        orphans = []
        for node_id, node in self.tracker.nodes.items():
            if not node.inputs and not node.outputs:
                orphans.append(node_id)
        return orphans
    
    def verify_circular_references(self) -> List[List[str]]:
        """Detect circular references in lineage"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def dfs(node_id: str, path: List[str]):
            if node_id in rec_stack:
                # Found cycle
                cycle_start = path.index(node_id)
                cycles.append(path[cycle_start:] + [node_id])
                return
            
            if node_id in visited:
                return
            
            visited.add(node_id)
            rec_stack.add(node_id)
            path.append(node_id)
            
            node = self.tracker.nodes.get(node_id)
            if node:
                for output in node.outputs:
                    dfs(output, path.copy())
            
            rec_stack.remove(node_id)
        
        for node_id in self.tracker.nodes:
            if node_id not in visited:
                dfs(node_id, [])
        
        return cycles
    
    def generate_integrity_report(self) -> str:
        """Generate lineage integrity report"""
        report = []
        report.append("=" * 60)
        report.append("LINEAGE INTEGRITY REPORT")
        report.append("=" * 60)
        
        metrics = self.tracker.get_metrics()
        report.append(f"Total Nodes: {metrics['node_count']}")
        report.append(f"Total Edges: {metrics['edge_count']}")
        report.append(f"Node Types: {metrics['node_types']}")
        report.append(f"Relationship Types: {metrics['relationship_types']}")
        report.append("")
        
        # Orphan nodes
        orphans = self.verify_orphan_nodes()
        if orphans:
            report.append(f"ORPHAN NODES ({len(orphans)}):")
            for o in orphans[:10]:
                node = self.tracker.nodes.get(o)
                report.append(f"  - {o} ({node.type if node else 'unknown'})")
        else:
            report.append("Orphan Nodes: None")
        
        # Circular references
        cycles = self.verify_circular_references()
        if cycles:
            report.append(f"")
            report.append(f"CIRCULAR REFERENCES ({len(cycles)}):")
            for cycle in cycles[:5]:
                report.append(f"  - {' -> '.join(cycle)}")
        else:
            report.append("Circular References: None")
        
        report.append("")
        report.append("=" * 60)
        report.append("Verification Complete")
        
        return "\\n".join(report)
'''
    
    file_path = LINEAGE_DIR / "verifier.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_graph_and_exporter():
    """Create graph.py and exporter.py"""
    print("\n[5/5] Creating graph and exporter...")
    
    # graph.py
    graph_content = '''"""
Lineage Graph - Visualization and Query Support
"""

from typing import List, Dict, Any, Set, Optional
from backend.lineage.tracker import LineageTracker, LineageNode, LineageEdge


class LineageGraph:
    """Lineage graph with query capabilities"""
    
    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
    
    def get_subgraph(self, node_ids: Set[str]) -> Dict[str, Any]:
        """Extract subgraph containing specified nodes"""
        subgraph = {
            "nodes": [],
            "edges": []
        }
        
        # Add nodes
        for node_id in node_ids:
            if node_id in self.tracker.nodes:
                node = self.tracker.nodes[node_id]
                subgraph["nodes"].append({
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "timestamp": node.timestamp.isoformat()
                })
        
        # Add edges between these nodes
        for edge in self.tracker.edges:
            if edge.source in node_ids and edge.target in node_ids:
                subgraph["edges"].append({
                    "source": edge.source,
                    "target": edge.target,
                    "relationship": edge.relationship
                })
        
        return subgraph
    
    def get_upstream_dependencies(self, node_id: str, depth: int = 3) -> List[Dict]:
        """Get upstream dependencies (inputs)"""
        dependencies = []
        
        def collect(current_id: str, current_depth: int):
            if current_depth > depth:
                return
            
            node = self.tracker.nodes.get(current_id)
            if node:
                dependencies.append({
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "depth": current_depth
                })
                
                for input_id in node.inputs:
                    collect(input_id, current_depth + 1)
        
        collect(node_id, 0)
        return dependencies
    
    def get_downstream_dependents(self, node_id: str, depth: int = 3) -> List[Dict]:
        """Get downstream dependents (outputs)"""
        dependents = []
        
        def collect(current_id: str, current_depth: int):
            if current_depth > depth:
                return
            
            node = self.tracker.nodes.get(current_id)
            if node:
                dependents.append({
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "depth": current_depth
                })
                
                for output_id in node.outputs:
                    collect(output_id, current_depth + 1)
        
        collect(node_id, 0)
        return dependents
    
    def get_critical_path(self, start_id: str, end_id: str) -> Optional[List[str]]:
        """Get critical path (longest path) between nodes"""
        # Simplified: use get_path from tracker
        return self.tracker.get_path(start_id, end_id)
    
    def export_for_visualization(self) -> Dict[str, Any]:
        """Export graph for visualization (D3.js, Cytoscape.js)"""
        return {
            "nodes": [
                {
                    "data": {
                        "id": n.id,
                        "label": n.name,
                        "type": n.type
                    }
                }
                for n in self.tracker.nodes.values()
            ],
            "edges": [
                {
                    "data": {
                        "id": f"{e.source}_{e.target}",
                        "source": e.source,
                        "target": e.target,
                        "label": e.relationship
                    }
                }
                for e in self.tracker.edges
            ]
        }
'''
    
    file_path = LINEAGE_DIR / "graph.py"
    file_path.write_text(graph_content)
    print(f"  [OK] Created: {file_path}")
    
    # exporter.py
    exporter_content = '''"""
Lineage Exporter - Export Lineage Data
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List
from backend.lineage.tracker import LineageTracker


class LineageExporter:
    """Export lineage data to various formats"""
    
    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
    
    def to_json(self, file_path: Path) -> bool:
        """Export lineage to JSON file"""
        try:
            data = self.tracker.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def to_csv(self, file_path: Path) -> bool:
        """Export nodes and edges to CSV files"""
        try:
            base_path = Path(file_path).with_suffix('')
            
            # Export nodes
            nodes_path = f"{base_path}_nodes.csv"
            with open(nodes_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'type', 'name', 'timestamp', 'inputs', 'outputs'])
                for node in self.tracker.nodes.values():
                    writer.writerow([
                        node.id, node.type, node.name, node.timestamp.isoformat(),
                        ';'.join(node.inputs), ';'.join(node.outputs)
                    ])
            
            # Export edges
            edges_path = f"{base_path}_edges.csv"
            with open(edges_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['source', 'target', 'relationship', 'timestamp'])
                for edge in self.tracker.edges:
                    writer.writerow([
                        edge.source, edge.target, edge.relationship, edge.timestamp.isoformat()
                    ])
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def to_graphviz(self, file_path: Path) -> bool:
        """Export lineage to Graphviz DOT format"""
        try:
            lines = ['digraph Lineage {']
            lines.append('    rankdir=TB;')
            lines.append('    node [shape=box, style=filled, fillcolor=lightblue];')
            
            # Add nodes
            for node in self.tracker.nodes.values():
                label = f"{node.name}\n({node.type})"
                lines.append(f'    "{node.id}" [label="{label}"];')
            
            # Add edges
            for edge in self.tracker.edges:
                lines.append(f'    "{edge.source}" -> "{edge.target}" [label="{edge.relationship}"];')
            
            lines.append('}')
            
            with open(file_path, 'w') as f:
                f.write('\\n'.join(lines))
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
'''
    
    file_path = LINEAGE_DIR / "exporter.py"
    file_path.write_text(exporter_content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 3: CREATE LINEAGE TRACKING SYSTEM")
    print("="*60)
    
    create_lineage_structure()
    create_init()
    create_tracker()
    create_verifier()
    create_graph_and_exporter()
    
    print("\n" + "="*60)
    print("[OK] Lineage tracking system created")
    print(f"   Location: {LINEAGE_DIR}")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())