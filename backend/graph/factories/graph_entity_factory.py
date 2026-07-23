"""
Graph Entity Factory — Converts GraphCandidate to persistence DTOs.

Pure transformation — NO SQL, NO Repository, NO UnitOfWork.
"""

import json
from typing import List, Dict, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime

from backend.graph.dto.graph_candidate import GraphCandidate, GraphNode, GraphEdge


class GraphEntityFactory:
    """
    Factory for persistence DTOs.
    
    Converts pure GraphCandidate to database-ready DTOs.
    Generates UUIDs and adds persistence metadata.
    
    NO SQL, NO Repository, NO UnitOfWork.
    """
    
    @staticmethod
    def create_entity_dtos(
        nodes: List[GraphNode],
        case_id: UUID,
        institution_id: UUID,
    ) -> List[Dict[str, Any]]:
        """
        Convert GraphNodes to entity DTOs.
        
        Args:
            nodes: List of pure GraphNodes
            case_id: Case UUID
            institution_id: Institution UUID
            
        Returns:
            List of entity DTOs ready for persistence
        """
        entities = []
        
        for node in nodes:
            entity_id = str(uuid4())
            
            entities.append({
                'id': entity_id,
                'name': node.name,
                'entity_type': node.node_type,
                'case_id': str(case_id),
                'institution_id': str(institution_id),
                'external_id': node.external_id,
                'confidence': node.confidence,
                'risk_score': node.risk_score,
                'first_seen': datetime.now(),
                'extra_data': json.dumps(node.properties),
                'created_by': 'system',
            })
        
        return entities
    
    @staticmethod
    def create_relationship_dtos(
        edges: List[GraphEdge],
        entity_id_map: Dict[str, str],
        case_id: UUID,
    ) -> List[Dict[str, Any]]:
        """
        Convert GraphEdges to relationship DTOs.
        
        Args:
            edges: List of pure GraphEdges
            entity_id_map: Mapping of node name → entity UUID
            case_id: Case UUID
            
        Returns:
            List of relationship DTOs ready for persistence
        """
        relationships = []
        
        for edge in edges:
            source_id = entity_id_map.get(edge.source)
            target_id = entity_id_map.get(edge.target)
            
            if source_id and target_id:
                relationships.append({
                    'source_id': source_id,
                    'target_id': target_id,
                    'relationship_type': edge.relationship_type,
                    'weight': edge.weight,
                    'case_id': str(case_id),
                    'extra_data': json.dumps(edge.properties),
                    'created_at': datetime.now(),
                })
        
        return relationships
    
    @staticmethod
    def create_all(
        graph: GraphCandidate,
        case_id: UUID,
        institution_id: UUID,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, str]]:
        """
        Convert entire GraphCandidate to persistence DTOs.
        
        Args:
            graph: Pure GraphCandidate
            case_id: Case UUID
            institution_id: Institution UUID
            
        Returns:
            Tuple of (entity_dtos, relationship_dtos, entity_id_map)
        """
        # Create entity DTOs
        entities = GraphEntityFactory.create_entity_dtos(
            nodes=graph.nodes,
            case_id=case_id,
            institution_id=institution_id,
        )
        
        # Build entity_id_map
        entity_id_map = {}
        for entity in entities:
            entity_id_map[entity['name']] = entity['id']
        
        # Create relationship DTOs
        relationships = GraphEntityFactory.create_relationship_dtos(
            edges=graph.edges,
            entity_id_map=entity_id_map,
            case_id=case_id,
        )
        
        return entities, relationships, entity_id_map
