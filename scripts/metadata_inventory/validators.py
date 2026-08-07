# scripts/metadata_inventory/validators.py
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from .enums import FindingID, Severity

@dataclass
class ValidationError:
    field: str
    message: str
    finding_id: Optional[str] = None

class RegistryValidator:
    """Validasi registry di startup."""
    
    def validate(self, registry: dict) -> List[ValidationError]:
        errors = []
        findings = registry.get("findings", {})
        
        # 1. Cek semua FindingID ada di registry
        for enum_member in FindingID:
            if enum_member.value not in findings:
                errors.append(ValidationError(
                    field="findings",
                    message=f"FindingID {enum_member.value} not found in registry",
                    finding_id=enum_member.value
                ))
        
        # 2. Cek semua entri registry memiliki FindingID
        for finding_id, definition in findings.items():
            try:
                FindingID[finding_id]
            except KeyError:
                errors.append(ValidationError(
                    field="findings",
                    message=f"Unknown finding ID in registry: {finding_id}",
                    finding_id=finding_id
                ))
        
        # 3. Validasi severity
        for finding_id, definition in findings.items():
            severity = definition.get("severity")
            if severity not in [s.value for s in Severity]:
                errors.append(ValidationError(
                    field="severity",
                    message=f"Invalid severity '{severity}' for {finding_id}",
                    finding_id=finding_id
                ))
        
        # 4. Validasi kategori
        valid_categories = ["metadata", "schema", "boundary", "migration", "performance"]
        for finding_id, definition in findings.items():
            category = definition.get("category")
            if category and category not in valid_categories:
                errors.append(ValidationError(
                    field="category",
                    message=f"Invalid category '{category}' for {finding_id}",
                    finding_id=finding_id
                ))
        
        return errors

class PipelineValidator:
    """Validasi pipeline di startup."""
    
    def validate(self, context: PipelineContext) -> List[ValidationError]:
        errors = []
        
        # Validasi contract version
        if context.contract_version != CONTRACT_VERSION:
            errors.append(ValidationError(
                field="contract_version",
                message=f"Context v{context.contract_version} != Framework v{CONTRACT_VERSION}"
            ))
        
        # Validasi paths
        if not context.project_root.exists():
            errors.append(ValidationError(
                field="project_root",
                message=f"Project root not found: {context.project_root}"
            ))
        
        # Validasi output directory
        if not context.output_dir.exists():
            errors.append(ValidationError(
                field="output_dir",
                message=f"Output directory not found: {context.output_dir}"
            ))
        
        return errors