# scripts/generators/manifest/schema.py
class ManifestSchema:
    """Manifest schema management"""
    
    SCHEMA_VERSION = 3
    COMPATIBLE_SCHEMA_VERSIONS = [1, 2, 3]
    
    @classmethod
    def get_schema(cls, version: int) -> Dict[str, Any]:
        """Get schema definition for a version"""
        schemas = {
            1: {
                'required': ['version', 'timestamp', 'inventory'],
                'optional': ['checksum']
            },
            2: {
                'required': ['version', 'timestamp', 'inventory', 'checksum'],
                'optional': ['metadata', 'provenance']
            },
            3: {
                'required': ['version', 'schema_version', 'timestamp', 'inventory', 'checksum'],
                'optional': ['provenance', 'metadata', 'artifacts']
            }
        }
        return schemas.get(version, schemas[3])
    
    @classmethod
    def validate(cls, manifest: Dict[str, Any]) -> List[str]:
        """Validate manifest against schema"""
        errors = []
        schema_version = manifest.get('schema_version', 1)
        
        if schema_version not in cls.COMPATIBLE_SCHEMA_VERSIONS:
            errors.append(f"Unsupported schema version: {schema_version}")
        
        schema = cls.get_schema(schema_version)
        for field in schema['required']:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")
        
        return errors

# Manifest Generator with Schema
class ManifestGenerator:
    def generate(self):
        manifest = {
            'version': VersionManager.MANIFEST_VERSION,
            'schema_version': ManifestSchema.SCHEMA_VERSION,
            'timestamp': datetime.now().isoformat(),
            'build': {
                'id': str(uuid.uuid4()),
                'duration': self._get_duration(),
            },
            'provenance': self._get_provenance(),
            'inventory': self._get_inventory_summary(),
            'validation': self._get_validation_summary(),
            'artifacts': self._get_artifact_checksums(),
            'checksum': self._calculate_checksum()
        }
        
        # Validate
        errors = ManifestSchema.validate(manifest)
        if errors:
            raise ValueError(f"Manifest validation failed: {errors}")
        
        return manifest