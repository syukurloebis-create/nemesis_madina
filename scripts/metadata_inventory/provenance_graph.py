# provenance_graph.py
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
import json

@dataclass
class ProvenanceNode:
    """A node in the provenance graph."""
    id: str
    type: str  # "artifact", "node", "finding", "decision"
    name: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    parents: List[str] = field(default_factory=list)
    children: List[str] = field(default_factory=list)

@dataclass
class ProvenanceEdge:
    """An edge in the provenance graph."""
    source: str
    target: str
    type: str  # "produces", "uses", "supports", "leads_to"

class ProvenanceGraph:
    """Graph tracking provenance from decision to artifact."""
    
    def __init__(self):
        self.nodes: Dict[str, ProvenanceNode] = {}
        self.edges: List[ProvenanceEdge] = []
    
    def add_node(self, node: ProvenanceNode) -> None:
        """Add a node to the graph."""
        self.nodes[node.id] = node
    
    def add_edge(self, edge: ProvenanceEdge) -> None:
        """Add an edge to the graph."""
        self.edges.append(edge)
        # Update parent/child relationships
        if edge.source in self.nodes and edge.target in self.nodes:
            if edge.target not in self.nodes[edge.source].children:
                self.nodes[edge.source].children.append(edge.target)
            if edge.source not in self.nodes[edge.target].parents:
                self.nodes[edge.target].parents.append(edge.source)
    
    def get_path(self, from_id: str, to_id: str) -> List[str]:
        """Get path between two nodes."""
        visited = set()
        path = []
        
        def dfs(current: str, target: str) -> bool:
            if current == target:
                return True
            if current in visited:
                return False
            visited.add(current)
            path.append(current)
            
            for child in self.nodes.get(current, ProvenanceNode(id="", type="", name="")).children:
                if dfs(child, target):
                    return True
            
            path.pop()
            return False
        
        if dfs(from_id, to_id):
            return path
        return []
    
    def get_decision_provenance(self, decision_id: str) -> Dict[str, Any]:
        """Get full provenance for a decision."""
        if decision_id not in self.nodes:
            return {"error": "Decision not found"}
        
        decision = self.nodes[decision_id]
        
        # Collect all findings supporting this decision
        findings = []
        for child_id in decision.children:
            child = self.nodes.get(child_id)
            if child and child.type == "finding":
                findings.append(child.name)
        
        # Collect all evidence supporting findings
        evidence = []
        for finding_id in decision.children:
            finding_node = self.nodes.get(finding_id)
            if finding_node:
                for child_id in finding_node.children:
                    child = self.nodes.get(child_id)
                    if child and child.type == "evidence":
                        evidence.append(child.name)
        
        # Collect all artifacts supporting evidence
        artifacts = []
        for evidence_id in [e for e in evidence if e in self.nodes]:
            evidence_node = self.nodes.get(evidence_id)
            if evidence_node:
                for child_id in evidence_node.children:
                    child = self.nodes.get(child_id)
                    if child and child.type == "artifact":
                        artifacts.append(child.name)
        
        return {
            "decision": decision.name,
            "findings": findings,
            "evidence": evidence,
            "artifacts": artifacts,
            "path": self.get_path(decision_id, artifacts[0] if artifacts else "")
        }
    
    def to_json(self) -> str:
        """Export graph to JSON."""
        data = {
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type,
                    "name": n.name,
                    "metadata": n.metadata,
                    "parents": n.parents,
                    "children": n.children
                }
                for n in self.nodes.values()
            ],
            "edges": [
                {"source": e.source, "target": e.target, "type": e.type}
                for e in self.edges
            ]
        }
        return json.dumps(data, indent=2)