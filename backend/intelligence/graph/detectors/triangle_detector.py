"""
Triangle Detection for Collusion Identification

A triangle (3-cycle) in a graph indicates potential collusion:
A → B → C → A (circular relationship)

Examples:
- Person A sends money to Person B, who sends to Person C, who sends back to A
- Company A owns Company B, which controls Company C, which is owned by A
"""

from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
import itertools


class TriangleDetector:
    """
    Detect triangular patterns in relationship graph.
    
    Triangle types:
    - Financial: Money flows in a cycle
    - Ownership: Circular ownership structure
    - Communication: Circular information flow
    - Mixed: Different relationship types forming cycle
    """
    
    def __init__(self):
        self.triangles = []
    
    def detect_financial_triangles(
        self,
        transactions: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect financial triangles (money flow cycles).
        
        Args:
            transactions: List of {'from': entity, 'to': entity, 'amount': float}
        
        Returns:
            List of detected triangles with entities and flow
        """
        # Build graph
        graph = defaultdict(set)
        for tx in transactions:
            from_entity = tx.get("from")
            to_entity = tx.get("to")
            if from_entity and to_entity:
                graph[from_entity].add(to_entity)
        
        # Find triangles
        triangles = self._find_cycles(graph, 3)
        
        # Enrich with metadata
        result = []
        for triangle in triangles:
            # Calculate total flow in triangle
            total_amount = 0
            for i in range(len(triangle)):
                from_entity = triangle[i]
                to_entity = triangle[(i + 1) % len(triangle)]
                for tx in transactions:
                    if tx.get("from") == from_entity and tx.get("to") == to_entity:
                        total_amount += tx.get("amount", 0)
            
            result.append({
                "type": "financial_triangle",
                "entities": list(triangle),
                "cycle": [f"{a}→{b}" for a, b in zip(triangle, triangle[1:] + [triangle[0]])],
                "total_amount": total_amount,
                "confidence": 0.8 if total_amount > 0 else 0.6,
                "severity": min(total_amount / 100000000, 1.0) if total_amount else 0.5,
                "description": f"Circular financial flow detected: {' → '.join(triangle)} → {triangle[0]}",
            })
        
        return result
    
    def detect_ownership_triangles(
        self,
        ownerships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect circular ownership structures.
        
        Args:
            ownerships: List of {'owner': entity, 'owned': entity, 'percentage': float}
        """
        # Build ownership graph
        graph = defaultdict(set)
        for own in ownerships:
            owner = own.get("owner")
            owned = own.get("owned")
            if owner and owned:
                graph[owner].add(owned)
        
        triangles = self._find_cycles(graph, 3)
        
        result = []
        for triangle in triangles:
            # Calculate control percentages
            percentages = []
            for i in range(len(triangle)):
                owner = triangle[i]
                owned = triangle[(i + 1) % len(triangle)]
                for own in ownerships:
                    if own.get("owner") == owner and own.get("owned") == owned:
                        percentages.append(own.get("percentage", 0))
            
            avg_percentage = sum(percentages) / len(percentages) if percentages else 0
            
            result.append({
                "type": "ownership_triangle",
                "entities": list(triangle),
                "cycle": [f"{a} owns {b}" for a, b in zip(triangle, triangle[1:] + [triangle[0]])],
                "avg_ownership": avg_percentage,
                "confidence": 0.9 if avg_percentage > 50 else 0.7,
                "severity": avg_percentage / 100,
                "description": f"Circular ownership detected: {triangle[0]} owns {triangle[1]}, who owns {triangle[2]}, who owns back {triangle[0]}",
            })
        
        return result
    
    def detect_mixed_triangles(
        self,
        relationships: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect triangles with mixed relationship types.
        
        Args:
            relationships: List of {'source': entity, 'target': entity, 'type': str}
        """
        # Build graph with relationship types
        graph = defaultdict(list)
        for rel in relationships:
            source = rel.get("source")
            target = rel.get("target")
            rel_type = rel.get("type")
            if source and target:
                graph[source].append({"target": target, "type": rel_type})
        
        # Find all connected triples
        entities = list(graph.keys())
        triangles = []
        
        for a, b, c in itertools.combinations(entities, 3):
            # Check if all connections exist
            a_to_b = any(e["target"] == b for e in graph.get(a, []))
            b_to_c = any(e["target"] == c for e in graph.get(b, []))
            c_to_a = any(e["target"] == a for e in graph.get(c, []))
            
            if a_to_b and b_to_c and c_to_a:
                # Get relationship types
                types = []
                for rel in graph.get(a, []):
                    if rel["target"] == b:
                        types.append(rel["type"])
                for rel in graph.get(b, []):
                    if rel["target"] == c:
                        types.append(rel["type"])
                for rel in graph.get(c, []):
                    if rel["target"] == a:
                        types.append(rel["type"])
                
                triangles.append({
                    "type": "mixed_triangle",
                    "entities": [a, b, c],
                    "relationship_types": types,
                    "cycle": [f"{a}→{b} ({types[0]})", f"{b}→{c} ({types[1]})", f"{c}→{a} ({types[2]})"],
                    "confidence": 0.85,
                    "severity": 0.7,
                    "description": f"Multi-relationship cycle detected: {a} → {b} ({types[0]}), {b} → {c} ({types[1]}), {c} → {a} ({types[2]})",
                })
        
        return triangles
    
    def _find_cycles(self, graph: Dict, max_length: int = 3) -> List[List[str]]:
        """
        Find cycles in directed graph.
        
        Args:
            graph: Adjacency list {node: set(neighbors)}
            max_length: Maximum cycle length to detect
        
        Returns:
            List of cycles (each cycle is list of nodes)
        """
        cycles = []
        
        def dfs(node, start, path, visited):
            if len(path) > max_length:
                return
            
            for neighbor in graph.get(node, []):
                if neighbor == start and len(path) >= 2:
                    # Found cycle
                    cycles.append(path + [start])
                elif neighbor not in visited:
                    visited.add(neighbor)
                    dfs(neighbor, start, path + [neighbor], visited)
                    visited.remove(neighbor)
        
        for node in graph:
            dfs(node, node, [node], {node})
        
        # Remove duplicates (normalize by sorting)
        normalized = set()
        unique_cycles = []
        for cycle in cycles:
            # Normalize: sort and take first element smallest
            normalized_cycle = tuple(sorted(cycle))
            if normalized_cycle not in normalized:
                normalized.add(normalized_cycle)
                unique_cycles.append(cycle)
        
        return unique_cycles
    
    def analyze_case_relationships(
        self,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Comprehensive triangle analysis for a case.
        
        Args:
            events: List of case events
        
        Returns:
            Dict with all detected triangles and summary
        """
        # Extract transactions and relationships from events
        transactions = []
        ownerships = []
        relationships = []
        
        for event in events:
            event_type = event.get("event_type")
            data = event.get("data", {})
            
            if event_type == "transaction_added":
                transactions.append({
                    "from": data.get("sender"),
                    "to": data.get("receiver"),
                    "amount": data.get("amount", 0),
                    "timestamp": event.get("timestamp"),
                })
            
            elif event_type == "ownership_added":
                ownerships.append({
                    "owner": data.get("owner"),
                    "owned": data.get("entity"),
                    "percentage": data.get("percentage", 0),
                })
            
            elif "relationship" in event_type:
                relationships.append({
                    "source": data.get("source"),
                    "target": data.get("target"),
                    "type": data.get("relationship_type"),
                })
        
        # Run detectors
        financial_triangles = self.detect_financial_triangles(transactions)
        ownership_triangles = self.detect_ownership_triangles(ownerships)
        mixed_triangles = self.detect_mixed_triangles(relationships)
        
        all_triangles = financial_triangles + ownership_triangles + mixed_triangles
        
        # Calculate overall collusion risk
        if all_triangles:
            collusion_risk = sum(t.get("severity", 0) for t in all_triangles) / len(all_triangles)
            collusion_risk = min(collusion_risk * 100, 100)
        else:
            collusion_risk = 0
        
        return {
            "triangles": all_triangles,
            "collusion_risk": round(collusion_risk, 2),
            "triangle_count": len(all_triangles),
            "types": {
                "financial": len(financial_triangles),
                "ownership": len(ownership_triangles),
                "mixed": len(mixed_triangles),
            },
        }