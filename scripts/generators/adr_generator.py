# scripts/generators/adr_generator.py
from typing import Dict, Any, List
from datetime import datetime
from scripts.inventory.query import InventoryQuery
from scripts.architecture.logging.logger import NemesisLogger

class ADRGenerator:
    def __init__(self, inventory: InventoryQuery):
        self.inventory = inventory
        self.logger = NemesisLogger()
    
    def generate(self, adr_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ADR status report"""
        adr_status = []
        
        for adr_id, config in adr_config.items():
            # Check if modules exist
            modules = []
            for module_pattern in config.get('modules', []):
                found = self.inventory.storage.query(
                    "SELECT * FROM modules WHERE path LIKE ?",
                    (f"%{module_pattern}%",)
                )
                if found:
                    modules.extend(found)
            
            status = {
                'id': adr_id,
                'title': config.get('title', 'Unknown'),
                'status': config.get('status', 'unknown'),
                'implementation_percent': self._calculate_implementation(modules, config),
                'modules_found': len(modules),
                'modules_expected': len(config.get('modules', []))
            }
            adr_status.append(status)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'adrs': adr_status
        }
    
    def _calculate_implementation(self, modules: List[Dict], config: Dict) -> float:
        """Calculate implementation percentage"""
        expected = len(config.get('modules', []))
        found = len(modules)
        if expected == 0:
            return 0.0
        return (found / expected) * 100