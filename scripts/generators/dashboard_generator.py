# scripts/generators/dashboard_generator.py
from typing import Dict, Any
from datetime import datetime
from scripts.inventory.query import InventoryQuery
from scripts.rules.engine import RuleEngine
from scripts.architecture.logging.logger import NemesisLogger
import json

class DashboardGenerator:
    def __init__(self, inventory: InventoryQuery, rule_engine: RuleEngine):
        self.inventory = inventory
        self.rule_engine = rule_engine
        self.logger = NemesisLogger()
    
    def generate(self) -> Dict[str, Any]:
        """Generate dashboard data"""
        modules = self.inventory.storage.get_modules()
        violations = self.rule_engine.get_violations()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_modules': len(modules),
                'total_violations': len(violations),
                'critical_violations': len([v for v in violations if v.severity == 'critical']),
                'high_violations': len([v for v in violations if v.severity == 'high']),
                'medium_violations': len([v for v in violations if v.severity == 'medium']),
                'low_violations': len([v for v in violations if v.severity == 'low'])
            },
            'modules_by_type': self._group_by_type(modules),
            'violations_by_rule': self._group_by_rule(violations)
        }
    
    def _group_by_type(self, modules: list) -> Dict[str, int]:
        result = {}
        for module in modules:
            module_type = module.get('type', 'unknown')
            result[module_type] = result.get(module_type, 0) + 1
        return result
    
    def _group_by_rule(self, violations: list) -> Dict[str, int]:
        result = {}
        for v in violations:
            rule_id = v.rule_id if hasattr(v, 'rule_id') else 'unknown'
            result[rule_id] = result.get(rule_id, 0) + 1
        return result
    
    def save(self, output_path: str = 'docs/architecture/generated/dashboard.json'):
        """Save dashboard data to file"""
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        data = self.generate()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.info(f"Dashboard data saved to {output_path}")