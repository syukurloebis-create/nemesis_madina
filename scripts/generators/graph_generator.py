# scripts/generators/graph_generator.py
from typing import Dict, Any, List
from scripts.inventory.query import InventoryQuery
from scripts.architecture.logging.logger import NemesisLogger
import json

class GraphGenerator:
    def __init__(self, inventory: InventoryQuery):
        self.inventory = inventory
        self.logger = NemesisLogger()
    
    def generate(self) -> Dict[str, Any]:
        """Generate knowledge graph"""
        modules = self.inventory.storage.get_modules()
        relations = self.inventory.storage.get_relations()
        
        graph = {
            'nodes': [],
            'edges': []
        }
        
        # Add modules as nodes
        for module in modules:
            graph['nodes'].append({
                'id': module['id'],
                'name': module['name'],
                'type': module['type'],
                'language': module['language']
            })
        
        # Add relations as edges
        for relation in relations:
            graph['edges'].append({
                'source': relation['source'],
                'target': relation['target'],
                'type': relation['type']
            })
        
        self.logger.info(f"Graph generated: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges")
        return graph
    
    def save(self, output_path: str = 'docs/architecture/generated/graph.json'):
        """Save graph to file"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        graph = self.generate()
        with open(output_path, 'w') as f:
            json.dump(graph, f, indent=2)
        
        self.logger.info(f"Graph saved to {output_path}")