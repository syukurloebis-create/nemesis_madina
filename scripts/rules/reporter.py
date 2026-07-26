# scripts/rules/reporter.py
from typing import List, Dict, Any
from scripts.architecture.models.violation import Violation
from scripts.architecture.logging.logger import NemesisLogger
import json
import yaml

class ViolationReporter:
    def __init__(self):
        self.logger = NemesisLogger()
    
    def generate_report(self, violations: List[Violation], format: str = 'json') -> str:
        """Generate violation report in specified format"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_violations': len(violations),
            'violations_by_severity': self._group_by_severity(violations),
            'violations_by_rule': self._group_by_rule(violations),
            'violations_by_module': self._group_by_module(violations),
            'violations': [v.__dict__ for v in violations]
        }
        
        if format == 'json':
            return json.dumps(report, indent=2)
        elif format == 'yaml':
            return yaml.dump(report)
        else:
            return self._generate_text_report(report)
    
    def save_report(self, violations: List[Violation], output_path: str, format: str = 'yaml'):
        """Save violation report to file"""
        report = self.generate_report(violations, format)
        with open(output_path, 'w') as f:
            f.write(report)
        self.logger.info(f"Report saved to {output_path}")
    
    def _group_by_severity(self, violations: List[Violation]) -> Dict[str, int]:
        result = {}
        for v in violations:
            result[v.severity] = result.get(v.severity, 0) + 1
        return result
    
    def _group_by_rule(self, violations: List[Violation]) -> Dict[str, int]:
        result = {}
        for v in violations:
            result[v.rule_id] = result.get(v.rule_id, 0) + 1
        return result
    
    def _group_by_module(self, violations: List[Violation]) -> Dict[str, int]:
        result = {}
        for v in violations:
            if v.module:
                result[v.module] = result.get(v.module, 0) + 1
        return result
    
    def _generate_text_report(self, report: Dict) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append("ARCHITECTURE VIOLATION REPORT")
        lines.append("=" * 60)
        lines.append(f"Total Violations: {report['total_violations']}")
        lines.append("")
        lines.append("Violations by Severity:")
        for severity, count in report['violations_by_severity'].items():
            lines.append(f"  {severity}: {count}")
        lines.append("")
        lines.append("Violations by Rule:")
        for rule, count in report['violations_by_rule'].items():
            lines.append(f"  {rule}: {count}")
        lines.append("")
        lines.append("Violation Details:")
        for v in report['violations']:
            lines.append(f"  [{v['severity']}] {v['message']}")
            if v.get('module'):
                lines.append(f"    Module: {v['module']}")
        lines.append("=" * 60)
        return "\n".join(lines)