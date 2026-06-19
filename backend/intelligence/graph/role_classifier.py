"""
Entity Role Classification in Financial Networks
Identifies: Source, Intermediary, Sink, Beneficial Owner
"""

from typing import List, Dict, Any, Set
from collections import defaultdict


class RoleClassifier:
    """
    Classify entity roles in transaction networks.
    
    Roles:
    - SOURCE: Sends money but rarely receives (initial funder)
    - INTERMEDIARY: Both sends and receives (money mover)
    - SINK: Receives money but rarely sends (final destination)
    - BENEFICIAL_OWNER: Ultimate beneficiary of funds
    - SHELL: Limited activity, potentially fake
    """
    
    def __init__(self):
        self.role_thresholds = {
            "source_ratio": 0.7,      # Outflow > 70% of total
            "sink_ratio": 0.7,        # Inflow > 70% of total
            "intermediary_ratio": 0.3,  # Both > 30%
            "shell_min_tx": 2,        # Minimum transactions
        }
    
    def classify_entity_roles(
        self,
        entities: List[Dict],
        edges: List[Dict]
    ) -> Dict[str, Any]:
        """
        Classify each entity's role based on transaction patterns.
        
        Returns:
            Dictionary with role assignments and confidence scores
        """
        if not edges:
            return {"roles": {}, "summary": {}}
        
        # Calculate inflow and outflow per entity
        inflow = defaultdict(float)
        outflow = defaultdict(float)
        incoming_tx = defaultdict(int)
        outgoing_tx = defaultdict(int)
        
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            amount = edge.get("properties", {}).get("amount", 0)
            edge_type = edge.get("type", "")
            
            if edge_type == "financial_transfer" or "financial" in edge_type:
                outflow[source] += amount
                inflow[target] += amount
                outgoing_tx[source] += 1
                incoming_tx[target] += 1
        
        # Get entity names mapping
        entity_names = {e["id"]: e["name"] for e in entities}
        
        roles = {}
        for entity in entities:
            entity_id = entity["id"]
            total_in = inflow.get(entity_id, 0)
            total_out = outflow.get(entity_id, 0)
            total_flow = total_in + total_out
            
            in_tx = incoming_tx.get(entity_id, 0)
            out_tx = outgoing_tx.get(entity_id, 0)
            total_tx = in_tx + out_tx
            
            role = "unknown"
            confidence = 0.5
            reasoning = []
            
            if total_flow > 0:
                in_ratio = total_in / total_flow
                out_ratio = total_out / total_flow
                
                # Source (mostly sends)
                if out_ratio >= self.role_thresholds["source_ratio"] and out_tx > 0:
                    role = "source"
                    confidence = min(0.9, out_ratio)
                    reasoning.append(f"Outflow {out_ratio:.0%} of total flow")
                
                # Sink (mostly receives)
                elif in_ratio >= self.role_thresholds["sink_ratio"] and in_tx > 0:
                    role = "sink"
                    confidence = min(0.9, in_ratio)
                    reasoning.append(f"Inflow {in_ratio:.0%} of total flow")
                
                # Intermediary (significant both directions)
                elif in_ratio >= self.role_thresholds["intermediary_ratio"] and out_ratio >= self.role_thresholds["intermediary_ratio"]:
                    role = "intermediary"
                    confidence = 0.7 + (min(in_ratio, out_ratio) * 0.2)
                    reasoning.append(f"Balanced flow: in {in_ratio:.0%}, out {out_ratio:.0%}")
                
                # Shell (minimal activity)
                elif total_tx <= self.role_thresholds["shell_min_tx"] and total_flow > 0:
                    role = "shell"
                    confidence = 0.6
                    reasoning.append(f"Limited activity: {total_tx} transactions")
            
            roles[entity_id] = {
                "entity_id": entity_id,
                "entity_name": entity_names.get(entity_id, "Unknown"),
                "entity_type": entity.get("type", "unknown"),
                "role": role,
                "confidence": round(confidence, 2),
                "reasoning": reasoning,
                "metrics": {
                    "total_inflow": total_in,
                    "total_outflow": total_out,
                    "total_flow": total_flow,
                    "inflow_ratio": round(in_ratio, 3) if total_flow > 0 else 0,
                    "outflow_ratio": round(out_ratio, 3) if total_flow > 0 else 0,
                    "incoming_transactions": in_tx,
                    "outgoing_transactions": out_tx,
                }
            }
        
        # Calculate network summary
        role_counts = defaultdict(int)
        for r in roles.values():
            role_counts[r["role"]] += 1
        
        # Identify suspicious role combinations
        suspicions = []
        if role_counts.get("shell", 0) > 2:
            suspicions.append({
                "type": "multiple_shell_companies",
                "count": role_counts["shell"],
                "risk": 0.6,
            })
        
        if role_counts.get("source", 0) > 0 and role_counts.get("sink", 0) == 0:
            suspicions.append({
                "type": "missing_sink",
                "risk": 0.4,
            })
        
        return {
            "roles": roles,
            "summary": {
                "role_distribution": dict(role_counts),
                "total_entities": len(entities),
                "classified_count": len([r for r in roles.values() if r["role"] != "unknown"]),
            },
            "suspicions": suspicions,
        }
    
    def identify_beneficial_owners(
        self,
        roles: Dict,
        edges: List[Dict]
    ) -> List[Dict]:
        """
        Identify potential beneficial owners based on network position.
        
        Indicators:
        - Ultimate sink of funds
        - Receives from multiple sources
        - Connected to shell companies
        """
        beneficial_owners = []
        
        # Find potential sinks (final destinations)
        for entity_id, role_data in roles.items():
            if role_data["role"] == "sink":
                # Check if sink receives from multiple sources
                incoming_sources = set()
                for edge in edges:
                    if edge.get("target") == entity_id:
                        source = edge.get("source")
                        if source:
                            incoming_sources.add(source)
                
                is_beneficial = len(incoming_sources) >= 2
                
                beneficial_owners.append({
                    "entity_id": entity_id,
                    "entity_name": role_data["entity_name"],
                    "type": "beneficial_owner",
                    "confidence": 0.8 if is_beneficial else 0.5,
                    "incoming_sources": list(incoming_sources),
                    "total_inflow": role_data["metrics"]["total_inflow"],
                })
        
        return beneficial_owners