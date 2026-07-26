# scripts/generators/debt_generator.py
from typing import Dict, Any, List
from datetime import datetime
from scripts.inventory.query import InventoryQuery
from scripts.architecture.logging.logger import NemesisLogger

class DebtGenerator:
    def __init__(self, inventory: InventoryQuery):
        self.inventory = inventory
        self.logger = NemesisLogger()
    
    def generate(self) -> Dict[str, Any]:
        """Generate technical debt report"""
        legacy_imports = self.inventory.get_legacy_imports()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_debt_items': len(legacy_imports),
            'debt_items': [
                {
                    'id': f"TD-{i:03d}",
                    'description': f"Legacy repository import: {item['source']} -> {item['target']}",
                    'severity': 'HIGH',
                    'category': 'legacy_migration',
                    'source': item['source'],
                    'target': item['target']
                }
                for i, item in enumerate(legacy_imports)
            ]
        }