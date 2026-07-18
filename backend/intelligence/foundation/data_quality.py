"""
Data Quality Pipeline
Validasi dan monitoring kualitas data
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Severity(str, Enum):
    """Severity level untuk issue"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class QualityIssue:
    """Data quality issue"""
    issue_id: str
    issue_type: str
    description: str
    severity: Severity
    affected_entity: str
    affected_field: str
    current_value: Any
    expected_value: Any
    recommendation: str
    created_at: datetime = field(default_factory=datetime.now)


class DataQualityPipeline:
    """Pipeline untuk data quality validation"""

    def __init__(self):
        self.issues: List[QualityIssue] = []
        self.rules: List[Dict[str, Any]] = []
        self._init_default_rules()

    def _init_default_rules(self) -> None:
        """Initialize default validation rules"""
        self.rules = [
            {
                "name": "case_title_not_empty",
                "description": "Case title harus ada",
                "entity": "case",
                "field": "title",
                "check": lambda data: bool(data.get("title")),
                "severity": Severity.CRITICAL,
                "recommendation": "Tambahkan judul case"
            },
            {
                "name": "case_risk_score_valid",
                "description": "Risk score harus antara 0-100",
                "entity": "case",
                "field": "risk_score",
                "check": lambda data: 0 <= data.get("risk_score", 0) <= 100,
                "severity": Severity.HIGH,
                "recommendation": "Perbaiki nilai risk score"
            },
            {
                "name": "evidence_has_hash",
                "description": "Evidence harus memiliki hash",
                "entity": "evidence",
                "field": "hash",
                "check": lambda data: bool(data.get("hash")),
                "severity": Severity.HIGH,
                "recommendation": "Tambahkan hash untuk evidence"
            },
            {
                "name": "entity_name_not_empty",
                "description": "Entity name harus ada",
                "entity": "entity",
                "field": "name",
                "check": lambda data: bool(data.get("name")),
                "severity": Severity.CRITICAL,
                "recommendation": "Tambahkan nama entity"
            },
            {
                "name": "graph_edge_has_both_nodes",
                "description": "Edge harus memiliki source dan target",
                "entity": "graph_edge",
                "field": "source_id,target_id",
                "check": lambda data: data.get("source_id") and data.get("target_id"),
                "severity": Severity.CRITICAL,
                "recommendation": "Pastikan edge memiliki source dan target"
            },
            {
                "name": "fraud_pattern_has_confidence",
                "description": "Fraud pattern harus memiliki confidence score",
                "entity": "fraud_pattern",
                "field": "confidence",
                "check": lambda data: isinstance(data.get("confidence"), (int, float)),
                "severity": Severity.MEDIUM,
                "recommendation": "Tambahkan confidence score"
            },
        ]

    def validate_entity(
        self,
        entity_type: str,
        data: Dict[str, Any]
    ) -> List[QualityIssue]:
        """Validate a single entity"""
        issues = []
        for rule in self.rules:
            if rule["entity"] == entity_type:
                try:
                    is_valid = rule["check"](data)
                    if not is_valid:
                        issues.append(QualityIssue(
                            issue_id=f"{rule['name']}_{datetime.now().timestamp()}",
                            issue_type=rule["name"],
                            description=rule["description"],
                            severity=rule["severity"],
                            affected_entity=entity_type,
                            affected_field=rule["field"],
                            current_value=data.get(rule["field"].split(",")[0]),
                            expected_value="Valid value",
                            recommendation=rule["recommendation"]
                        ))
                except Exception as e:
                    logger.error(f"Validation error: {e}")

        if issues:
            self.issues.extend(issues)

        return issues

    def validate_batch(
        self,
        entity_type: str,
        data_list: List[Dict[str, Any]]
    ) -> List[QualityIssue]:
        """Validate multiple entities"""
        all_issues = []
        for data in data_list:
            issues = self.validate_entity(entity_type, data)
            all_issues.extend(issues)
        return all_issues

    def get_issues_by_severity(self, severity: Severity) -> List[QualityIssue]:
        """Get issues by severity"""
        return [i for i in self.issues if i.severity == severity]

    def get_issues_by_entity(self, entity_type: str) -> List[QualityIssue]:
        """Get issues by entity type"""
        return [i for i in self.issues if i.affected_entity == entity_type]

    def get_stats(self) -> Dict[str, Any]:
        """Get quality statistics"""
        total = len(self.issues)
        by_severity = {
            Severity.CRITICAL.value: len(self.get_issues_by_severity(Severity.CRITICAL)),
            Severity.HIGH.value: len(self.get_issues_by_severity(Severity.HIGH)),
            Severity.MEDIUM.value: len(self.get_issues_by_severity(Severity.MEDIUM)),
            Severity.LOW.value: len(self.get_issues_by_severity(Severity.LOW)),
            Severity.INFO.value: len(self.get_issues_by_severity(Severity.INFO)),
        }
        by_entity = {}
        for entity in set(i.affected_entity for i in self.issues):
            by_entity[entity] = len(self.get_issues_by_entity(entity))

        return {
            "total_issues": total,
            "by_severity": by_severity,
            "by_entity": by_entity,
            "quality_score": max(0, 100 - total * 5)  # Simplified quality score
        }

    def generate_report(self) -> Dict[str, Any]:
        """Generate quality report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "summary": self.get_stats(),
            "issues": [{
                "id": i.issue_id,
                "type": i.issue_type,
                "description": i.description,
                "severity": i.severity.value,
                "recommendation": i.recommendation
            } for i in self.issues[:20]]  # Limit to 20 issues
        }


# Singleton instance
data_quality = DataQualityPipeline()