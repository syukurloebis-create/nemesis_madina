"""
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
    fields: Dict[str, str]
    required: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    deprecated_at: Optional[datetime] = None
    migration_to: Optional[SchemaVersion] = None
    
    def validate(self, data: Dict[str, Any]) -> tuple:
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
    
    def validate(self, name: str, data: Dict[str, Any], version: SchemaVersion = None) -> tuple:
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
