# scripts/rules/engine.py
from typing import List, Dict, Any, Optional
from scripts.architecture.models.violation import Violation
from scripts.inventory.query import InventoryQuery
from scripts.architecture.logging.logger import NemesisLogger

class RuleEngine:
    def __init__(self, inventory: InventoryQuery):
        self.inventory = inventory
        self.logger = NemesisLogger()
        self.rules: List[Dict[str, Any]] = []
        self.violations: List[Violation] = []
    
    def load_rules(self, rules: List[Dict[str, Any]]) -> None:
        """Load rules from configuration"""
        self.rules = rules
        self.logger.info(f"Loaded {len(self.rules)} rules")
    
    def evaluate(self) -> List[Violation]:
        """Evaluate all rules against inventory"""
        self.violations = []
        
        for rule in self.rules:
            if rule['type'] == 'forbidden_import':
                self._check_forbidden_import(rule)
            elif rule['type'] == 'domain_purity':
                self._check_domain_purity(rule)
            elif rule['type'] == 'layer_separation':
                self._check_layer_separation(rule)
            # Add more rule types as needed
        
        self.logger.info(f"Evaluation complete: {len(self.violations)} violations found")
        return self.violations
    
    def _check_forbidden_import(self, rule: Dict[str, Any]) -> None:
        """Check for forbidden imports"""
        target = rule['target_modules'][0]
        results = self.inventory.storage.query(
            "SELECT source, target FROM relations "
            "WHERE type='imports' AND target LIKE ?",
            (f"{target}%",)
        )
        
        for result in results:
            self.violations.append(Violation(
                rule_id=rule['id'],
                message=f"Forbidden import: {result['source']} imports {result['target']}",
                severity=rule['severity'],
                module=result['source'],
                details={'target': result['target']}
            ))
    
    def _check_domain_purity(self, rule: Dict[str, Any]) -> None:
        """Check domain purity (no framework imports)"""
        domain_modules = self.inventory.get_modules_by_type('domain')
        forbidden = rule.get('forbidden_imports', ['fastapi', 'sqlalchemy'])
        
        for module in domain_modules:
            imports = self.inventory.storage.query(
                "SELECT target FROM relations WHERE source = ? AND type='imports'",
                (module['id'],)
            )
            
            for imp in imports:
                target = imp['target']
                for forbidden_import in forbidden:
                    if forbidden_import in target:
                        self.violations.append(Violation(
                            rule_id=rule['id'],
                            message=f"Domain module {module['name']} imports {target}",
                            severity=rule['severity'],
                            module=module['id'],
                            details={'import': target, 'forbidden': forbidden_import}
                        ))
    
    def _check_layer_separation(self, rule: Dict[str, Any]) -> None:
        """Check layer separation rules"""
        # This is a placeholder - full implementation in v9.x
        pass
    
    def get_violations(self) -> List[Violation]:
        return self.violations