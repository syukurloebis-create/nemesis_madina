# scripts/metadata_inventory/registry.py
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from .enums import Severity, FindingID

@dataclass(frozen=True)
class FindingDefinition:
    """Definisi finding dari registry."""
    finding_id: FindingID
    severity: Severity
    category: str
    title: str
    description: str
    remediation: str
    documentation: Optional[str] = None

@dataclass(frozen=True)
class RegistryMetadata:
    schema_version: str
    registry_version: str
    last_updated: str

class FindingRegistry:
    """
    Single Source of Truth untuk finding definitions.
    Semua metadata finding berasal dari registry YAML.
    """
    
    _instance = None
    _definitions: Dict[FindingID, FindingDefinition] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_registry()
        return cls._instance
    
    def _load_registry(self):
        """Load registry dari YAML."""
        registry_path = Path(__file__).parent / "finding_registry.yaml"
        
        if not registry_path.exists():
            raise FileNotFoundError(f"Finding registry not found: {registry_path}")
        
        with open(registry_path, "r") as f:
            data = yaml.safe_load(f)
        
        self._metadata = RegistryMetadata(
            schema_version=data.get("schema_version", "1.0"),
            registry_version=data.get("registry_version", "1.0.0"),
            last_updated=data.get("last_updated", "")
        )
        
        for finding_id, definition in data.get("findings", {}).items():
            try:
                id_enum = FindingID[finding_id]
            except KeyError:
                continue  # Skip unknown IDs
            
            self._definitions[id_enum] = FindingDefinition(
                finding_id=id_enum,
                severity=Severity(definition.get("severity", "WARNING")),
                category=definition.get("category", "unknown"),
                title=definition.get("title", finding_id),
                description=definition.get("description", ""),
                remediation=definition.get("remediation", ""),
                documentation=definition.get("documentation")
            )
    
    def get(self, finding_id: FindingID) -> Optional[FindingDefinition]:
        """Get definition for a finding ID."""
        return self._definitions.get(finding_id)
    
    def create_finding(self, finding_id: FindingID, evidence: List[Evidence]) -> Finding:
        """Create a Finding from registry data."""
        definition = self.get(finding_id)
        if not definition:
            raise ValueError(f"Unknown finding ID: {finding_id}")
        
        return Finding(
            id=finding_id,
            severity=definition.severity,
            title=definition.title,
            description=definition.description,
            evidence=evidence,
            affected_modules=[]  # Akan diisi oleh analyzer
        )