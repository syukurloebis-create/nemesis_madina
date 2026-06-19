"""
Multi-Case Correlation Engine
Identifies connections between different cases
"""

from typing import List, Dict, Any, Set
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.intelligence.graph.models import Entity, Relationship, CollusionDetection

CASE_ID_FIELD = "aggregate_id"


class CaseCorrelator:
    """
    Correlate entities and patterns across multiple cases.
    
    Features:
    - Entity overlap detection
    - Pattern similarity
    - Network connection between cases
    - Risk propagation
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_entity_overlaps(
        self,
        case_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Find entities that appear in multiple cases.
        
        Returns:
            Dictionary with overlapping entities and cases
        """
        if not case_ids:
            return {"overlaps": [], "entity_frequencies": {}}
        
        # Query entities for all cases
        result = await self.session.execute(
            select(Entity).where(Entity.case_id.in_(case_ids))
        )
        entities = result.scalars().all()
        
        # Group by entity name and type
        entity_cases = defaultdict(set)
        for entity in entities:
            key = f"{entity.entity_type}:{entity.name}"
            entity_cases[key].add(entity.case_id)
        
        # Find overlaps (entities appearing in multiple cases)
        overlaps = []
        for entity_key, cases in entity_cases.items():
            if len(cases) > 1:
                overlaps.append({
                    "entity_key": entity_key,
                    "case_ids": list(cases),
                    "occurrence_count": len(cases),
                    "entity_type": entity_key.split(":")[0],
                    "entity_name": entity_key.split(":")[1],
                })
        
        # Calculate entity frequencies
        entity_frequencies = {
            entity_key: len(cases) 
            for entity_key, cases in entity_cases.items()
        }
        
        return {
            "overlaps": overlaps,
            "entity_frequencies": entity_frequencies,
            "total_entities": len(entity_cases),
            "overlap_count": len(overlaps),
            "has_connections": len(overlaps) > 0,
        }
    
    async def find_similar_patterns(
        self,
        case_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Find similar collusion patterns across cases.
        """
        if not case_ids:
            return {"similar_patterns": [], "pattern_clusters": {}}
        
        # Query detections for all cases
        result = await self.session.execute(
            select(CollusionDetection).where(CollusionDetection.case_id.in_(case_ids))
        )
        detections = result.scalars().all()
        
        # Group by pattern type
        patterns_by_type = defaultdict(list)
        for detection in detections:
            patterns_by_type[detection.pattern_type].append({
                "case_id": detection.case_id,
                "description": detection.description,
                "entities": detection.entity_names,
                "severity": detection.severity,
            })
        
        # Find similar pattern clusters
        pattern_clusters = {}
        for pattern_type, items in patterns_by_type.items():
            if len(items) > 1:
                pattern_clusters[pattern_type] = {
                    "case_count": len(set(i["case_id"] for i in items)),
                    "detection_count": len(items),
                    "cases": list(set(i["case_id"] for i in items)),
                    "average_severity": sum(i["severity"] for i in items) / len(items),
                }
        
        return {
            "similar_patterns": pattern_clusters,
            "total_pattern_types": len(patterns_by_type),
            "has_similar_patterns": len(pattern_clusters) > 0,
        }
    
    async def build_case_network(
        self,
        case_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Build network of cases connected by shared entities.
        """
        overlaps_result = await self.find_entity_overlaps(case_ids)
        
        # Build case-to-case connections
        case_connections = defaultdict(lambda: defaultdict(int))
        
        for overlap in overlaps_result.get("overlaps", []):
            connected_cases = overlap["case_ids"]
            for i in range(len(connected_cases)):
                for j in range(i + 1, len(connected_cases)):
                    case_connections[connected_cases[i]][connected_cases[j]] += 1
                    case_connections[connected_cases[j]][connected_cases[i]] += 1
        
        # Calculate network metrics
        case_degree = {
            case_id: len(connections) 
            for case_id, connections in case_connections.items()
        }
        
        return {
            "case_connections": dict(case_connections),
            "case_degree": case_degree,
            "connected_cases": len(case_connections),
            "total_cases": len(case_ids),
            "network_density": len(case_connections) / (len(case_ids) * (len(case_ids) - 1)) if len(case_ids) > 1 else 0,
        }
    
    async def calculate_cross_case_risk(
        self,
        case_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Calculate risk propagation between connected cases.
        """
        # Get risk scores for each case
        from backend.intelligence.models import RiskScore
        
        risks = {}
        for case_id in case_ids:
            result = await self.session.execute(
                select(RiskScore)
                .where(RiskScore.case_id == case_id)
                .order_by(RiskScore.calculated_at.desc())
                .limit(1)
            )
            risk = result.scalar_one_or_none()
            if risk:
                risks[case_id] = risk.overall_score
        
        # Get case connections
        network = await self.build_case_network(case_ids)
        
        # Propagate risk through connections
        propagated_risks = {}
        for case_id, risk_score in risks.items():
            connected = network["case_connections"].get(case_id, {})
            if connected:
                # Average risk from connected cases
                connected_risks = [risks.get(c, 0) for c in connected.keys()]
                connected_avg = sum(connected_risks) / len(connected_risks) if connected_risks else 0
                propagated_risks[case_id] = {
                    "original_risk": risk_score,
                    "propagated_risk": round((risk_score + connected_avg) / 2, 2),
                    "influence_count": len(connected),
                }
            else:
                propagated_risks[case_id] = {
                    "original_risk": risk_score,
                    "propagated_risk": risk_score,
                    "influence_count": 0,
                }
        
        return {
            "case_risks": propagated_risks,
            "network_risk": sum(r["propagated_risk"] for r in propagated_risks.values()) / len(propagated_risks) if propagated_risks else 0,
            "has_cross_case_risk": len([r for r in propagated_risks.values() if r["propagated_risk"] > r["original_risk"]]) > 0,
        }
    
    async def comprehensive_correlation(
        self,
        case_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Run all correlation analyses and return combined result.
        """
        overlaps = await self.find_entity_overlaps(case_ids)
        patterns = await self.find_similar_patterns(case_ids)
        network = await self.build_case_network(case_ids)
        risks = await self.calculate_cross_case_risk(case_ids)
        
        return {
            "entity_overlaps": overlaps,
            "pattern_similarity": patterns,
            "case_network": network,
            "cross_case_risk": risks,
            "correlation_score": self._calculate_correlation_score(overlaps, patterns, network),
        }
    
    def _calculate_correlation_score(
        self,
        overlaps: Dict,
        patterns: Dict,
        network: Dict
    ) -> float:
        """Calculate overall correlation score (0-100)."""
        score = 0.0
        
        if overlaps.get("overlap_count", 0) > 0:
            score += min(40, overlaps["overlap_count"] * 10)
        
        if patterns.get("has_similar_patterns", False):
            score += 30
        
        if network.get("connected_cases", 0) > 0:
            score += min(30, network["connected_cases"] * 10)
        
        return min(100, score)