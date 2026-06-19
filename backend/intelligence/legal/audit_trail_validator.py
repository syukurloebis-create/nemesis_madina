from typing import Dict


class AuditTrailValidator:
    """
    Validasi audit trail untuk compliance
    """

    def validate(self, record: Dict) -> Dict:
        issues = []

        if "entity_id" not in record:
            issues.append("missing_entity_id")

        if "timestamp" not in record:
            issues.append("missing_timestamp")

        if "hash" not in record:
            issues.append("missing_hash")

        return {
            "valid": len(issues) == 0,
            "issues": issues
        }