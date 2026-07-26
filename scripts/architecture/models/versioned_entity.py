# scripts/architecture/models/versioned_entity.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any, List
from scripts.architecture.registries.engine import RegistryProvider

@dataclass
class VersionedEntity:
    """Base class for versioned entities"""
    id: str
    version: int
    schema_version: int
    created_at: datetime
    updated_at: datetime
    data: Dict[str, Any]
    deprecated: bool = False
    superseded_by: Optional[str] = None

class VersionedRegistry:
    """Registry with versioning support"""
    
    def __init__(self, provider: RegistryProvider):
        self.provider = provider
        self._entities: Dict[str, List[VersionedEntity]] = {}
        self._load()
    
    def _load(self):
        data = self.provider.load()
        for entity_id, versions in data.items():
            self._entities[entity_id] = []
            for version_data in versions:
                self._entities[entity_id].append(
                    VersionedEntity(**version_data)
                )
    
    def _save(self) -> None:
        """Save all entities to provider"""
        data = {}
        for entity_id, versions in self._entities.items():
            data[entity_id] = []
            for version in versions:
                # Convert to dict for serialization
                version_dict = {
                    'id': version.id,
                    'version': version.version,
                    'schema_version': version.schema_version,
                    'created_at': version.created_at.isoformat(),
                    'updated_at': version.updated_at.isoformat(),
                    'data': version.data,
                    'deprecated': version.deprecated,
                    'superseded_by': version.superseded_by
                }
                data[entity_id].append(version_dict)
        self.provider.save(data)

    def get(self, entity_id: str, version: Optional[int] = None) -> Optional[VersionedEntity]:
        """Get entity by ID and optional version"""
        if entity_id not in self._entities:
            return None
        
        versions = self._entities[entity_id]
        if version is None:
            # Return latest non-deprecated version
            for v in reversed(versions):
                if not v.deprecated:
                    return v
            return versions[-1] if versions else None
        
        for v in versions:
            if v.version == version:
                return v
        return None
    
    def get_all_versions(self, entity_id: str) -> List[VersionedEntity]:
        """Get all versions of an entity"""
        return self._entities.get(entity_id, [])
    
    def create_version(self, entity_id: str, data: Dict[str, Any]) -> VersionedEntity:
        """Create a new version of an entity"""
        versions = self._entities.get(entity_id, [])
        
        # Find latest version
        latest_version = max([v.version for v in versions]) if versions else 0
        new_version = latest_version + 1
        
        entity = VersionedEntity(
            id=entity_id,
            version=new_version,
            schema_version=data.get('schema_version', 1),
            created_at=datetime.now(),
            updated_at=datetime.now(),
            data=data,
            deprecated=False
        )
        
        if entity_id not in self._entities:
            self._entities[entity_id] = []
        self._entities[entity_id].append(entity)
        
        self._save()
        return entity
    
    def deprecate(self, entity_id: str, version: int, superseded_by: Optional[str] = None):
        """Deprecate a specific version"""
        versions = self._entities.get(entity_id, [])
        for v in versions:
            if v.version == version:
                v.deprecated = True
                v.superseded_by = superseded_by
                v.updated_at = datetime.now()
                self._save()
                return
        raise ValueError(f"Version {version} not found for entity {entity_id}")