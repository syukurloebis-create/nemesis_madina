# scripts/gate/gate.py
from typing import List, Dict, Any
from enum import Enum
from scripts.rules.engine import RuleEngine
from scripts.architecture.models.violation import Violation
from scripts.architecture.logging.logger import NemesisLogger

class GateLevel(Enum):
    INFORMATIONAL = "informational"
    WARNING = "warning"
    SOFT_FAIL = "soft_fail"
    HARD_FAIL = "hard_fail"

class ArchitectureGate:
    def __init__(self, rule_engine: RuleEngine):
        self.rule_engine = rule_engine
        self.logger = NemesisLogger()
        self.level = GateLevel.INFORMATIONAL
    
    def set_level(self, level: GateLevel) -> None:
        """Set gate level"""
        self.level = level
        self.logger.info(f"Gate level set to: {level.value}")
    
    def evaluate(self, threshold: int = 0) -> Dict[str, Any]:
        """Evaluate gate against violations"""
        violations = self.rule_engine.evaluate()
        result = {
            'passed': True,
            'violations': len(violations),
            'critical_violations': len([v for v in violations if v.severity == 'critical']),
            'high_violations': len([v for v in violations if v.severity == 'high']),
            'level': self.level.value,
            'message': ''
        }
        
        # Determine if gate passes
        if self.level == GateLevel.INFORMATIONAL:
            result['passed'] = True
            result['message'] = f"Informational: {len(violations)} violations found"
        
        elif self.level == GateLevel.WARNING:
            result['passed'] = True
            result['message'] = f"Warning: {len(violations)} violations found"
            if len(violations) > 0:
                result['message'] += " - Please review violations"
        
        elif self.level == GateLevel.SOFT_FAIL:
            if len(violations) > threshold:
                result['passed'] = False
                result['message'] = f"Soft Fail: {len(violations)} violations found (threshold: {threshold})"
            else:
                result['passed'] = True
                result['message'] = f"Soft Fail: {len(violations)} violations found - within threshold"
        
        elif self.level == GateLevel.HARD_FAIL:
            if len(violations) > threshold:
                result['passed'] = False
                result['message'] = f"Hard Fail: {len(violations)} violations found (threshold: {threshold})"
            else:
                result['passed'] = True
                result['message'] = f"Hard Fail: {len(violations)} violations found - within threshold"
        
        self.logger.info(f"Gate evaluation: {result['message']}")
        return result
    
    def save_report(self, result: Dict[str, Any], output_path: str = 'gate-report.json'):
        """Save gate report"""
        import json
        import os
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        self.logger.info(f"Gate report saved to {output_path}")