# scripts/rules/semantic.py
from typing import List, Dict, Any
from scripts.architecture.models.violation import Violation
from scripts.inventory.query import InventoryQuery

class SemanticRules:
    """Semantic rules for architecture governance"""
    
    @staticmethod
    def check_adr_compliance(inventory: InventoryQuery, adr_config: Dict[str, Any]) -> List[Violation]:
        """Check ADR compliance"""
        violations = []
        
        for adr_id, config in adr_config.items():
            if config.get('status') == 'deprecated':
                # Check if any modules still implement deprecated ADR
                modules = inventory.get_modules()
                for module in modules:
                    if config.get('module_pattern') in module['path']:
                        violations.append(Violation(
                            rule_id='ADR-001',
                            message=f"Module {module['name']} implements deprecated ADR: {adr_id}",
                            severity='high',
                            module=module['id'],
                            details={'adr': adr_id, 'superseded_by': config.get('superseded_by')}
                        ))
        
        return violations
    
    @staticmethod
    def check_capability_ownership(inventory: InventoryQuery, capability_config: Dict[str, Any]) -> List[Violation]:
        """Check capability ownership"""
        violations = []
        
        for cap_id, config in capability_config.items():
            for module_pattern in config.get('modules', []):
                # Check if module exists
                modules = inventory.storage.query(
                    "SELECT * FROM modules WHERE path LIKE ?",
                    (f"%{module_pattern}%",)
                )
                if not modules:
                    violations.append(Violation(
                        rule_id='CAP-001',
                        message=f"Capability {cap_id} references missing module: {module_pattern}",
                        severity='medium',
                        details={'capability': cap_id, 'module': module_pattern}
                    ))
        
        return violations