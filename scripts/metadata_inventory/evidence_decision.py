# evidence_decision.py
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

class Confidence(Enum):
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.9
    CERTAIN = 1.0

@dataclass
class Evidence:
    """Evidence supporting a finding."""
    source: str  # Layer/Node that produced this evidence
    description: str
    details: Dict[str, Any]
    confidence: Confidence

@dataclass
class Finding:
    """A finding with evidence and confidence."""
    type: str
    severity: str  # INFO, LOW, MEDIUM, HIGH, CRITICAL
    description: str
    evidence: List[Evidence]
    confidence: Confidence
    recommendation: Optional[str] = None

@dataclass
class DecisionNode:
    """Node in decision graph."""
    name: str
    condition: str
    findings: List[Finding]
    children: List['DecisionNode'] = field(default_factory=list)
    decision: Optional[str] = None
    confidence: float = 0.0

class EvidenceDecisionGraph:
    """Evidence-driven decision graph."""
    
    def __init__(self):
        self.root: Optional[DecisionNode] = None
    
    def build(self, findings: List[Finding]) -> DecisionNode:
        """Build decision graph from findings."""
        # Group findings by severity
        critical = [f for f in findings if f.severity == "CRITICAL"]
        high = [f for f in findings if f.severity == "HIGH"]
        medium = [f for f in findings if f.severity == "MEDIUM"]
        low = [f for f in findings if f.severity == "LOW"]
        info = [f for f in findings if f.severity == "INFO"]
        
        # Build decision tree
        root = DecisionNode(
            name="System Health",
            condition="Overall system health based on all findings",
            findings=findings,
            confidence=1.0
        )
        
        # Critical findings branch
        if critical:
            high_confidence = any(f.confidence == Confidence.CERTAIN for f in critical)
            critical_node = DecisionNode(
                name="Critical Findings",
                condition="Critical severity findings present",
                findings=critical,
                confidence=1.0 if high_confidence else 0.8
            )
            root.children.append(critical_node)
            
            # Sub-branches for each critical finding
            for f in critical:
                evidence_node = DecisionNode(
                    name=f"Evidence: {f.type}",
                    condition=f.description,
                    findings=[f],
                    confidence=f.confidence.value
                )
                critical_node.children.append(evidence_node)
        
        # High findings branch
        if high:
            high_node = DecisionNode(
                name="High Findings",
                condition="High severity findings present",
                findings=high,
                confidence=0.8
            )
            root.children.append(high_node)
        
        # Medium findings branch
        if medium:
            medium_node = DecisionNode(
                name="Medium Findings",
                condition="Medium severity findings present",
                findings=medium,
                confidence=0.6
            )
            root.children.append(medium_node)
        
        # Determine overall decision
        if critical:
            root.decision = "BROKEN"
            root.confidence = min(1.0, max(f.confidence.value for f in critical))
        elif high:
            root.decision = "DEGRADED"
            root.confidence = max(f.confidence.value for f in high)
        elif medium:
            root.decision = "WARNING"
            root.confidence = max(f.confidence.value for f in medium)
        else:
            root.decision = "HEALTHY"
            root.confidence = 1.0
        
        self.root = root
        return root
    
    def trace_decision(self, node: DecisionNode, path: List[str] = None) -> Dict[str, Any]:
        """Trace decision path."""
        if path is None:
            path = []
        
        path.append(node.name)
        
        result = {
            "path": " → ".join(path),
            "node": node.name,
            "condition": node.condition,
            "decision": node.decision,
            "confidence": node.confidence,
            "findings": [{
                "type": f.type,
                "severity": f.severity,
                "description": f.description,
                "confidence": f.confidence.value,
                "evidence": [{
                    "source": e.source,
                    "description": e.description,
                    "confidence": e.confidence.value
                } for e in f.evidence]
            } for f in node.findings]
        }
        
        if node.children:
            result["children"] = []
            for child in node.children:
                result["children"].append(self.trace_decision(child, path.copy()))
        
        return result
    
    def get_recommendations(self, node: DecisionNode = None) -> List[str]:
        """Get recommendations from decision graph."""
        if node is None:
            node = self.root
        
        recommendations = []
        
        for finding in node.findings:
            if finding.recommendation:
                recommendations.append(finding.recommendation)
        
        for child in node.children:
            recommendations.extend(self.get_recommendations(child))
        
        return list(set(recommendations))