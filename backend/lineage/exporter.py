"""
Lineage Exporter - Export Lineage Data
"""

import json
import csv
from pathlib import Path
from typing import Dict, Any, List
from lineage.tracker import LineageTracker


class LineageExporter:
    """Export lineage data to various formats"""
    
    def __init__(self, tracker: LineageTracker):
        self.tracker = tracker
    
    def to_json(self, file_path: Path) -> bool:
        """Export lineage to JSON file"""
        try:
            data = self.tracker.to_dict()
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def to_csv(self, file_path: Path) -> bool:
        """Export nodes and edges to CSV files"""
        try:
            base_path = Path(file_path).with_suffix('')
            
            # Export nodes
            nodes_path = f"{base_path}_nodes.csv"
            with open(nodes_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'type', 'name', 'timestamp', 'inputs', 'outputs'])
                for node in self.tracker.nodes.values():
                    writer.writerow([
                        node.id, node.type, node.name, node.timestamp.isoformat(),
                        ';'.join(node.inputs), ';'.join(node.outputs)
                    ])
            
            # Export edges
            edges_path = f"{base_path}_edges.csv"
            with open(edges_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['source', 'target', 'relationship', 'timestamp'])
                for edge in self.tracker.edges:
                    writer.writerow([
                        edge.source, edge.target, edge.relationship, edge.timestamp.isoformat()
                    ])
            
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    
    def to_graphviz(self, file_path: Path) -> bool:
        """Export lineage to Graphviz DOT format"""
        try:
            lines = ['digraph Lineage {']
            lines.append('    rankdir=TB;')
            lines.append('    node [shape=box, style=filled, fillcolor=lightblue];')
            
            # Add nodes
            for node in self.tracker.nodes.values():
                label = f"{node.name}\\n({node.type})"
                lines.append(f'    "{node.id}" [label="{label}"];')
            
            # Add edges
            for edge in self.tracker.edges:
                lines.append(f'    "{edge.source}" -> "{edge.target}" [label="{edge.relationship}"];')
            
            lines.append('}')
            
            with open(file_path, 'w') as f:
                f.write('\n'.join(lines))
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
