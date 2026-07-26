# scripts/generators/report_generator.py
from typing import List, Dict, Any
from datetime import datetime
from scripts.inventory.query import InventoryQuery
from scripts.rules.engine import RuleEngine
from scripts.architecture.logging.logger import NemesisLogger

class ReportGenerator:
    def __init__(self, inventory: InventoryQuery, rule_engine: RuleEngine):
        self.inventory = inventory
        self.rule_engine = rule_engine
        self.logger = NemesisLogger()
    
    def generate_inventory_report(self) -> Dict[str, Any]:
        """Generate inventory report"""
        modules = self.inventory.storage.get_modules()
        relations = self.inventory.storage.get_relations()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_modules': len(modules),
                'total_relations': len(relations),
                'modules_by_type': self._group_by_type(modules),
                'modules_by_language': self._group_by_language(modules)
            },
            'legacy_imports': self.inventory.get_legacy_imports()
        }
    
    def generate_violation_report(self) -> Dict[str, Any]:
        """Generate violation report"""
        violations = self.rule_engine.get_violations()
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_violations': len(violations),
            'violations_by_severity': self._group_by_severity(violations),
            'violations_by_rule': self._group_by_rule(violations),
            'violations': [v.__dict__ for v in violations]
        }
    
    def _group_by_type(self, modules: list) -> Dict[str, int]:
        result = {}
        for module in modules:
            module_type = module.get('type', 'unknown')
            result[module_type] = result.get(module_type, 0) + 1
        return result
    
    def _group_by_language(self, modules: list) -> Dict[str, int]:
        result = {}
        for module in modules:
            language = module.get('language', 'unknown')
            result[language] = result.get(language, 0) + 1
        return result
    
    def _group_by_severity(self, violations: list) -> Dict[str, int]:
        result = {}
        for v in violations:
            severity = v.severity if hasattr(v, 'severity') else 'unknown'
            result[severity] = result.get(severity, 0) + 1
        return result
    
    def _group_by_rule(self, violations: list) -> Dict[str, int]:
        result = {}
        for v in violations:
            rule_id = v.rule_id if hasattr(v, 'rule_id') else 'unknown'
            result[rule_id] = result.get(rule_id, 0) + 1
        return result