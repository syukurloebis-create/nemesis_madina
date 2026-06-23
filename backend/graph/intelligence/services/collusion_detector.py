"""Collusion Detection Service - Detect suspicious patterns in procurement"""

from typing import List, Dict, Any, Set, Tuple
from collections import defaultdict
from graph.intelligence.models import CollusionDetectionResult, RelationshipType


class CollusionDetector:
    """Detect collusion patterns in procurement network"""
    
    def __init__(self, edge_repo):
        self.edge_repo = edge_repo
    
    async def detect_bid_rigging(self, tender_id: str) -> List[CollusionDetectionResult]:
        """Detect bid rigging patterns in a tender"""
        results = []
        
        # Get all vendors in this tender
        vendors = await self._get_tender_vendors(tender_id)
        
        # Check for vendor relationships
        for i, vendor1 in enumerate(vendors):
            for vendor2 in vendors[i+1:]:
                relationships = await self.edge_repo.get_relationships(vendor1, vendor2)
                
                for rel in relationships:
                    if rel.weight > 0.7:
                        results.append(CollusionDetectionResult(
                            entities=[vendor1, vendor2],
                            relationship_type=rel.relationship_type,
                            score=rel.weight,
                            confidence=rel.confidence,
                            evidence=[{
                                "type": "relationship",
                                "relationship": rel.relationship_type.value,
                                "weight": rel.weight
                            }]
                        ))
        
        return results
    
    async def detect_shared_patterns(
        self,
        entity_ids: List[str],
        pattern_type: str = "address"
    ) -> List[CollusionDetectionResult]:
        """Detect shared patterns (address, phone, director) among entities"""
        results = []
        
        # Group by pattern value
        groups = defaultdict(list)
        
        for entity_id in entity_ids:
            # Get entity properties
            properties = await self._get_entity_properties(entity_id)
            pattern_value = properties.get(pattern_type)
            
            if pattern_value:
                groups[pattern_value].append(entity_id)
        
        # Create results for groups with multiple entities
        for pattern_value, entities in groups.items():
            if len(entities) > 1:
                results.append(CollusionDetectionResult(
                    entities=entities,
                    relationship_type=RelationshipType.SHARES_ADDRESS,
                    score=0.8,
                    confidence=0.7,
                    evidence=[{
                        "type": pattern_type,
                        "value": pattern_value,
                        "entities": entities
                    }]
                ))
        
        return results
    
    async def detect_circular_ownership(self, max_depth: int = 5) -> List[CollusionDetectionResult]:
        """Detect circular ownership patterns"""
        results = []
        
        # Get all companies
        companies = await self._get_entities_by_type("company")
        
        for company in companies:
            # Find ownership chain
            chain = await self._find_ownership_chain(company, company, max_depth)
            if len(chain) > 2:
                results.append(CollusionDetectionResult(
                    entities=chain,
                    relationship_type=RelationshipType.OWNS,
                    score=0.9,
                    confidence=0.6,
                    evidence=[{
                        "type": "circular_ownership",
                        "chain": chain
                    }]
                ))
        
        return results
    
    async def _get_tender_vendors(self, tender_id: str) -> List[str]:
        # Implementation to get vendors for a tender
        # This would query from tender data
        return []
    
    async def _get_entity_properties(self, entity_id: str) -> Dict[str, Any]:
        # Implementation to get entity properties
        return {}
    
    async def _get_entities_by_type(self, entity_type: str) -> List[str]:
        # Implementation to get entities by type
        return []
    
    async def _find_ownership_chain(self, start: str, target: str, max_depth: int) -> List[str]:
        # Implementation to find ownership chain
        return []


class RelationshipExtractor:
    """Extract relationships from various data sources"""
    
    @staticmethod
    async def extract_from_anomaly(anomaly_data: Dict[str, Any]) -> List[EntityEdge]:
        """Extract relationships from anomaly detection"""
        edges = []
        
        if anomaly_data.get('anomaly_type') == 'shared_director':
            edges.append(EntityEdge(
                source_id=anomaly_data['vendor_a'],
                target_id=anomaly_data['vendor_b'],
                relationship_type=RelationshipType.SAME_DIRECTOR,
                weight=anomaly_data.get('confidence', 0.8),
                confidence=anomaly_data.get('confidence', 0.8),
                evidence_ids=[UUID(anomaly_data['evidence_id'])] if anomaly_data.get('evidence_id') else []
            ))
        
        return edges
    
    @staticmethod
    async def extract_from_relationship_data(data: Dict[str, Any]) -> List[EntityEdge]:
        """Extract relationships from structured relationship data"""
        edges = []
        
        relationship_map = {
            "owns": RelationshipType.OWNS,
            "controls": RelationshipType.CONTROLS,
            "related_to": RelationshipType.RELATED_TO,
            "manages": RelationshipType.MANAGES,
            "endorsed_by": RelationshipType.ENDORSED_BY
        }
        
        rel_type = relationship_map.get(data.get('type'))
        if rel_type:
            edges.append(EntityEdge(
                source_id=data['source'],
                target_id=data['target'],
                relationship_type=rel_type,
                weight=data.get('weight', 0.5),
                confidence=data.get('confidence', 0.5),
                evidence_ids=data.get('evidence_ids', [])
            ))
        
        return edges
