"""
Schema Migration - Migrate Data Between Schema Versions
"""

from typing import Dict, Any, List, Optional
from schema.registry import SchemaRegistry, SchemaVersion


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
