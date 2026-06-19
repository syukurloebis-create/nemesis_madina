#!/usr/bin/env python3
"""
NEMESIS FASE 3 - Create Schema Registry for Versioning
"""

import sys
import json
from pathlib import Path
from datetime import datetime

SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

SCHEMA_DIR = PROJECT_ROOT / "backend" / "schema"

def create_schema_structure():
    """Create schema directory structure"""
    print("\n[1/4] Creating schema directory...")
    SCHEMA_DIR.mkdir(parents=True, exist_ok=True)
    return True

def create_init():
    """Create __init__.py for schema module"""
    content = '''"""
NEMESIS Schema Module - Schema Registry and Versioning
"""

from backend.schema.registry import SchemaRegistry, SchemaVersion, EventSchema
from backend.schema.migration import SchemaMigrator
from backend.schema.validator import SchemaValidator

__all__ = [
    'SchemaRegistry',
    'SchemaVersion',
    'EventSchema',
    'SchemaMigrator',
    'SchemaValidator'
]
'''
    
    file_path = SCHEMA_DIR / "__init__.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_registry():
    """Create registry.py - schema registry"""
    content = '''"""
Schema Registry - Manage Schema Versions
"""

from enum import Enum
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import json


class SchemaVersion(str, Enum):
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"


@dataclass
class EventSchema:
    """Event schema definition"""
    name: str
    version: SchemaVersion
    fields: Dict[str, str]  # field_name -> field_type
    required: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    deprecated_at: Optional[datetime] = None
    migration_to: Optional[SchemaVersion] = None
    
    def validate(self, data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate data against schema"""
        errors = []
        
        # Check required fields
        for field in self.required:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        # Check field types (simplified)
        for field, value in data.items():
            if field in self.fields:
                expected_type = self.fields[field]
                if not self._check_type(value, expected_type):
                    errors.append(f"Field '{field}' expected {expected_type}, got {type(value).__name__}")
        
        return len(errors) == 0, errors
    
    def _check_type(self, value: Any, expected: str) -> bool:
        type_mapping = {
            "str": str, "int": int, "float": float, "bool": bool,
            "dict": dict, "list": list, "datetime": datetime
        }
        expected_type = type_mapping.get(expected)
        return isinstance(value, expected_type) if expected_type else True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version.value,
            "fields": self.fields,
            "required": self.required,
            "created_at": self.created_at.isoformat(),
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
            "migration_to": self.migration_to.value if self.migration_to else None
        }


class SchemaRegistry:
    """Registry for managing schema versions"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._schemas: Dict[str, Dict[SchemaVersion, EventSchema]] = {}
        self._load_default_schemas()
        self._initialized = True
    
    def _load_default_schemas(self):
        """Load default schemas"""
        # Evidence schemas
        self.register(EventSchema(
            name="EvidenceCreated",
            version=SchemaVersion.V1,
            fields={"id": "str", "hash": "str", "timestamp": "datetime", "source": "str"},
            required=["id", "hash", "timestamp", "source"]
        ))
        
        self.register(EventSchema(
            name="EvidenceCreated",
            version=SchemaVersion.V2,
            fields={"id": "str", "hash": "str", "signature": "str", "timestamp": "datetime", "source": "str"},
            required=["id", "hash", "signature", "timestamp", "source"]
        ))
        
        # Event schemas
        self.register(EventSchema(
            name="EventPublished",
            version=SchemaVersion.V1,
            fields={"event_id": "str", "event_type": "str", "data": "dict", "source": "str", "timestamp": "datetime"},
            required=["event_id", "event_type", "source", "timestamp"]
        ))
        
        # Anomaly schemas
        self.register(EventSchema(
            name="AnomalyDetected",
            version=SchemaVersion.V1,
            fields={"anomaly_id": "str", "severity": "str", "description": "str", "timestamp": "datetime"},
            required=["anomaly_id", "severity", "timestamp"]
        ))
    
    def register(self, schema: EventSchema):
        """Register a schema"""
        key = f"{schema.name}"
        if key not in self._schemas:
            self._schemas[key] = {}
        self._schemas[key][schema.version] = schema
    
    def get_schema(self, name: str, version: SchemaVersion) -> Optional[EventSchema]:
        """Get schema by name and version"""
        key = f"{name}"
        if key in self._schemas:
            return self._schemas[key].get(version)
        return None
    
    def get_latest_version(self, name: str) -> Optional[EventSchema]:
        """Get latest (non-deprecated) version of schema"""
        key = f"{name}"
        if key not in self._schemas:
            return None
        
        latest = None
        for version, schema in self._schemas[key].items():
            if schema.deprecated_at is None:
                if latest is None or version.value > latest.version.value:
                    latest = schema
        return latest
    
    def list_schemas(self) -> List[EventSchema]:
        """List all registered schemas"""
        result = []
        for schemas in self._schemas.values():
            result.extend(schemas.values())
        return result
    
    def deprecate(self, name: str, version: SchemaVersion, migration_to: SchemaVersion = None):
        """Mark a schema as deprecated"""
        schema = self.get_schema(name, version)
        if schema:
            schema.deprecated_at = datetime.now()
            schema.migration_to = migration_to
    
    def validate(self, name: str, data: Dict[str, Any], version: SchemaVersion = None) -> tuple[bool, List[str]]:
        """Validate data against schema"""
        if version is None:
            schema = self.get_latest_version(name)
        else:
            schema = self.get_schema(name, version)
        
        if not schema:
            return False, [f"Schema not found: {name}"]
        
        return schema.validate(data)
    
    def get_schema_diff(self, name: str, from_version: SchemaVersion, to_version: SchemaVersion) -> Dict[str, Any]:
        """Get differences between two schema versions"""
        from_schema = self.get_schema(name, from_version)
        to_schema = self.get_schema(name, to_version)
        
        if not from_schema or not to_schema:
            return {"error": "Schema not found"}
        
        added_fields = set(to_schema.fields.keys()) - set(from_schema.fields.keys())
        removed_fields = set(from_schema.fields.keys()) - set(to_schema.fields.keys())
        changed_fields = {
            f: (from_schema.fields[f], to_schema.fields[f])
            for f in set(from_schema.fields.keys()) & set(to_schema.fields.keys())
            if from_schema.fields[f] != to_schema.fields[f]
        }
        
        return {
            "name": name,
            "from_version": from_version.value,
            "to_version": to_version.value,
            "added_fields": list(added_fields),
            "removed_fields": list(removed_fields),
            "changed_fields": changed_fields
        }
'''
    
    file_path = SCHEMA_DIR / "registry.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_migration():
    """Create migration.py - schema migration"""
    content = '''"""
Schema Migration - Migrate Data Between Schema Versions
"""

from typing import Dict, Any, List, Optional
from backend.schema.registry import SchemaRegistry, SchemaVersion


class SchemaMigrator:
    """Migrate data between schema versions"""
    
    def __init__(self, registry: SchemaRegistry):
        self.registry = registry
    
    def migrate(self, data: Dict[str, Any], from_version: SchemaVersion, to_version: SchemaVersion) -> Dict[str, Any]:
        """Migrate data from one version to another"""
        # Get migration path
        migrations = self._get_migration_path(from_version, to_version)
        
        result = data.copy()
        for migration in migrations:
            result = self._apply_migration(result, migration)
        
        return result
    
    def _get_migration_path(self, from_version: SchemaVersion, to_version: SchemaVersion) -> List[SchemaVersion]:
        """Get list of versions to migrate through"""
        versions = [SchemaVersion.V1, SchemaVersion.V2, SchemaVersion.V3]
        
        from_idx = versions.index(from_version)
        to_idx = versions.index(to_version)
        
        if to_idx > from_idx:
            return versions[from_idx + 1:to_idx + 1]
        else:
            return list(reversed(versions[to_idx:from_idx]))
    
    def _apply_migration(self, data: Dict[str, Any], target_version: SchemaVersion) -> Dict[str, Any]:
        """Apply a single migration step"""
        result = data.copy()
        
        # Version-specific migrations
        if target_version == SchemaVersion.V2:
            # Add signature field
            if 'hash' in result and 'signature' not in result:
                result['signature'] = f"sig_{result['hash'][:16]}"
        
        elif target_version == SchemaVersion.V1:
            # Remove signature field
            result.pop('signature', None)
        
        return result
    
    def can_migrate(self, from_version: SchemaVersion, to_version: SchemaVersion) -> bool:
        """Check if migration is possible"""
        try:
            self._get_migration_path(from_version, to_version)
            return True
        except ValueError:
            return False
    
    def batch_migrate(
        self,
        items: List[Dict[str, Any]],
        from_version: SchemaVersion,
        to_version: SchemaVersion
    ) -> List[Dict[str, Any]]:
        """Migrate a batch of items"""
        return [self.migrate(item, from_version, to_version) for item in items]
'''
    
    file_path = SCHEMA_DIR / "migration.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def create_validator():
    """Create validator.py - schema validator"""
    content = '''"""
Schema Validator - Validate Data Against Schemas
"""

from typing import Dict, Any, List, Tuple, Optional
from backend.schema.registry import SchemaRegistry, SchemaVersion


class SchemaValidator:
    """Validate data against registered schemas"""
    
    def __init__(self, registry: SchemaRegistry):
        self.registry = registry
    
    def validate_event(self, event_type: str, data: Dict[str, Any], version: SchemaVersion = None) -> Tuple[bool, List[str]]:
        """Validate an event against its schema"""
        return self.registry.validate(event_type, data, version)
    
    def validate_evidence(self, evidence: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate evidence data"""
        required_fields = ['id', 'hash', 'created_at', 'source']
        errors = []
        
        for field in required_fields:
            if field not in evidence:
                errors.append(f"Missing required field: {field}")
        
        # Validate hash format
        if 'hash' in evidence and evidence['hash']:
            if len(evidence['hash']) not in [32, 64, 128]:  # Common hash lengths
                errors.append(f"Invalid hash length: {len(evidence['hash'])}")
        
        # Validate timestamp
        if 'created_at' in evidence:
            try:
                datetime.fromisoformat(evidence['created_at'])
            except (ValueError, TypeError):
                errors.append("Invalid timestamp format")
        
        return len(errors) == 0, errors
    
    def validate_lineage_node(self, node: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate lineage node"""
        required_fields = ['id', 'type', 'name', 'timestamp']
        errors = []
        
        for field in required_fields:
            if field not in node:
                errors.append(f"Missing required field: {field}")
        
        valid_types = ['input', 'transform', 'decision', 'output', 'evidence', 'event', 'context']
        if 'type' in node and node['type'] not in valid_types:
            errors.append(f"Invalid node type: {node['type']}. Expected one of {valid_types}")
        
        return len(errors) == 0, errors
    
    def validate_lineage_edge(self, edge: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate lineage edge"""
        required_fields = ['source', 'target', 'relationship']
        errors = []
        
        for field in required_fields:
            if field not in edge:
                errors.append(f"Missing required field: {field}")
        
        valid_relationships = ['produces', 'consumes', 'derives', 'verifies', 'contains']
        if 'relationship' in edge and edge['relationship'] not in valid_relationships:
            errors.append(f"Invalid relationship: {edge['relationship']}")
        
        return len(errors) == 0, errors
'''
    
    # Add datetime import
    content = "from datetime import datetime\n" + content
    
    file_path = SCHEMA_DIR / "validator.py"
    file_path.write_text(content)
    print(f"  [OK] Created: {file_path}")
    return True

def main():
    print("\n" + "="*60)
    print("FASE 3: CREATE SCHEMA REGISTRY")
    print("="*60)
    
    create_schema_structure()
    create_init()
    create_registry()
    create_migration()
    create_validator()
    
    print("\n" + "="*60)
    print("[OK] Schema registry created")
    print(f"   Location: {SCHEMA_DIR}")
    print("="*60)
    return 0

if __name__ == "__main__":
    sys.exit(main())