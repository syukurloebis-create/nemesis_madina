"""
Lineage Verifier - Verify Lineage Integrity
"""

from typing import List, Dict, Any, Tuple
from lineage.tracker import LineageTracker, LineageNode
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
        
        return "\n".join(report)
