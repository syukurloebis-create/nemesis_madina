from datetime import datetime
"""
Schema Validator - Validate Data Against Schemas
"""

from typing import Dict, Any, List, Tuple, Optional
from backend.schema.registry import SchemaRegistry, SchemaVersion


class SchemaValidator:
    """Validate data against registered schemas"""
    
    def __init__(self, registry: SchemaRegistry):
        self.registry = registry
    
    def validate_event(self, event_type: str, data: Dict[str, Any], version: SchemaVersion = None) -> Tuple[bool, List[str]]:
        """Validate an event against its schema"""
        return self.registry.validate(event_type, data, version)
    
    def validate_evidence(self, evidence: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate evidence data"""
        required_fields = ['id', 'hash', 'created_at', 'source']
        errors = []
        
        for field in required_fields:
            if field not in evidence:
                errors.append(f"Missing required field: {field}")
        
        # Validate hash format
        if 'hash' in evidence and evidence['hash']:
            if len(evidence['hash']) not in [32, 64, 128]:  # Common hash lengths
                errors.append(f"Invalid hash length: {len(evidence['hash'])}")
        
        # Validate timestamp
        if 'created_at' in evidence:
            try:
                datetime.fromisoformat(evidence['created_at'])
            except (ValueError, TypeError):
                errors.append("Invalid timestamp format")
        
        return len(errors) == 0, errors
    
    def validate_lineage_node(self, node: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate lineage node"""
        required_fields = ['id', 'type', 'name', 'timestamp']
        errors = []
        
        for field in required_fields:
            if field not in node:
                errors.append(f"Missing required field: {field}")
        
        valid_types = ['input', 'transform', 'decision', 'output', 'evidence', 'event', 'context']
        if 'type' in node and node['type'] not in valid_types:
            errors.append(f"Invalid node type: {node['type']}. Expected one of {valid_types}")
        
        return len(errors) == 0, errors
    
    def validate_lineage_edge(self, edge: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate lineage edge"""
        required_fields = ['source', 'target', 'relationship']
        errors = []
        
        for field in required_fields:
            if field not in edge:
                errors.append(f"Missing required field: {field}")
        
        valid_relationships = ['produces', 'consumes', 'derives', 'verifies', 'contains']
        if 'relationship' in edge and edge['relationship'] not in valid_relationships:
            errors.append(f"Invalid relationship: {edge['relationship']}")
        
        return len(errors) == 0, errors
